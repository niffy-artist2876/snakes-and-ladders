"""Board layout, complete artwork, and visible tokens in headless SDL."""

import os
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine
from snakes_ladders.engine.board import LADDERS, SNAKES
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui import board_view
from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.result_screen import ResultScreen
from snakes_ladders.ui.widgets import BACKGROUND, TOKEN_COLOURS
from tests.engine.test_factories import make_state
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.fixture
def surface():
    pygame.init()
    yield pygame.display.set_mode((1280, 720))
    pygame.quit()


def has_colour(surface, rect, colour):
    return any(surface.get_at((x, y))[:3] == colour
               for x in range(rect.left, rect.right)
               for y in range(rect.top, rect.bottom))


def test_all_numbers_follow_boustrophedon_order(surface, monkeypatch):
    labels = {}
    original = board_view.label

    def record(target, text, position, *args):
        labels[int(text)] = position
        original(target, text, position, *args)

    monkeypatch.setattr(board_view, "label", record)
    view = BoardView()
    assert set(labels) == set(range(1, 101))
    # Each row reverses, with 1 at bottom left and 100 at top left.
    for row in range(10):
        expected = list(range(row * 10 + 1, row * 10 + 11))
        if row % 2:
            expected.reverse()
        actual = sorted(expected, key=lambda number: labels[number][0])
        assert actual == expected
        assert {labels[number][1] for number in expected} == {543 - row * 60}
    assert view.square_rect(1).bottomleft == (40, 660)
    assert view.square_rect(10).bottomright == (640, 660)
    assert view.square_rect(100).topleft == (40, 60)
    assert len({tuple(view.square_rect(n)) for n in range(1, 101)}) == 100


def test_every_snake_and_ladder_has_visible_endpoints(surface):
    view = BoardView()
    view.draw(surface, [])
    for links, colour in ((SNAKES, view.SNAKE_COLOUR), (LADDERS, view.LADDER_COLOUR)):
        for start, end in links.items():
            for square in (start, end):
                rect = view.square_rect(square)
                # Endpoints occupy the right half, away from numbers and tokens.
                assert has_colour(surface, pygame.Rect(rect.x + 30, rect.y + 2, 29, 26), colour)


def test_four_tokens_remain_distinct_on_every_square_and_at_start(surface):
    view = BoardView()
    for square in range(101):
        players = make_state(square, square, square, square).players
        surface.fill(BACKGROUND)
        view.draw(surface, players)
        slots = []
        for index, player in enumerate(players):
            center = view.token_center(square, index)
            bounds = pygame.Rect(center[0] - 7, center[1] - 7, 14, 14)
            assert surface.get_rect().contains(bounds)
            if square:
                assert view.square_rect(square).contains(bounds)
            assert has_colour(surface, bounds, TOKEN_COLOURS[player.colour])
            assert all(not bounds.colliderect(other) for other in slots)
            slots.append(bounds)


def test_roll_updates_the_board_and_results_keep_final_tokens_visible(surface):
    controller = GameController(GameEngine(rng=ScriptedRng([1, 1, 1])))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    game = GameScreen(controller)
    game.draw(surface)
    start = game.board_view.token_center(0, 0)
    game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=game.roll_button.center))
    assert controller.state.players[0].position == 38
    game.update(1)
    game.draw(surface)
    assert surface.get_at(start)[:3] == BACKGROUND
    center = game.board_view.token_center(38, 0)
    assert has_colour(surface, pygame.Rect(center[0] - 7, center[1] - 7, 14, 14), TOKEN_COLOURS["blue"])
    controller.on_roll_requested()  # Alice's turn.
    controller.on_animation_done()
    controller.state.players[0].position = 99
    controller.on_roll_requested()
    assert controller.screen == "result"
    result = ResultScreen(controller)
    result.draw(surface)
    center = result.board_view.token_center(100, 0)
    assert has_colour(surface, pygame.Rect(center[0] - 7, center[1] - 7, 14, 14), TOKEN_COLOURS["blue"])
    assert not result.new_game_button.colliderect(result.board_view.RECT)
    assert not result.exit_button.colliderect(result.board_view.RECT)


def test_token_position_render_updates_within_one_second_of_roll_display(surface):
    controller = GameController(GameEngine(rng=ScriptedRng([1, 4])))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    game = GameScreen(controller)

    # Ladder path: roll 1 from start lands on 1 and resolves to 38.
    start = time.perf_counter()
    game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=game.roll_button.center))
    game.update(1)
    game.draw(surface)
    elapsed = time.perf_counter() - start
    assert elapsed <= 1.0
    assert controller.state.players[0].position == 38
    center = game.board_view.token_center(38, 0)
    assert has_colour(surface, pygame.Rect(center[0] - 7, center[1] - 7, 14, 14), TOKEN_COLOURS["blue"])

    # Snake path: set a snake head then roll onto it (95 -> 75).
    controller.state.current_index = 0
    controller.state.players[0].position = 91
    start = time.perf_counter()
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.update(1)
    game.draw(surface)
    elapsed = time.perf_counter() - start
    assert elapsed <= 1.0
    assert controller.state.players[0].position == 75
    center = game.board_view.token_center(75, 0)
    assert has_colour(surface, pygame.Rect(center[0] - 7, center[1] - 7, 14, 14), TOKEN_COLOURS["blue"])
