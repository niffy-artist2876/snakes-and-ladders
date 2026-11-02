"""FR-18: every exit route offers save/discard/cancel for a running game."""

import os
from copy import deepcopy

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.setup_screen import SetupScreen
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.fixture
def controller(tmp_path):
    controller = GameController(GameEngine(rng=ScriptedRng([3, 4])), SaveManager(tmp_path))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    return controller


@pytest.fixture
def surface():
    pygame.init()
    yield pygame.display.set_mode((1280, 720))
    pygame.quit()


def click(rect):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)


def test_save_and_exit_writes_loadable_current_state(controller, surface):
    controller.state.players[0].position = 12
    controller.state.current_index = 1
    screen = GameScreen(controller)
    screen.handle_event(click(screen.exit_button))
    assert controller.running and controller.pending_prompt == "exit"
    screen.draw(surface)
    screen.handle_event(click(screen.dialog.save_button))
    assert not controller.running
    resumed = GameController(save_manager=controller.save_manager)
    assert resumed.on_resume_requested()
    assert resumed.state == controller.state


def test_exit_without_saving_preserves_existing_save(controller, surface):
    assert controller.on_save_requested()
    saved = controller.save_manager.save_path.read_bytes()
    controller.state.players[0].position = 12
    screen = GameScreen(controller)
    screen.handle_event(click(screen.exit_button))
    screen.handle_event(click(screen.dialog.discard_button))
    assert not controller.running
    assert controller.save_manager.save_path.read_bytes() == saved


@pytest.mark.parametrize("use_escape", [False, True])
def test_cancel_preserves_session_and_rolling_still_works(controller, surface, use_escape):
    screen = GameScreen(controller)
    before = deepcopy(controller.state)
    screen.handle_event(click(screen.exit_button))
    screen.handle_event(click(screen.roll_button))
    assert controller.state == before
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE) if use_escape else click(screen.dialog.cancel_button)
    screen.handle_event(event)
    assert controller.pending_prompt is None and controller.running
    assert controller.state == before
    screen.handle_event(click(screen.roll_button))
    assert controller.state.last_roll == 3


def test_save_failure_keeps_game_open_and_can_retry(controller, surface, monkeypatch):
    assert controller.on_save_requested()
    original = controller.save_manager.save_path.read_bytes()
    controller.state.players[0].position = 12
    screen = GameScreen(controller)
    screen.handle_event(click(screen.exit_button))
    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disk full")))
        screen.handle_event(click(screen.dialog.save_button))
    assert controller.running and controller.pending_prompt == "exit"
    assert controller.error_message == "Could not save the game."
    assert controller.save_manager.save_path.read_bytes() == original
    screen.draw(surface)
    screen.handle_event(click(screen.dialog.save_button))
    assert not controller.running
    assert controller.save_manager.load()["players"][0]["position"] == 12


@pytest.mark.real_animation
def test_exit_during_move_disables_save_until_animation_finishes(controller, surface):
    screen = GameScreen(controller)
    screen.handle_event(click(screen.roll_button))
    assert controller.state.phase is Phase.ANIMATING
    screen.handle_event(click(screen.exit_button))
    screen.handle_event(click(screen.dialog.save_button))
    assert controller.running
    assert not controller.save_manager.exists()
    screen.draw(surface)
    screen.update(1)
    assert controller.state.phase is Phase.AWAITING_ROLL
    screen.handle_event(click(screen.dialog.save_button))
    assert not controller.running and controller.save_manager.exists()


@pytest.mark.parametrize("screen_name", ["setup", "result"])
def test_exit_without_active_game_needs_no_prompt(controller, screen_name):
    controller.screen = screen_name
    controller.exit_requested()
    assert not controller.running and controller.pending_prompt is None


def test_setup_exit_button_closes_application(controller, surface):
    controller.screen = "setup"
    controller.state = None
    screen = SetupScreen(controller=controller)
    screen.draw(surface)
    screen.handle_event(click(screen.exit_button))
    assert not controller.running


def test_save_and_discard_cannot_close_without_an_exit_request(controller):
    assert not controller.save_and_exit()
    controller.exit_without_saving()
    assert controller.running and not controller.save_manager.exists()


def test_window_close_uses_prompt_and_cancel_then_discard(controller, monkeypatch):
    monkeypatch.setattr(app, "GameController", lambda: controller)
    frame = 0

    def events():
        nonlocal frame
        frame += 1
        assert frame <= 3, "Exit flow did not terminate"
        dialog = GameScreen(controller).dialog
        if frame == 1:
            return [pygame.event.Event(pygame.QUIT)]
        if frame == 2:
            assert controller.running and controller.pending_prompt == "exit"
            return [click(dialog.cancel_button)]
        assert controller.pending_prompt is None and controller.running
        return [pygame.event.Event(pygame.QUIT), click(dialog.discard_button)]

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert not controller.running and frame == 3
