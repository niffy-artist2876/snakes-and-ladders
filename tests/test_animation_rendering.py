"""Optimized movement must match a full redraw and preserve other tokens."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from snakes_ladders.engine import Phase
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.viewport import present
from snakes_ladders.ui.widgets import BACKGROUND
from tests.test_animation import controller_for


def test_cached_animation_matches_full_redraw_and_invalidates_changes(monkeypatch):
    pygame.init()
    try:
        window = pygame.display.set_mode((1280, 720))
        canvas = pygame.Surface((1280, 720))
        reference = canvas.copy()
        controller = controller_for([4], count=4)
        controller.state.players[0].position = 8
        game = GameScreen(controller)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        original = game._draw_scene
        rebuilds = []

        def tracked(*args, **kwargs):
            rebuilds.append(True)
            return original(*args, **kwargs)

        monkeypatch.setattr(game, "_draw_scene", tracked)
        for frame in range(12):
            if frame == 6:
                controller.error_message = "Could not save the game."
            dirty = game.draw(canvas)
            present(canvas, window, dirty)
            # Independent full-board path; no dirty-region restoration or cache.
            original(reference)
            reference.fill(BACKGROUND, (0, 670, 650, 50))
            game.board_view.draw(reference, controller.state.players, game.animation)
            assert pygame.image.tobytes(canvas, "RGB") == pygame.image.tobytes(reference, "RGB")
            assert pygame.image.tobytes(window, "RGB") == pygame.image.tobytes(reference, "RGB")
            if frame not in (0, 6):
                assert dirty is not None
                assert sum(area.width * area.height for area in dirty) < 1000
            game.update(.015)
        assert len(rebuilds) == 2
        game.update(1)
        assert controller.state.phase is Phase.AWAITING_ROLL
        assert game.draw(canvas) is None
    finally:
        pygame.quit()
