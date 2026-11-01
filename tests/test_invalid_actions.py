"""FR-17: actions outside the game rules are ignored and disabled."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui.game_screen import GameScreen
from tests.engine.test_scripted_rng import ScriptedRng


def started_controller(*rolls):
    controller = GameController(GameEngine(rng=ScriptedRng(list(rolls))))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    return controller


def test_roll_moves_phase_to_animating_and_blocks_a_second_roll():
    controller = started_controller(3, 4)
    assert controller.on_roll_requested() is not None
    assert controller.state.phase is Phase.ANIMATING
    # A second roll while the token is still moving is ignored: nothing changes.
    assert controller.on_roll_requested() is None
    assert controller.state.last_roll == 3
    assert [p.position for p in controller.state.players] == [3, 0]
    assert controller.state.current_index == 1


def test_animation_done_allows_the_next_roll():
    controller = started_controller(3, 4)
    controller.on_roll_requested()
    controller.on_animation_done()
    assert controller.state.phase is Phase.AWAITING_ROLL
    result = controller.on_roll_requested()
    assert result.player_index == 1


def test_animation_done_is_a_no_op_outside_animating():
    controller = started_controller(3)
    controller.on_animation_done()
    assert controller.state.phase is Phase.AWAITING_ROLL
    controller.state.phase = Phase.GAME_OVER
    controller.on_animation_done()
    assert controller.state.phase is Phase.GAME_OVER
    GameController().on_animation_done()  # no game started: must not raise


def test_winning_roll_ends_the_game_not_animating():
    controller = started_controller(1)
    controller.state.players[0].position = 99
    controller.on_roll_requested()
    assert controller.state.phase is Phase.GAME_OVER
    controller.on_animation_done()
    assert controller.state.phase is Phase.GAME_OVER
    assert controller.on_roll_requested() is None


def test_save_is_only_allowed_between_rolls():
    controller = GameController()
    assert controller.on_save_requested() is False  # no game yet
    controller = started_controller(3)
    assert controller.on_save_requested() is True
    controller.on_roll_requested()
    assert controller.state.phase is Phase.ANIMATING
    assert controller.on_save_requested() is False  # move in progress
    controller.on_animation_done()
    assert controller.on_save_requested() is True
    controller.state.phase = Phase.GAME_OVER
    assert controller.on_save_requested() is False


@pytest.fixture
def game_screen():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    yield
    pygame.quit()


def roll_inputs(screen):
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.roll_button.center)
    space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    return [click, space]


@pytest.mark.parametrize("phase", [Phase.ANIMATING, Phase.GAME_OVER])
def test_roll_button_and_space_are_ignored_when_not_awaiting_roll(game_screen, phase):
    controller = started_controller(3, 3)
    screen = GameScreen(controller)
    controller.state.phase = phase
    for event in roll_inputs(screen):
        screen.handle_event(event)
    assert controller.state.last_roll is None
    assert [p.position for p in controller.state.players] == [0, 0]


def test_ui_roll_completes_the_move_so_the_game_stays_playable(game_screen):
    controller = started_controller(3, 5)
    screen = GameScreen(controller)
    click, space = roll_inputs(screen)
    screen.handle_event(click)
    screen.handle_event(space)
    assert [p.position for p in controller.state.players] == [3, 0]
    screen.update(1)
    screen.handle_event(space)
    screen.update(1)
    assert [p.position for p in controller.state.players] == [3, 5]
    assert controller.state.phase is Phase.AWAITING_ROLL
