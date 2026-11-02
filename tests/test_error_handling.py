"""NFR-10: fault injection leaves a usable screen and no unhandled exception."""

import builtins
import os
from copy import deepcopy
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.persistence.exceptions import EngineInvariantError
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.setup_screen import SetupScreen


@pytest.fixture
def controller(tmp_path):
    return GameController(GameEngine(), SaveManager(tmp_path))


def start(controller):
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])


@pytest.mark.parametrize("content", [None, b"", b" ", b"not json", b"\xff\xfe", b"[]", b"null", b"[" * 9000])
def test_missing_empty_corrupt_saves_preserve_live_state(controller, content):
    start(controller)
    before = deepcopy(controller.state)
    if content is not None:
        controller.save_manager.save_path.write_bytes(content)
    assert controller.on_resume_requested() is False
    assert controller.state == before
    assert controller.screen == "game" and controller.error_message
    assert controller.on_roll_requested() is not None


def test_save_read_permission_failure_is_reported(controller, monkeypatch):
    start(controller)
    assert controller.on_save_requested()
    original = builtins.open

    def unreadable(path, *args, **kwargs):
        if Path(path) == controller.save_manager.save_path:
            raise PermissionError("private filesystem detail")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", unreadable)
    assert not controller.on_resume_requested()
    assert controller.error_message == "Save file is corrupted or has been modified."


def test_metadata_permission_failure_does_not_break_setup_or_resume(controller, monkeypatch):
    original = Path.is_file

    def unreadable(path):
        if path == controller.save_manager.save_path:
            raise PermissionError("private metadata detail")
        return original(path)

    monkeypatch.setattr(Path, "is_file", unreadable)
    assert not controller.can_resume()
    assert not controller.on_resume_requested()
    assert controller.screen == "setup" and controller.state is None
    assert controller.error_message == "Save file is corrupted or has been modified."


@pytest.mark.parametrize("failure", [PermissionError, OSError])
def test_write_fault_clears_stale_success_and_keeps_previous_save(controller, monkeypatch, failure):
    start(controller)
    assert controller.on_save_requested()
    before = controller.save_manager.save_path.read_bytes()

    def fail_replace(*args):
        raise failure("read-only directory or disk full")

    monkeypatch.setattr(os, "replace", fail_replace)
    assert not controller.on_save_requested()
    assert controller.status_message is None
    assert controller.error_message == "Could not save the game."
    assert controller.save_manager.save_path.read_bytes() == before
    assert controller.on_roll_requested() is not None


def test_hostile_setup_input_stays_editable_and_cannot_start(controller):
    pygame.init()
    try:
        surface = pygame.display.set_mode((1280, 720))
        screen = SetupScreen(controller.start_new_game, controller=controller)
        for value in ("!", "\x00", "\u540d", "W" * 10000):
            screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text=value))
            for key in (pygame.K_TAB, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
            screen.draw(surface)
            screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.start_button.center))
            assert controller.state is None and screen.validation_error()
        screen.names = ["Sam", "Alice", "", ""]
        screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.start_button.center))
        assert controller.screen == "game"
    finally:
        pygame.quit()


@pytest.mark.parametrize("stage", ["engine", "events", "update", "draw", "flip"])
@pytest.mark.parametrize("failure", [EngineInvariantError, RuntimeError])
def test_real_loop_recovers_logs_traceback_and_can_start_again(controller, monkeypatch, stage, failure):
    start(controller)
    monkeypatch.setattr(app, "GameController", lambda: controller)
    detail = "injected internal failure with private path"

    def fail_once(original):
        failed = False

        def call(*args, **kwargs):
            nonlocal failed
            if not failed:
                failed = True
                controller.state.players[0].position = 55  # A partially completed operation.
                raise failure(detail)
            return original(*args, **kwargs)

        return call

    if stage == "engine":
        monkeypatch.setattr(controller.engine, "roll_and_move", fail_once(controller.engine.roll_and_move))
    elif stage in ("update", "draw"):
        monkeypatch.setattr(GameScreen, stage, fail_once(getattr(GameScreen, stage)))
    elif stage == "flip":
        monkeypatch.setattr(pygame.display, "flip", fail_once(pygame.display.flip))

    frame = 0
    recovered = False

    def events():
        nonlocal frame, recovered
        frame += 1
        assert frame <= 4, "Application did not recover to a usable screen"
        if frame == 1:
            if stage == "events":
                raise failure(detail)
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if stage == "engine" else []
        if frame == 2:
            assert controller.screen == "setup" and controller.state is None
            assert controller.pending_prompt is None
            assert controller.error_message == "An unexpected error occurred. Returning to the start screen."
            recovered = True
            return []  # Actually render the recovered setup screen.
        if frame == 3:
            return [pygame.event.Event(pygame.TEXTINPUT, text="Sam"),
                    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
                    pygame.event.Event(pygame.TEXTINPUT, text="Alice"),
                    pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 645))]
        assert controller.screen == "game" and controller.error_message is None
        assert [player.position for player in controller.state.players] == [0, 0]
        return [pygame.event.Event(pygame.QUIT),
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(600, 435))]

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert recovered and not controller.running
    log = (controller.save_manager.directory / "snl.log").read_text(encoding="utf-8")
    assert "Traceback" in log and detail in log and failure.__name__ in log
