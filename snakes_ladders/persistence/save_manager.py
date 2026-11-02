"""Save file persistence management (SDD 3.5, 3.6.3, SEC-02, SEC-03, SEC-05, NFR-11)."""

import json
import logging
import os
from pathlib import Path

from snakes_ladders.engine.models import GameState
from snakes_ladders.persistence.checksum import ChecksumService
from snakes_ladders.persistence.exceptions import (
    SaveError,
    SaveFormatError,
    SaveNotFoundError,
    SaveTooLargeError,
    SaveWriteError,
)
from snakes_ladders.persistence.validator import SaveValidator

MAX_SAVE_SIZE = 10 * 1024  # 10 KB (SEC-03)
SAVE_FILE_NAME = "savegame.json"
TEMP_FILE_NAME = "savegame.json.tmp"
LOG_FILE_NAME = "snl.log"

logger = logging.getLogger("snakes_ladders.persistence")


def _reject_constant(c: str):
    raise ValueError(f"Invalid JSON constant: {c}")


def get_default_save_dir() -> Path:
    """Determine per-user save directory without platform-specific imports (SDD 2.8, NFR-05)."""
    override = os.environ.get("SNL_SAVE_DIR")
    if override:
        return Path(override)
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidate = Path(appdata) / "SnakesLadders"
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            pass
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        candidate = Path(xdg_data) / "SnakesLadders"
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            pass
    home = Path.home()
    mac_support = home / "Library" / "Application Support"
    if mac_support.is_dir():
        candidate = mac_support / "SnakesLadders"
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            pass
    try:
        candidate = home / ".local" / "share" / "SnakesLadders"
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except OSError:
        pass
    return Path.cwd() / ".snakes_ladders"


class SaveManager:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory) if directory is not None else get_default_save_dir()
        self.save_path = self.directory / SAVE_FILE_NAME
        self.temp_path = self.directory / TEMP_FILE_NAME
        self._setup_file_logger()

    def _setup_file_logger(self) -> None:
        """Ensure logging writes to snl.log in the save directory (SDD 2.8)."""
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            log_path = self.directory / LOG_FILE_NAME
            root_logger = logging.getLogger("snakes_ladders")
            # Avoid adding multiple handlers for the same path
            has_handler = any(
                isinstance(h, logging.FileHandler) and Path(h.baseFilename) == log_path
                for h in root_logger.handlers
            )
            if not has_handler:
                handler = logging.FileHandler(log_path, encoding="utf-8")
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
                handler.setFormatter(formatter)
                root_logger.addHandler(handler)
        except OSError:
            pass

    def exists(self) -> bool:
        """Check if a save file exists (SDD 3.6.3, UI-4)."""
        try:
            return self.save_path.is_file()
        except OSError:
            return False  # Unreadable metadata must not break setup rendering.

    def save(self, state: GameState) -> None:
        """Serialise, checksum and atomically write game state (SDD 3.3 SD-3, NFR-11).

        The temporary file shares the destination directory. Flush and fsync it
        before os.replace, the commit point: an interruption before that point
        leaves the previous save intact. A later save overwrites any stale temp
        file, and load() only ever reads the committed save.
        """
        state_dict = {
            "players": [
                {"name": p.name, "colour": p.colour, "position": p.position}
                for p in state.players
            ],
            "current_index": state.current_index,
            "extra_turn_enabled": state.extra_turn_enabled,
            "extra_rolls_used": state.extra_rolls_used,
            "last_roll": state.last_roll,
        }
        checksum = ChecksumService.compute(state_dict)
        payload = {
            "version": 1,
            "state": state_dict,
            "checksum": checksum,
        }

        text_data = json.dumps(payload, indent=2)
        content_bytes = text_data.encode("utf-8")
        if len(content_bytes) > MAX_SAVE_SIZE:
            logger.warning("SaveTooLargeError: payload exceeds %d bytes", MAX_SAVE_SIZE)
            raise SaveTooLargeError("Save file exceeds the 10 KB limit.")

        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            with open(self.temp_path, "wb") as f:
                f.write(content_bytes)
                f.flush()
                os.fsync(f.fileno())
            os.replace(self.temp_path, self.save_path)
            logger.info("Game saved successfully to %s", self.save_path)
        except OSError as exc:
            try:
                if self.temp_path.exists():
                    self.temp_path.unlink()
            except OSError:
                pass
            logger.error("SaveWriteError: failed to save game: %s", exc)
            raise SaveWriteError("Could not save the game.") from exc

    def load(self) -> dict:
        """Validate size, parse JSON, validate schema/ranges/checksum, return state dict.
        
        Does not alter any live game state (SDD 3.3 SD-2, SEC-02, SEC-03, SEC-05).
        """
        try:
            if not self.save_path.is_file():
                logger.info("SaveNotFoundError: save file not found at %s", self.save_path)
                raise SaveNotFoundError("No saved game found.")
            with open(self.save_path, "rb") as f:
                content_bytes = f.read(MAX_SAVE_SIZE + 1)
        except OSError as exc:
            logger.warning("SaveFormatError: failed to read file: %s", exc)
            raise SaveFormatError("Save file is corrupted or has been modified.") from exc

        if len(content_bytes) > MAX_SAVE_SIZE:
            logger.warning("SaveTooLargeError: file exceeds %d bytes", MAX_SAVE_SIZE)
            raise SaveTooLargeError("Save file is corrupted or has been modified.")

        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            logger.warning("SaveFormatError: UTF-8 decode failed: %s", exc)
            raise SaveFormatError("Save file is corrupted or has been modified.") from exc

        try:
            # Data-only JSON parser; no eval, exec or pickle (SEC-05)
            data = json.loads(text, parse_constant=_reject_constant)
        except (json.JSONDecodeError, ValueError, RecursionError) as exc:
            logger.warning("SaveFormatError: JSON decode failed: %s", exc)
            raise SaveFormatError("Save file is corrupted or has been modified.") from exc

        try:
            state_dict = SaveValidator.validate(data)
            logger.info("Save file validated successfully from %s", self.save_path)
            return state_dict
        except SaveError as exc:
            logger.warning("%s: %s", type(exc).__name__, exc)
            raise
