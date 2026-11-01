"""Time-based movement and bounded frame-rate measurements (NFR-12)."""

import logging

import pygame

logger = logging.getLogger("snakes_ladders.animation")
TARGET_FPS = 60
MIN_FPS = 30


class TokenAnimation:
    DURATION = 0.25  # Includes dice movement and any snake/ladder transition.

    def __init__(self, board, result):
        self.player_index = result.player_index
        squares = [result.from_pos]
        squares.extend(range(result.from_pos + 1, result.landed_pos + 1))
        if squares[-1] != result.final_pos:
            squares.append(result.final_pos)
        self.points = [pygame.Vector2(board.token_center(square, self.player_index)) for square in squares]
        self.elapsed = 0.0
        self.frames = 0
        self.first_frame = self.last_frame = None
        self.longest_interval = 0.0

    @property
    def finished(self):
        return self.elapsed >= self.DURATION or len(self.points) == 1

    @property
    def center(self):
        progress = min(1.0, self.elapsed / self.DURATION) * (len(self.points) - 1)
        index = min(int(progress), len(self.points) - 1)
        if index == len(self.points) - 1:
            return self.points[-1]
        return self.points[index].lerp(self.points[index + 1], progress - index)

    def update(self, seconds):
        self.elapsed += max(0.0, seconds)

    def record_frame(self, timestamp):
        if self.last_frame is not None:
            self.longest_interval = max(self.longest_interval, timestamp - self.last_frame)
        else:
            self.first_frame = timestamp
        self.last_frame = timestamp
        self.frames += 1

    def log_result(self):
        if self.frames < 2 or not self.longest_interval:
            return  # Do not report an unmeasured animation as passing.
        average = (self.frames - 1) / (self.last_frame - self.first_frame)
        minimum = 1 / self.longest_interval
        logger.info("Token move: player=%d frames=%d average_fps=%.2f minimum_fps=%.2f",
                    self.player_index + 1, self.frames, average, minimum)
