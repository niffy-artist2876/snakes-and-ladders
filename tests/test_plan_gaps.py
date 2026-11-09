"""Test Plan cases that had no automated test.

Found when the Test Plan was mapped to the suite. Each test names its case ID.
"""

import hashlib
import inspect
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import DiceService, GameEngine, Phase
from snakes_ladders.engine.setup import InputValidationError, PlayerConfig, validate_name
from snakes_ladders.persistence import ChecksumService, SaveManager
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.result_screen import ResultScreen
from tests.engine.test_scripted_rng import ScriptedRng

ROOT = Path(__file__).resolve().parent.parent
PLAYERS = [PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")]
SPACE = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
CORRUPT = "Save file is corrupted or has been modified."


def controller_for(save_dir, rolls=()):
    return GameController(GameEngine(rng=ScriptedRng(list(rolls))), SaveManager(save_dir))


def payload(last_roll=4, name="Sam", position=10):
    state = {
        "players": [
            {"name": name, "colour": "blue", "position": position},
            {"name": "Alice", "colour": "orange", "position": 20},
        ],
        "current_index": 0,
        "extra_turn_enabled": False,
        "extra_rolls_used": 0,
        "last_roll": last_roll,
    }
    return {"version": 1, "state": state, "checksum": ChecksumService.compute(state)}


def write_save(save_dir, content):
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / "savegame.json"
    path.write_bytes(content if isinstance(content, bytes) else json.dumps(content).encode("utf-8"))
    return path


@pytest.fixture
def screen_ready():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    yield
    pygame.quit()


# ---------------------------------------------------------------- SEC-01


@pytest.mark.parametrize("name", ["<b>x</b>", "x;y", "../a", "\U0001F600"])
def test_more_hostile_names_are_rejected_and_never_stored(name):
    # TC-SEC01-2: the names the other tests do not cover.
    with pytest.raises(InputValidationError):
        validate_name(name)
    controller = GameController()
    with pytest.raises(InputValidationError):
        controller.start_new_game([PlayerConfig(name, "blue"), PlayerConfig("Alice", "orange")])
    assert controller.state is None


def test_name_validation_agrees_with_an_independent_oracle_on_random_strings():
    # TC-SEC01-4: 10,000 random strings; accepted if and only if the pattern matches after stripping.
    rng = random.Random(2026)
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
    pattern = re.compile(r"[A-Za-z0-9 ]{1,15}")
    accepted = rejected = 0
    for _ in range(10_000):
        length = rng.randint(0, 100)
        if rng.random() < 0.5:  # Mostly valid-looking strings, so both outcomes are well exercised.
            text = "".join(rng.choice(allowed) for _ in range(rng.randint(0, 20)))
        else:  # Anything in the Unicode range except surrogates.
            text = "".join(chr(rng.choice([rng.randrange(0xD800), rng.randrange(0xE000, 0x110000)]))
                           for _ in range(length))
        expected = pattern.fullmatch(text.strip(" ")) is not None
        try:
            assert validate_name(text) == text.strip(" ")
            outcome = True
        except InputValidationError:
            outcome = False
        assert outcome == expected, repr(text)
        accepted += outcome
        rejected += not outcome
    assert accepted > 100 and rejected > 100


def test_saved_name_with_a_disallowed_character_is_rejected_on_load(tmp_path):
    # TC-SEC01-5: a valid checksum does not excuse a bad name (the empty and 16-character names
    # are covered in test_save_security).
    write_save(tmp_path, payload(name="Bob!"))
    controller = controller_for(tmp_path)
    assert controller.on_resume_requested() is False
    assert controller.error_message == CORRUPT


# ---------------------------------------------------------------- SEC-03


def oversize():
    return b"x" * 10_300


def bad_json():
    return b"not json"


def out_of_range():
    return payload(position=101)


def wrong_checksum():
    data = payload()
    data["state"]["players"][0]["position"] = 50
    return data


@pytest.mark.parametrize("make_content", [oversize, bad_json, out_of_range, wrong_checksum])
def test_rejected_save_leaves_the_file_and_the_session_untouched(tmp_path, make_content):
    # TC-SEC03-6
    path = write_save(tmp_path, make_content())
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    controller = controller_for(tmp_path)
    assert controller.on_resume_requested() is False
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    assert not (tmp_path / "savegame.json.tmp").exists()
    assert controller.screen == "setup" and controller.state is None
    controller.start_new_game(PLAYERS)  # New Game still works.
    assert controller.screen == "game"


def test_valid_resume_still_works_after_a_rejected_one(tmp_path):
    # TC-SEC03-6
    write_save(tmp_path, bad_json())
    assert controller_for(tmp_path).on_resume_requested() is False
    write_save(tmp_path, payload())
    assert controller_for(tmp_path).on_resume_requested() is True


def test_save_path_that_is_a_directory_does_not_crash(tmp_path):
    # TC-SEC03-8
    (tmp_path / "savegame.json").mkdir()
    controller = controller_for(tmp_path)
    assert controller.on_resume_requested() is False
    assert controller.state is None and controller.screen == "setup"
    assert controller.error_message


@pytest.mark.skipif(sys.platform == "win32", reason="/dev/zero exists only on Linux and macOS")
def test_save_path_that_is_dev_zero_returns_quickly(tmp_path):
    # TC-SEC03-8: the read is limited to 10 KB plus one byte, so an endless file cannot hang the app.
    os.symlink("/dev/zero", tmp_path / "savegame.json")
    controller = controller_for(tmp_path)
    started = time.perf_counter()
    assert controller.on_resume_requested() is False
    assert time.perf_counter() - started < 1.0
    assert controller.state is None


# ---------------------------------------------------------------- SEC-04


def test_dice_value_and_seed_cannot_be_set_from_outside():
    # TC-SEC04-1
    assert list(inspect.signature(GameEngine.roll_and_move).parameters) == ["self", "state"]
    for instance in (DiceService(), GameEngine()):
        public = {name for name in dir(instance) if not name.startswith("_")}
        assert not {name for name in public if re.search(r"seed|rng|dice|^set", name)} - {"SIDES"}


def test_last_roll_in_a_save_never_feeds_the_next_roll(tmp_path):
    # TC-SEC04-3: a save with last_roll 6 and a scripted RNG returning 2 rolls a 2.
    write_save(tmp_path, payload(last_roll=6))
    controller = controller_for(tmp_path, [2])
    assert controller.on_resume_requested()
    assert controller.on_roll_requested().roll == 2


DICE_SCRIPT = "import sys; from snakes_ladders.engine import DiceService; d = DiceService(); print([d.roll() for _ in range(20)])"


def twenty_rolls(tmp_path, extra_args=(), extra_env=None):
    env = {**os.environ, "PYTHONPATH": str(ROOT), **(extra_env or {})}
    result = subprocess.run([sys.executable, "-c", DICE_SCRIPT, *extra_args],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_seeding_attempts_do_not_make_the_dice_repeatable(tmp_path):
    # TC-SEC04-4: a --seed argument, SNL_SEED and PYTHONHASHSEED, and a stray seed.cfg.
    (tmp_path / "seed.cfg").write_text("seed = 1\n")
    attempts = [
        {"extra_args": ("--seed", "1")},
        {"extra_env": {"SNL_SEED": "1", "PYTHONHASHSEED": "0"}},
        {},
    ]
    for attempt in attempts:
        # Two launches never give the same 20 values (a chance of 6 to the power -20).
        assert twenty_rolls(tmp_path, **attempt) != twenty_rolls(tmp_path, **attempt)


# ---------------------------------------------------------------- SEC-06


def test_full_session_never_touches_the_network(tmp_path, monkeypatch):
    # TC-SEC06-2: setup, play, save, resume, play to a win, restart, exit with every socket call trapped.
    def trap(*args, **kwargs):
        raise AssertionError("the application tried to use the network")

    for name in ("socket", "create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, trap)

    controller = controller_for(tmp_path, [3, 1])
    controller.start_new_game(PLAYERS)
    controller.on_roll_requested()
    controller.on_animation_done()
    assert controller.on_save_requested()
    assert controller.on_resume_requested()
    controller.state.players[controller.state.current_index].position = 99
    assert controller.on_roll_requested().winner_index is not None
    controller.new_game_requested()
    controller.on_restart_confirmed()
    assert controller.screen == "setup"
    controller.exit_requested()
    assert controller.running is False


# ---------------------------------------------------------------- FR-17


@pytest.mark.real_animation
def test_ten_quick_space_presses_roll_only_once(screen_ready, tmp_path):
    # TC-FR17-1
    rng = ScriptedRng([3] * 11)
    controller = GameController(GameEngine(rng=rng), SaveManager(tmp_path))
    controller.start_new_game(PLAYERS)
    screen = GameScreen(controller)
    for _ in range(10):
        screen.handle_event(SPACE)
    assert rng.remaining == 10  # Exactly one value was drawn.
    assert controller.state.phase is Phase.ANIMATING


def test_roll_after_a_win_is_ignored_on_the_game_and_result_screens(screen_ready, tmp_path):
    # TC-FR17-2
    controller = controller_for(tmp_path, [1, 5])
    controller.start_new_game(PLAYERS)
    controller.state.players[0].position = 99
    assert controller.on_roll_requested().winner_index == 0
    before = deepcopy(controller.state)
    assert controller.on_roll_requested() is None
    ResultScreen(controller).handle_event(SPACE)
    assert controller.state == before


@pytest.mark.real_animation
def test_save_is_ignored_while_a_token_moves_and_the_file_is_unchanged(screen_ready, tmp_path):
    # TC-FR17-3
    controller = controller_for(tmp_path, [3, 3])
    controller.start_new_game(PLAYERS)
    assert controller.on_save_requested()
    path = tmp_path / "savegame.json"
    fingerprint = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
    screen = GameScreen(controller)
    screen.handle_event(SPACE)
    assert controller.state.phase is Phase.ANIMATING
    assert controller.on_save_requested() is False
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.save_button.center))
    assert (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns) == fingerprint


@pytest.mark.real_animation
def test_ignored_actions_log_at_debug_level_and_show_nothing(screen_ready, tmp_path, caplog):
    # TC-FR17-5
    controller = controller_for(tmp_path, [3, 3])
    controller.start_new_game(PLAYERS)
    GameScreen(controller).handle_event(SPACE)
    caplog.set_level("DEBUG", logger="snakes_ladders.controller")
    caplog.clear()
    assert controller.on_roll_requested() is None
    assert controller.on_save_requested() is False
    records = [r for r in caplog.records if r.name == "snakes_ladders.controller"]
    assert records and all(r.levelname == "DEBUG" for r in records)
    assert controller.error_message is None


# ------------------------------------------------------------- UI-4, C3


def test_forced_resume_without_a_file_shows_the_not_found_message(tmp_path):
    # TC-UI4-1
    controller = controller_for(tmp_path)
    assert controller.can_resume() is False
    assert controller.on_resume_requested() is False
    assert controller.error_message == "No saved game found."


def test_save_file_is_plain_utf8_json_with_the_documented_fields(tmp_path):
    # TC-C3-1: read with the standard json module, as an independent tool would.
    controller = controller_for(tmp_path)
    controller.start_new_game(PLAYERS)
    assert controller.on_save_requested()
    data = json.loads((tmp_path / "savegame.json").read_text(encoding="utf-8"))
    assert set(data) == {"version", "state", "checksum"}
    assert data["version"] == 1
    assert set(data["state"]) == {"players", "current_index", "extra_turn_enabled", "extra_rolls_used", "last_roll"}
    assert all(set(player) == {"name", "colour", "position"} for player in data["state"]["players"])
    assert re.fullmatch(r"[0-9a-f]{64}", data["checksum"])


# --------------------------------------------------------------- NFR-06


def test_engine_tests_pass_when_pygame_is_unavailable():
    # TC-N06-2: block the pygame module, then run the engine tests in a fresh process.
    code = ("import sys; sys.modules['pygame'] = None; import pytest; "
            "raise SystemExit(pytest.main(['tests/engine', '-q', '-p', 'no:cacheprovider']))")
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout[-800:] + result.stderr[-400:]
