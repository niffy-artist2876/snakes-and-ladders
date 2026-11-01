"""Run the unchanged FPS acceptance test with macOS-like oversleep injected."""

from time import sleep

from snakes_ladders import main as app
from snakes_ladders.ui.frame_pacing import FramePacer
from tests import test_animation


def test_twenty_moves_with_120ms_sleep_coalescing(monkeypatch, caplog):
    calls = []

    def coalesced_sleep(seconds):
        calls.append(seconds)
        sleep(seconds + .120)

    monkeypatch.setattr(app, "FramePacer", lambda fps: FramePacer(fps, sleeper=coalesced_sleep))
    # Keep every assertion, including actual flip-to-flip minimum FPS >= 30.
    test_animation.test_twenty_animated_moves_meet_thirty_fps(monkeypatch, caplog)
    assert calls  # The slow idle sleep path really executed.
