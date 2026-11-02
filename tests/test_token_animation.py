"""NFR-12: token movement is animated smoothly at 30 FPS or better.

Two kinds of test. The animation maths is checked with fake frame times, so it is
exact and identical on every machine. The frame rate is then measured through the
real application loop over 20 moves (TC-N12-1) and judged on the average rate, not
on the slowest single frame: one stalled frame on a shared CI machine says nothing
about whether the game renders at 30 FPS.
"""

import logging
import os
import re
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import Event, GameEngine, Phase, TurnResult
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui.animation import DURATION, MIN_FPS, TokenAnimation
from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.frame_pacing import FramePacer
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.widgets import TOKEN_COLOURS
from tests.engine.test_scripted_rng import ScriptedRng

pytestmark = pytest.mark.real_animation  # These tests need the real timing.

RealClock = pygame.time.Clock


@pytest.fixture
def board_view():
    pygame.init()
    yield BoardView()
    pygame.quit()


def move(from_pos, landed, final, event=Event.NONE, winner=None):
    return TurnResult(0, landed - from_pos, from_pos, landed, final, event, False, winner, 1)


def run(token, frame_seconds):
    """Advance an animation frame by frame and return the token position of every frame."""
    centers = []
    while not token.finished:
        token.update(frame_seconds)
        centers.append(pygame.Vector2(token.center))
    return centers


def test_token_starts_on_its_square_and_ends_on_the_final_square(board_view):
    token = TokenAnimation(board_view, move(8, 12, 12))
    assert token.center == pygame.Vector2(board_view.token_center(8, 0))
    token.update(DURATION)
    assert token.finished
    assert token.center == pygame.Vector2(board_view.token_center(12, 0))


def test_move_from_the_start_position_works(board_view):
    token = TokenAnimation(board_view, move(0, 3, 3))
    assert token.center == pygame.Vector2(board_view.token_center(0, 0))
    token.update(DURATION)
    assert token.center == pygame.Vector2(board_view.token_center(3, 0))


@pytest.mark.parametrize("name, result, via", [
    ("snake", move(14, 17, 7, Event.SNAKE), 17),
    ("ladder", move(0, 4, 14, Event.LADDER), 4),
])
def test_snake_or_ladder_visits_the_head_or_base_then_slides(board_view, name, result, via):
    # TC-FR06-1: the token visibly moves to the head, then to the tail.
    token = TokenAnimation(board_view, result)
    stop = pygame.Vector2(board_view.token_center(via, 0))
    closest = min(c.distance_to(stop) for c in run(token, 0.001))
    assert closest < 1.5
    assert token.center == pygame.Vector2(board_view.token_center(result.final_pos, 0))


def test_overshoot_has_nothing_to_animate(board_view):
    token = TokenAnimation(board_view, move(99, 99, 99, Event.OVERSHOOT))
    assert token.finished


def test_movement_depends_on_time_not_on_frame_rate(board_view):
    # The same elapsed time gives the same position at 60, 30 and 20 frames per second.
    result = move(8, 14, 14)
    positions = []
    for frames, seconds in ((12, 1 / 60), (6, 1 / 30), (4, 1 / 20)):
        token = TokenAnimation(board_view, result)
        for _ in range(frames):
            token.update(seconds)
        positions.append(pygame.Vector2(token.center))
    assert positions[0].distance_to(positions[1]) < 0.01
    assert positions[0].distance_to(positions[2]) < 0.01


def test_at_30_fps_a_move_is_smooth_and_short(board_view):
    # NFR-12 at its minimum rate: many distinct frames, small jumps, done well within 1 s (FR-13).
    token = TokenAnimation(board_view, move(0, 6, 6))  # A 6 from the start.
    centers = run(token, 1 / MIN_FPS)
    assert token.elapsed < 1.0
    assert len(centers) >= 8
    assert len({(round(c.x), round(c.y)) for c in centers}) == len(centers)  # Every frame differs.
    steps = [a.distance_to(b) for a, b in zip(centers, centers[1:])]
    assert max(steps) <= token.length / (DURATION * MIN_FPS) * 1.01 + 0.01  # Constant speed.


def make_screen(rolls, positions=(0, 0)):
    controller = GameController(GameEngine(rng=ScriptedRng(rolls)))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    for player, position in zip(controller.state.players, positions):
        player.position = position
    return controller, GameScreen(controller)


SPACE = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)


def test_roll_starts_the_animation_and_blocks_input_until_it_ends(board_view):
    # FR-17: no roll and no save while the token is moving.
    controller, screen = make_screen([3, 4])
    screen.handle_event(SPACE)
    assert controller.state.phase is Phase.ANIMATING
    assert screen.animation is not None
    assert screen.animating is True
    result = controller.last_result
    screen.handle_event(SPACE)
    assert controller.last_result is result  # The second roll was ignored.
    assert controller.on_save_requested() is False
    screen.update(DURATION / 2)
    assert controller.state.phase is Phase.ANIMATING
    screen.update(DURATION)
    assert screen.animation is None
    assert screen.animating is False
    assert controller.state.phase is Phase.AWAITING_ROLL
    screen.handle_event(SPACE)
    assert controller.last_result is not result  # Allowed again.


