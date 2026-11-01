"""Monotonic frame deadlines independent of SDL's coarse delay timer."""

from time import perf_counter, sleep


class FramePacer:
    def __init__(self, fps, timer=perf_counter, sleeper=sleep):
        self.period = 1.0 / fps
        self.timer = timer
        self.sleeper = sleeper
        self.previous = self.timer()

    def begin_frame(self):
        now = self.timer()
        elapsed = now - self.previous
        self.previous = now
        self.deadline = now + self.period
        return elapsed

    def wait(self, precise=False):
        # Sleep for most of the interval. Finish the last millisecond using
        # the high-resolution clock rather than an SDL millisecond delay.
        # Rendering time counts towards the budget; late frames never sleep.
        remaining = self.deadline - self.timer()
        # Some background macOS processes coalesce sleeps to 50–140 ms.
        # During a short active animation, do not enter a sleep at all:
        # even sleeping for the bulk of the interval can miss the deadline.
        # Idle screens retain the lower-CPU sleep path.
        if not precise and remaining > .001:
            self.sleeper(remaining - .001)
        while self.timer() < self.deadline:
            pass
