"""Playable board with turn controls and a player legend."""

import pygame

from snakes_ladders.engine import Phase
from snakes_ladders.ui.animation import TokenAnimation
from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.session_dialog import SessionDialog
from snakes_ladders.ui.widgets import BACKGROUND, TOKEN_COLOURS, button, label


class GameScreen:
    def __init__(self, controller):
        self.controller = controller
        self.board_view = BoardView()
        self.animation = None
        self.animation_state = None
        self.roll_button = pygame.Rect(700, 560, 220, 50)
        self.save_button = pygame.Rect(700, 625, 140, 45)
        self.restart_button = pygame.Rect(860, 625, 160, 45)
        self.exit_button = pygame.Rect(1040, 625, 140, 45)
        self.dialog = SessionDialog(controller)

    def handle_event(self, event):
        if self.dialog.handle_event(event):
            if self.controller.screen != "game":
                self.animation = None
            return
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
                self._start_animation(result)
        elif clicked_save:
            self.controller.on_save_requested()
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
              and self.restart_button.collidepoint(event.pos)):
            self.controller.new_game_requested()
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
              and self.exit_button.collidepoint(event.pos)):
            self.controller.exit_requested()

    @property
    def animating(self):
        return self.animation is not None

    def _start_animation(self, result):
        animation = TokenAnimation(self.board_view, result)
        if result.winner_index is not None or animation.finished:
            # A winning move goes straight to the results; an overshoot has nothing to move.
            self.controller.on_animation_done()
        else:
            self.animation = animation
            self.animation_state = self.controller.state

    def update(self, seconds):
        """Advance the running animation by one frame that took `seconds`."""
        if self.animation is None:
            return
        if (self.controller.state is not self.animation_state
                or self.controller.state.phase is not Phase.ANIMATING):
            self.animation = None  # The game changed under the animation (new game, load).
            return
        self.animation.update(seconds)
        if self.animation.finished:
            self.animation = None
            self.controller.on_animation_done()

    def draw(self, surface):
        surface.fill(BACKGROUND)
        state = self.controller.state
        label(surface, "Snakes and Ladders", (40, 15), 38)
        label(surface, "Reach 100 exactly. Ladders go up; snakes go down.", (700, 45), 22)
        centers = None
        if self.animation is not None:
            centers = {self.animation.player_index: self.animation.center}
        self.board_view.draw(surface, state.players, centers)

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
        if state.phase is Phase.ANIMATING:
            hint = "Moving... your next roll is ready when the token stops."
        elif state.phase is Phase.AWAITING_ROLL:
            if self.controller.last_result is not None and self.controller.last_result.extra_roll:
                hint = "You rolled a 6! Roll again for your extra turn."
            else:
                hint = "Your turn: click Roll Dice or press Space."
        else:
            hint = "Game finished. Choose New Game on the results screen."
        label(surface, hint, (700, 530), 22)
        button(surface, self.roll_button, "Roll Dice (Space)", state.phase is Phase.AWAITING_ROLL)
        if state.last_roll is not None:
            label(surface, f"Last roll: {state.last_roll}", (950, 575))

        button(surface, self.save_button, "Save Game", state.phase is Phase.AWAITING_ROLL)
        button(surface, self.restart_button, "Restart")
        button(surface, self.exit_button, "Exit")
        if self.controller.status_message:
            label(surface, self.controller.status_message, (700, 685), 22, (110, 230, 165))
        elif self.controller.error_message:
            label(surface, self.controller.error_message, (700, 685), 22, (255, 180, 145))
        self.dialog.draw(surface)
