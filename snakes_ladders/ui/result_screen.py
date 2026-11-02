"""Winner announcement and final standings (FR-16)."""

import pygame

from snakes_ladders.ui.board_view import BoardView
from snakes_ladders.ui.session_dialog import SessionDialog
from snakes_ladders.ui.widgets import BACKGROUND, TOKEN_COLOURS, button, label


class ResultScreen:
    def __init__(self, controller):
        self.controller = controller
        self.board_view = BoardView()
        self.new_game_button = pygame.Rect(700, 580, 180, 50)
        self.exit_button = pygame.Rect(910, 580, 150, 50)
        self.dialog = SessionDialog(controller)

    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.new_game_button.collidepoint(event.pos):
                self.controller.new_game_requested()
            elif self.exit_button.collidepoint(event.pos):
                self.controller.exit_requested()

    def draw(self, surface):
        surface.fill(BACKGROUND)
        self.board_view.draw(surface, self.controller.state.players)
        standings = self.controller.engine.standings(self.controller.state)
        winner_index = self.controller.last_result.winner_index
        winner = self.controller.state.players[winner_index]
        label(surface, "Final board", (40, 15), 38)
        label(surface, f"Winner: {winner.name}!", (700, 65), 40)
        label(surface, "Final standings", (700, 125), 32)
        label(surface, "Rank", (700, 190))
        label(surface, "Player", (820, 190))
        label(surface, "Square", (1130, 190))
        for row, standing in enumerate(standings):
            y = 250 + row * 65
            label(surface, str(standing.rank), (715, y))
            pygame.draw.circle(surface, TOKEN_COLOURS[standing.colour], (795, y + 10), 18)
            label(surface, str(standing.player_index + 1), (790, y + 2), 22, (15, 20, 30))
            label(surface, standing.name, (830, y))
            label(surface, str(standing.position), (1150, y))
        button(surface, self.new_game_button, "New Game")
        button(surface, self.exit_button, "Exit")
        self.dialog.draw(surface)