def test_overshoot_ends_the_turn_without_animating(board_view):
    controller, screen = make_screen([6], positions=(99, 0))
    screen.handle_event(SPACE)
    assert screen.animation is None
    assert controller.state.phase is Phase.AWAITING_ROLL
    assert controller.state.players[0].position == 99


def test_winning_move_goes_straight_to_the_results(board_view):
    controller, screen = make_screen([1], positions=(99, 0))
    screen.handle_event(SPACE)
    assert screen.animation is None
    assert controller.screen == "result"


def test_the_moving_token_is_drawn_where_the_animation_is(board_view):
    controller, screen = make_screen([6])
    surface = pygame.Surface((1280, 720))
    screen.handle_event(SPACE)
    screen.update(DURATION / 2)
    x, y = screen.animation.center
    screen.draw(surface)
    assert surface.get_at((round(x) - 6, round(y)))[:3] == TOKEN_COLOURS["blue"]
    final = screen.board_view.token_center(6, 0)
    assert surface.get_at((final[0] - 6, final[1]))[:3] != TOKEN_COLOURS["blue"]  # Not there yet.


def test_animation_is_dropped_if_the_game_changes_under_it(board_view):
    controller, screen = make_screen([3])
    screen.handle_event(SPACE)
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    screen.update(0.01)
    assert screen.animation is None


class OvershootingClock:
    """The real clock, but every sleep overshoots by 35 ms. Busy or background macOS
    machines stretch sleeps like this, and it cut a CI run to about 20 FPS."""

    def __init__(self):
        self._clock = RealClock()

    def tick(self, fps=0):
        milliseconds = self._clock.tick(fps)
        time.sleep(0.035)
        return milliseconds + 35


def play_moves(monkeypatch, caplog, count):
    """Play `count` moves through the real application loop; return (frames, seconds)."""
    controller = GameController(GameEngine(rng=ScriptedRng([1] * count)))
    controller.start_new_game([PlayerConfig(f"P{i}", c) for i, c in
                               enumerate(("blue", "orange", "green", "magenta"))])
    monkeypatch.setattr(app, "GameController", lambda: controller)
    caplog.set_level(logging.INFO, logger="snakes_ladders.animation")
    moves = 0
    frames = 0

    def events():
        nonlocal moves, frames
        frames += 1
        assert frames < 1000, "The animation never finished"
        if controller.state.phase is not Phase.AWAITING_ROLL:
            return []
        if moves == count:
            return [pygame.event.Event(pygame.QUIT),
                    pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(600, 435))]
        moves += 1
        return [SPACE]

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()

    records = [r.getMessage() for r in caplog.records if r.name == "snakes_ladders.animation"]
    assert len(records) == moves == count
    total_frames = total_seconds = 0
    for record in records:
        print(record)
        move_frames = int(re.search(r"frames=(\d+)", record)[1])
        seconds = float(re.search(r"seconds=([\d.]+)", record)[1])
        assert move_frames >= 2  # Really animated, not jumped.
        assert seconds < 1.0  # FR-13: the token arrives within a second.
        total_frames += move_frames
        total_seconds += seconds
    print(f"{count} moves: {total_frames} frames in {total_seconds:.2f} s = "
          f"{total_frames / total_seconds:.1f} FPS")
    return total_frames, total_seconds


def test_twenty_moves_in_the_real_loop_render_at_30_fps_or_better(monkeypatch, caplog):
    # TC-N12-1: frame rate logged during 20 moves.
    total_frames, total_seconds = play_moves(monkeypatch, caplog, 20)
    assert total_frames / total_seconds >= MIN_FPS, f"{total_frames / total_seconds:.1f} FPS over 20 moves"


def test_frame_rate_holds_when_the_os_sleep_overshoots(monkeypatch, caplog):
    # The macOS CI failure: sleeps stretched to ~50 ms gave about 20 FPS. A moving token
    # must not depend on the OS sleep, so the rate must still be 30 FPS or better.
    monkeypatch.setattr(pygame.time, "Clock", OvershootingClock)
    total_frames, total_seconds = play_moves(monkeypatch, caplog, 6)
    assert total_frames / total_seconds >= MIN_FPS, f"{total_frames / total_seconds:.1f} FPS"


class FakeClock:
    def __init__(self):
        self.ticks = []

    def tick(self, fps):
        self.ticks.append(fps)
        return 0


class FakeTimer:
    """Advances 1 ms every time it is read, so spinning loops end without real waiting."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        self.now += 0.001
        return self.now


def test_pacer_spins_and_never_sleeps_while_a_token_moves():
    clock = FakeClock()
    pacer = FramePacer(clock, 60, FakeTimer())
    seconds = pacer.wait(precise=True)
    assert clock.ticks == []  # No sleep that the OS could stretch.
    assert 1 / 60 <= seconds < 1 / 60 + 0.003  # Held to the frame budget, no more.


def test_pacer_sleeps_on_idle_screens_to_save_cpu():
    clock = FakeClock()
    pacer = FramePacer(clock, 60, FakeTimer())
    pacer.wait(precise=False)
    assert clock.ticks == [60]
