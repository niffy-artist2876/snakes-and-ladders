"""NFR-12: non-blocking movement and real presentation timings for 20 moves."""

import logging
import os
import re

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui.animation import MIN_FPS, TokenAnimation
from snakes_ladders.ui.game_screen import GameScreen
from tests.engine.test_scripted_rng import ScriptedRng


def controller_for(rolls, count=2):
    controller = GameController(GameEngine(rng=ScriptedRng(rolls)))
    controller.start_new_game([PlayerConfig(f"P{i}", colour) for i, colour in
                               enumerate(("blue", "orange", "green", "magenta"))][:count])
    return controller


@pytest.mark.parametrize("position,roll,final", [(0, 1, 38), (91, 4, 75), (8, 4, 12), (99, 1, 100)])
def test_animation_reaches_final_square_and_blocks_roll_save(position, roll, final):
    pygame.init()
    try:
        controller = controller_for([roll])
        controller.state.players[0].position = position
        screen = GameScreen(controller)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        screen.handle_event(event)
        assert controller.screen == "game"
        assert screen.animation.center == pygame.Vector2(screen.board_view.token_center(position, 0))
        assert controller.on_save_requested() is False
        result = controller.last_result
        screen.handle_event(event)
        assert controller.last_result is result
        screen.update(TokenAnimation.DURATION / 2)
        assert screen.animation is not None
        assert screen.animation.center != pygame.Vector2(screen.board_view.token_center(position, 0))
        screen.update(TokenAnimation.DURATION / 2)
        assert screen.animation is None
        assert controller.state.players[0].position == final
        assert controller.screen == ("result" if final == 100 else "game")
        if final != 100:
            assert controller.state.phase is Phase.AWAITING_ROLL
    finally:
        pygame.quit()


def test_overshoot_has_no_spurious_animation():
    pygame.init()
    try:
        controller = controller_for([6])
        controller.state.players[0].position = 99
        screen = GameScreen(controller)
        screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        assert screen.animation is None
        assert controller.state.phase is Phase.AWAITING_ROLL
        assert controller.state.players[0].position == 99
    finally:
        pygame.quit()


def test_twenty_animated_moves_meet_thirty_fps(monkeypatch, caplog):
    controller = controller_for([1] * 20, count=4)
    monkeypatch.setattr(app, "GameController", lambda: controller)
    caplog.set_level(logging.INFO, logger="snakes_ladders.animation")
    moves = 0
    frames = 0

    def events():
        nonlocal moves, frames
        frames += 1
        assert frames < 2000, "Animation did not finish"
        if controller.state.phase is not Phase.AWAITING_ROLL:
            return []
        if moves == 20:
            return [pygame.event.Event(pygame.QUIT)]
        moves += 1
        return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    records = [r.getMessage() for r in caplog.records if r.name == "snakes_ladders.animation"]
    assert len(records) == moves == 20
    for record in records:
        print(record)
        assert int(re.search(r"frames=(\d+)", record)[1]) >= 2
        assert float(re.search(r"minimum_fps=([\d.]+)", record)[1]) >= MIN_FPS, record
