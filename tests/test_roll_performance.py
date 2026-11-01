"""NFR-01/NFR-07: measure input through the actual application's display flip."""

import os
from time import perf_counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.widgets import BACKGROUND, TEXT, TOKEN_COLOURS, _render_label
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.mark.parametrize("player_count", [2, 4], ids=["two-players", "four-players"])
def test_fifty_rolls_are_presented_within_one_second(monkeypatch, player_count):
    controller = GameController(GameEngine(rng=ScriptedRng([1] * 50)))
    configs = [PlayerConfig(name, colour) for name, colour in (
        ("Sam", "blue"), ("Alice", "orange"), ("Dara", "green"), ("Alex", "magenta"),
    )][:player_count]
    controller.start_new_game(configs)
    monkeypatch.setattr(app, "GameController", lambda: controller)
    pygame.init()
    board = BoardView()
    _render_label.cache_clear()  # Include the first uncached gameplay frame.
    durations = []
    started = None
    previous_result = None
    flip = pygame.display.flip

    def events():
        nonlocal started
        if len(durations) == 50:
            started = None
            return [pygame.event.Event(pygame.QUIT)]
        if started is not None:
            return []
        started = perf_counter()
        if len(durations) % 2:
            return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(810, 585))]
        return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]

    def present():
        nonlocal previous_result, started
        flip()
        elapsed = perf_counter() - started if started is not None else None
        if elapsed is None:
            return
        assert elapsed <= 1, "Animation exceeded the roll-to-display deadline"
        if controller.state.phase is Phase.ANIMATING:
            return
        assert controller.screen == "game"
        result = controller.last_result
        assert result is not previous_result  # A stale displayed roll must not pass.
        previous_result = result
        assert result.player_index == len(durations) % player_count
        assert controller.state.current_index == (len(durations) + 1) % player_count
        assert result.roll == controller.state.last_roll == 1
        player = controller.state.players[result.player_index]
        assert player.position == result.final_pos
        surface = pygame.display.get_surface()
        for index, visible_player in enumerate(controller.state.players):
            x, y = board.token_center(visible_player.position, index)
            assert surface.get_at((x - 6, y))[:3] == TOKEN_COLOURS[visible_player.colour]
        # The displayed dice result must also have reached the frame being flipped.
        text = _render_label("Last roll: 1", 26, TEXT)
        expected = pygame.Surface(text.get_size())
        expected.fill(BACKGROUND)
        expected.blit(text, (0, 0))
        actual = surface.subsurface((950, 575, *expected.get_size()))
        assert pygame.image.tobytes(actual, "RGB") == pygame.image.tobytes(expected, "RGB")
        durations.append(elapsed)
        started = None

    monkeypatch.setattr(pygame.event, "get", events)
    monkeypatch.setattr(pygame.display, "flip", present)
    app.main()
    assert len(durations) == 50
    print(f"{player_count} players, 50 roll-to-display samples: "
          f"max={max(durations):.6f}s mean={sum(durations)/50:.6f}s")
    assert all(duration <= 1 for duration in durations), durations
