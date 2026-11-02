"""Token movement animation, driven by elapsed time (NFR-12, SDD C7)."""

import logging

import pygame

logger = logging.getLogger("snakes_ladders.animation")

TARGET_FPS = 60
MIN_FPS = 30
DURATION = 0.3  # Seconds for a whole move, snake or ladder included (FR-13: under 1 s).


class TokenAnimation:
    """Walks one token along its path. Position depends on elapsed time, not frame count,
    so a slow frame makes the movement coarser but never longer or shorter."""

    def __init__(self, board_view, result, duration=None):
        self.player_index = result.player_index
        self.duration = DURATION if duration is None else duration
        squares = [result.from_pos, *range(result.from_pos + 1, result.landed_pos + 1)]
        if squares[-1] != result.final_pos:
            squares.append(result.final_pos)  # The snake or ladder after the dice move.
        self.points = [
            pygame.Vector2(board_view.token_center(square, self.player_index)) for square in squares
        ]
        self.length = sum(a.distance_to(b) for a, b in zip(self.points, self.points[1:]))
        self.elapsed = 0.0
        self.frames = 0
        self._logged = False

    @property
    def finished(self):
        return self.length == 0 or self.elapsed >= self.duration

    @property
    def center(self):
        """The token position now, at constant speed along the whole path."""
        if self.duration <= 0:
            return self.points[-1]
        remaining = min(1.0, self.elapsed / self.duration) * self.length
        for start, end in zip(self.points, self.points[1:]):
            step = start.distance_to(end)
            if remaining <= step:
                return start.lerp(end, remaining / step) if step else end
            remaining -= step
        return self.points[-1]

    def update(self, seconds):
        """Advance by one rendered frame that took `seconds`."""
        self.elapsed += max(0.0, seconds)
        self.frames += 1
        if self.finished and not self._logged:
            self._logged = True
            self._log()

    def _log(self):
        if self.length == 0 or self.elapsed <= 0:
            return  # A move that did not animate is not a frame-rate sample.
        logger.info(
            "Token move: player=%d frames=%d seconds=%.4f average_fps=%.2f",
            self.player_index + 1, self.frames, self.elapsed, self.frames / self.elapsed,
        )
