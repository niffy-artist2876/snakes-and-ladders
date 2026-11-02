"""FR-14: restart requires confirmation, preserves saves and resets a session."""

import os
from copy import deepcopy

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.result_screen import ResultScreen
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.fixture
def controller(tmp_path):
    controller = GameController(GameEngine(rng=ScriptedRng([3, 1])), SaveManager(tmp_path))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    return controller


@pytest.fixture
def surface():
    pygame.init()
    yield pygame.display.set_mode((1280, 720))
    pygame.quit()


def click(rect):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)


@pytest.mark.parametrize("screen_name", ["game", "result"])
def test_restart_cancel_preserves_entire_state_and_blocks_background_input(controller, surface, screen_name):
    if screen_name == "result":
        controller.state.players[0].position = 97
        controller.on_roll_requested()
        screen = ResultScreen(controller)
        restart_button = screen.new_game_button
    else:
        screen = GameScreen(controller)
        restart_button = screen.restart_button
    before = deepcopy(controller.state)
    screen.handle_event(click(restart_button))
    screen.draw(surface)
    assert controller.pending_prompt == "restart"
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert controller.on_roll_requested() is None
    assert controller.state == before
    screen.handle_event(click(screen.dialog.cancel_button))
    assert controller.pending_prompt is None
    assert controller.screen == screen_name
    assert controller.state == before


@pytest.mark.parametrize("screen_name", ["game", "result"])
def test_confirm_restart_clears_session_keeps_save_and_starts_fresh(controller, surface, screen_name):
    assert controller.on_save_requested()
    saved = controller.save_manager.save_path.read_bytes()
    if screen_name == "result":
        controller.state.players[0].position = 97
        controller.on_roll_requested()
        screen = ResultScreen(controller)
        restart_button = screen.new_game_button
    else:
        screen = GameScreen(controller)
        restart_button = screen.restart_button
    screen.handle_event(click(restart_button))
    screen.handle_event(click(screen.dialog.confirm_button))
    assert controller.running
    assert controller.screen == "setup"
    assert controller.state is None and controller.last_result is None
    assert controller.pending_prompt is None
    assert controller.save_manager.save_path.read_bytes() == saved
    controller.start_new_game([PlayerConfig("New1", "green"), PlayerConfig("New2", "magenta")])
    assert [p.position for p in controller.state.players] == [0, 0]
    assert controller.state.current_index == 0
    assert controller.state.phase is Phase.AWAITING_ROLL


def test_escape_cancels_and_unrequested_confirmation_does_nothing(controller, surface):
    state = controller.state
    controller.on_restart_confirmed()
    assert controller.state is state
    screen = GameScreen(controller)
    screen.handle_event(click(screen.restart_button))
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert controller.pending_prompt is None
    assert controller.state is state
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert controller.state.last_roll == 3


@pytest.mark.real_animation
def test_restart_during_animation_discards_the_old_animation(controller, surface):
    screen = GameScreen(controller)
    screen.handle_event(click(screen.roll_button))
    assert screen.animating
    screen.handle_event(click(screen.restart_button))
    screen.handle_event(click(screen.dialog.confirm_button))
    assert not screen.animating
    controller.start_new_game([PlayerConfig("New1", "green"), PlayerConfig("New2", "magenta")])
    screen.update(1)
    screen.draw(surface)
    assert [p.position for p in controller.state.players] == [0, 0]
