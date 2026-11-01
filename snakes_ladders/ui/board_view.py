"""The complete board and tokens, shared by gameplay and results."""

import math

import pygame

from snakes_ladders.engine.board import Board
from snakes_ladders.ui.widgets import BACKGROUND, MIN_FONT_SIZE, TOKEN_COLOURS, label


class BoardView:
    CELL_SIZE = 60
    RECT = pygame.Rect(40, 60, 600, 600)
    SNAKE_COLOUR = (183, 49, 76)
    LADDER_COLOUR = (125, 78, 20)
    CELL_COLOURS = ((232, 240, 221), (203, 222, 200))
    TOKEN_OFFSETS = ((14, 30), (36, 30), (14, 50), (36, 50))
    TOKEN_RADIUS = 9

    def __init__(self):
        self.board = Board()
        # Cache the fixed artwork rather than rendering 100 labels each frame.
        self.artwork = pygame.Surface(self.RECT.size)
        self._draw_artwork()
        self.token_font = pygame.font.Font(None, MIN_FONT_SIZE)

    def square_rect(self, square):
        """1 is bottom left; 10 is bottom right; 100 is top left."""
        if not 1 <= square <= 100:
            raise ValueError("Board squares range from 1 to 100")
        row, column = divmod(square - 1, 10)
        if row % 2:
            column = 9 - column
        return pygame.Rect(
            self.RECT.x + column * self.CELL_SIZE,
            self.RECT.y + (9 - row) * self.CELL_SIZE,
            self.CELL_SIZE, self.CELL_SIZE,
        )

    def token_center(self, position, player_index):
        """Give each of the four players a permanent, non-overlapping slot."""
        if position == 0:
            return (170 + player_index * 30, 688)
        rect = self.square_rect(position)
        dx, dy = self.TOKEN_OFFSETS[player_index]
        return rect.x + dx, rect.y + dy

    def _anchor(self, square):
        rect = self.square_rect(square)
        return pygame.Vector2(rect.x - self.RECT.x + 50, rect.y - self.RECT.y + 10)

    def _draw_artwork(self):
        for square in range(1, 101):
            rect = self.square_rect(square).move(-self.RECT.x, -self.RECT.y)
            colour = self.CELL_COLOURS[(rect.x // 60 + rect.y // 60) % 2]
            pygame.draw.rect(self.artwork, colour, rect)
            pygame.draw.rect(self.artwork, (143, 170, 147), rect, 1)

        for base, top in self.board.ladders.items():
            start, end = self._anchor(base), self._anchor(top)
            direction = end - start
            normal = pygame.Vector2(-direction.y, direction.x).normalize() * 5
            for side in (-1, 1):
                pygame.draw.line(self.artwork, (246, 224, 163), start + side * normal, end + side * normal, 6)
                pygame.draw.line(self.artwork, self.LADDER_COLOUR, start + side * normal, end + side * normal, 3)
            rungs = max(2, int(direction.length() / 14))
            for rung in range(rungs + 1):
                point = start.lerp(end, rung / rungs)
                pygame.draw.line(self.artwork, self.LADDER_COLOUR, point - normal, point + normal, 2)

        for head, tail in self.board.snakes.items():
            start, end = self._anchor(head), self._anchor(tail)
            direction = end - start
            normal = pygame.Vector2(-direction.y, direction.x).normalize()
            steps = max(20, int(direction.length() / 3))
            waves = max(1, round(direction.length() / 65))
            points = [
                start.lerp(end, i / steps) + normal * 6 * math.sin(i / steps * waves * 2 * math.pi)
                for i in range(steps + 1)
            ]
            pygame.draw.lines(self.artwork, (255, 231, 224), False, points, 9)
            pygame.draw.lines(self.artwork, self.SNAKE_COLOUR, False, points, 5)
            pygame.draw.circle(self.artwork, self.SNAKE_COLOUR, end, 3)
            pygame.draw.circle(self.artwork, self.SNAKE_COLOUR, start, 8)
            for offset in (-3, 3):
                eye = start + normal * offset - direction.normalize() * 2
                pygame.draw.circle(self.artwork, (255, 255, 240), eye, 2)

        # Numbers sit above the paths in their own corner, clear of token slots.
        for square in range(1, 101):
            rect = self.square_rect(square).move(-self.RECT.x, -self.RECT.y)
            colour = self.CELL_COLOURS[(rect.x // 60 + rect.y // 60) % 2]
            pygame.draw.rect(self.artwork, colour, (rect.x + 2, rect.y + 2, 26, 16))
            label(self.artwork, str(square), (rect.x + 4, rect.y + 3), 19, (28, 48, 39))

    def draw_token(self, surface, player, index, center):
        """Draw one token, including its outline and number."""
        pygame.draw.circle(surface, BACKGROUND, center, self.TOKEN_RADIUS + 1)
        pygame.draw.circle(surface, TOKEN_COLOURS[player.colour], center, self.TOKEN_RADIUS)
        number = self.token_font.render(str(index + 1), True, (15, 20, 30))
        surface.blit(number, number.get_rect(center=center))

    def draw(self, surface, players, animation=None, exclude_player=None):
        surface.blit(self.artwork, self.RECT)
        label(surface, "START (0)", (40, 679), 23)
        for index, player in enumerate(players):
            if index == exclude_player:
                continue
            center = self.token_center(player.position, index)
            if animation is not None and index == animation.player_index:
                center = tuple(round(value) for value in animation.center)
            self.draw_token(surface, player, index, center)
