"""Real elapsed time and deadline accounting without platform timer jitter."""

import pytest

from snakes_ladders.ui.frame_pacing import FramePacer


class Clock:
    def __init__(self, oversleep=0):
        self.now = 0.0
        self.sleeps = []
        self.oversleep = oversleep

    def timer(self):
        self.now += .00001
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds + self.oversleep


def test_frame_work_is_subtracted_from_wait_budget():
    clock = Clock()
    pacer = FramePacer(60, clock.timer, clock.sleep)
    pacer.begin_frame()
    clock.now += .010
    pacer.wait()
    assert len(clock.sleeps) == 1
    assert clock.sleeps[0] == pytest.approx(1/60 - .010 - .001, abs=.0001)
    assert pacer.begin_frame() == pytest.approx(1/60, abs=.0001)


def test_late_frame_does_not_sleep_or_hide_elapsed_time():
    clock = Clock()
    pacer = FramePacer(60, clock.timer, clock.sleep)
    pacer.begin_frame()
    clock.now += .075
    pacer.wait()
    assert clock.sleeps == []
    assert pacer.begin_frame() >= .075


def test_oversleep_is_counted_and_next_deadline_starts_from_actual_time():
    clock = Clock(oversleep=.060)
    pacer = FramePacer(60, clock.timer, clock.sleep)
    pacer.begin_frame()
    pacer.wait()
    assert pacer.begin_frame() >= .060
    assert pacer.deadline > clock.now
    assert len(clock.sleeps) == 1


def test_active_animation_never_uses_coalesced_sleep():
    clock = Clock(oversleep=.120)
    pacer = FramePacer(60, clock.timer, clock.sleep)
    pacer.begin_frame()
    clock.now += .001  # Rendering work takes one millisecond.
    pacer.wait(precise=True)
    assert clock.sleeps == []
    assert pacer.begin_frame() == pytest.approx(1 / 60, abs=.0001)
