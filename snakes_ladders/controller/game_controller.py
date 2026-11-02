"""Use cases connecting screens to the Pygame-free engine."""

import logging

from snakes_ladders.controller.input_validator import validate_setup
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.persistence import (
    SaveError,
    SaveManager,
    SaveNotFoundError,
    SaveTooLargeError,
    SaveWriteError,
)

logger = logging.getLogger("snakes_ladders.controller")


class GameController:
    def __init__(self, engine=None, save_manager=None):
        self.engine = engine if engine is not None else GameEngine()
        self.save_manager = save_manager if save_manager is not None else SaveManager()
        self.state = None
        self.screen = "setup"
        self.running = True
        self.last_result = None
        self.error_message = None
        self.status_message = None
        self.pending_prompt = None

    def start_new_game(self, configs, extra_turn=False):
        configs = validate_setup(configs)
        state = self.engine.new_game(configs, extra_turn)
        self.state = state
        self.last_result = None
        self.error_message = None
        self.status_message = None
        self.pending_prompt = None
        self.screen = "game"

    def on_roll_requested(self):
        if not self._is_awaiting_roll():
            logger.debug("Roll requested while not awaiting roll (ignored)")
            return None
        self.status_message = None
        self.last_result = self.engine.roll_and_move(self.state)
        if self.last_result.winner_index is not None:
            self.screen = "result"
        else:
            self.state.phase = Phase.ANIMATING
        return self.last_result

    def on_animation_done(self):
        """The UI calls this when the token has finished moving (SDD 3.1)."""
        if self.state is not None and self.state.phase is Phase.ANIMATING:
            self.state.phase = Phase.AWAITING_ROLL

    def on_save_requested(self):
        """Saving is only allowed between rolls (FR-15, FR-17, NFR-11)."""
        if not self._is_awaiting_roll():
            logger.debug("Save requested while not awaiting roll (ignored)")
            return False
        return self._save_game()

    def _save_game(self):
        try:
            self.save_manager.save(self.state)
            self.status_message = "Game saved."
            self.error_message = None
            return True
        except SaveTooLargeError as error:
            logger.warning("SaveTooLargeError: %s", error)
            self.error_message = str(error)
            self.status_message = None
            return False
        except SaveWriteError as error:
            logger.error("SaveWriteError: %s", error)
            self.error_message = "Could not save the game."
            return False

    def on_resume_requested(self):
        """Resume the most recent saved game (FR-15, UC10, SDD 3.6.1)."""
        try:
            saved_state = self.save_manager.load()
            self.state = self.engine.from_saved(saved_state)
            self.last_result = None
            self.error_message = None
            self.status_message = None
            self.screen = "game"
            return True
        except SaveNotFoundError as error:
            logger.info("SaveNotFoundError: %s", error)
            self.error_message = "No saved game found."
            return False
        except SaveError as error:
            logger.warning("%s: %s", type(error).__name__, error)
            self.error_message = "Save file is corrupted or has been modified."
            return False

    def can_resume(self):
        """Check whether a save file exists for UI display (UI-4)."""
        return self.save_manager.exists()

    def _is_awaiting_roll(self):
        return (
            self.pending_prompt is None
            and self.screen == "game"
            and self.state is not None
            and self.state.phase is Phase.AWAITING_ROLL
        )

    def new_game_requested(self):
        """Ask before discarding a running or completed game (FR-14)."""
        if self.screen in ("game", "result") and self.pending_prompt is None:
            self.pending_prompt = "restart"

    def on_restart_confirmed(self):
        if self.pending_prompt == "restart":
            self.state = None
            self.last_result = None
            self.error_message = None
            self.status_message = None
            self.pending_prompt = None
            self.screen = "setup"

    def cancel_prompt(self):
        self.pending_prompt = None

    def exit_requested(self):
        """Window close and Exit buttons share the same save-aware flow (FR-18)."""
        if self.screen == "game" and self.state is not None and self.state.phase is not Phase.GAME_OVER:
            self.pending_prompt = "exit"
        else:
            self.pending_prompt = None
            self.running = False

    def can_save_before_exit(self):
        return (
            self.screen == "game"
            and self.state is not None
            and self.state.phase is Phase.AWAITING_ROLL
        )

    def save_and_exit(self):
        if self.pending_prompt != "exit" or not self.can_save_before_exit():
            return False
        if not self._save_game():
            return False  # Keep the prompt and session usable when saving fails.
        self.pending_prompt = None
        self.running = False
        return True

    def exit_without_saving(self):
        if self.pending_prompt == "exit":
            self.pending_prompt = None
            self.running = False
