"""Frame pacing for the main loop (NFR-12)."""

from time import perf_counter


class FramePacer:
    """Holds the loop to `fps` frames per second and reports how long each frame took.

    While a token moves, the pacer waits by spinning on the clock. Sleeping can
    overshoot by 50 ms or more on busy or background macOS machines (CI runners show
    it), which cuts the frame rate far below 30. Spinning costs CPU only for the
    0.3 s of a move. Idle screens still sleep, so they use almost no CPU.
    """

    def __init__(self, clock, fps, timer=perf_counter):
        self.clock = clock
        self.fps = fps
        self.timer = timer
        self._start = timer()

    def wait(self, precise):
        """Finish the current frame and return how long it took, in seconds."""
        if precise:
            deadline = self._start + 1.0 / self.fps
            while self.timer() < deadline:
                pass
        else:
            self.clock.tick(self.fps)
        now = self.timer()
        seconds = now - self._start
        self._start = now
        return seconds
