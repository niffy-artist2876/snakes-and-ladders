"""Playable board with turn controls and a player legend."""

import pygame

from snakes_ladders.engine import Phase
from snakes_ladders.ui.animation import TokenAnimation
from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.widgets import BACKGROUND, TOKEN_COLOURS, button, label


class GameScreen:
    def __init__(self, controller):
        self.controller = controller
        self.board_view = BoardView()
        self.roll_button = pygame.Rect(700, 560, 220, 50)
        self.save_button = pygame.Rect(700, 625, 140, 45)
        self.animation = None
        self._animation_background = None
        self._background_key = None
        self._previous_token_rect = None

    def update(self, seconds):
        if self.animation is None:
            return
        self.animation.update(seconds)
        if self.animation.finished:
            self.animation.log_result()
            self.animation = None
            self.controller.on_animation_done()
            if self.controller.state.phase is Phase.GAME_OVER:
                self.controller.screen = "result"

    def record_frame(self, timestamp):
        if self.animation is not None:
            self.animation.record_frame(timestamp)

    def handle_event(self, event):
        clicked_roll = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.roll_button.collidepoint(event.pos)
        )
        pressed_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        clicked_save = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.save_button.collidepoint(event.pos)
        )
        if clicked_roll or pressed_space:
            result = self.controller.on_roll_requested()
            if result is not None:
                self.animation = TokenAnimation(self.board_view, result)
                # Keep the board visible until a winning token reaches square 100.
                self.controller.screen = "game"
                self.update(0)
        elif clicked_save:
            self.controller.on_save_requested()

    def draw(self, surface):
        if self.animation is None:
            self._animation_background = None
            self._background_key = None
            self._previous_token_rect = None
            self._draw_scene(surface)
            return None

        state = self.controller.state
        # Include mutable scene data so resize, status or game-state changes
        # cannot leave a stale sidebar or stale stationary tokens in the cache.
        key = (id(surface), id(self.animation), state.current_index, state.phase,
               state.last_roll, self.controller.status_message, self.controller.error_message,
               tuple((p.name, p.colour, p.position) for p in state.players))
        full_redraw = key != self._background_key
        if full_redraw:
            self._draw_scene(surface, exclude_player=self.animation.player_index)
            self._animation_background = surface.copy()
            self._background_key = key
            self._previous_token_rect = None
        center = tuple(round(value) for value in self.animation.center)
        radius = self.board_view.TOKEN_RADIUS + 1
        rect = pygame.Rect(center[0] - radius, center[1] - radius, 2 * radius + 1, 2 * radius + 1)
        dirty = [rect]
        if self._previous_token_rect is not None:
            dirty.append(self._previous_token_rect)
        for area in dirty:
            surface.blit(self._animation_background, area, area)
        index = self.animation.player_index
        self.board_view.draw_token(surface, state.players[index], index, center)
        self._previous_token_rect = rect
        return None if full_redraw else dirty

    def _draw_scene(self, surface, exclude_player=None):
        surface.fill(BACKGROUND)
        state = self.controller.state
        label(surface, "Snakes and Ladders", (40, 15), 38)
        self.board_view.draw(surface, state.players, exclude_player=exclude_player)
        label(surface, "Players", (700, 150), 30)
        for i, player in enumerate(state.players):
            y = 200 + i * 75
            pygame.draw.circle(surface, TOKEN_COLOURS[player.colour], (720, y + 15), 20)
            label(surface, str(i + 1), (714, y + 6), colour=(15, 20, 30))
            label(surface, f"{player.name}   |   Square {player.position}", (755, y))
        if state.phase is Phase.GAME_OVER:
            winner = state.players[self.controller.last_result.winner_index]
            label(surface, f"Winner: {winner.name}", (700, 80), 32)
        else:
            current_player = state.players[state.current_index]
            pygame.draw.circle(surface, TOKEN_COLOURS[current_player.colour], (720, 95), 20)
            label(surface, str(state.current_index + 1), (714, 86), colour=(15, 20, 30))
            label(surface, f"Turn: {current_player.name}", (755, 80), 32)
        label(surface, "Snakes: red curves", (700, 465), 25)
        label(surface, "Ladders: brown rails", (700, 495), 25)
        button(surface, self.roll_button, "Roll Dice (Space)", state.phase is Phase.AWAITING_ROLL)
        if state.last_roll is not None:
            label(surface, f"Last roll: {state.last_roll}", (950, 575))

        button(surface, self.save_button, "Save Game", state.phase is Phase.AWAITING_ROLL)
        if self.controller.status_message:
            label(surface, self.controller.status_message, (860, 635), 22, (110, 230, 165))
        elif self.controller.error_message:
            label(surface, self.controller.error_message, (860, 635), 22, (255, 180, 145))
