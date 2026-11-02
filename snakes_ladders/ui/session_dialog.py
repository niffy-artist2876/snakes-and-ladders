"""Modal session confirmation shared by the game and results screens."""

import pygame

from snakes_ladders.ui.widgets import TEXT, button, label


class SessionDialog:
    def __init__(self, controller):
        self.controller = controller
        self.confirm_button = pygame.Rect(390, 400, 230, 50)
        self.cancel_button = pygame.Rect(660, 400, 230, 50)

    def handle_event(self, event):
        if self.controller.pending_prompt is None:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.controller.cancel_prompt()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cancel_button.collidepoint(event.pos):
                self.controller.cancel_prompt()
            elif self.confirm_button.collidepoint(event.pos):
                self.controller.on_restart_confirmed()
        return True  # Consume every event while the prompt is open.

    def draw(self, surface):
        if self.controller.pending_prompt is None:
            return
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        surface.blit(shade, (0, 0))
        panel = pygame.Rect(240, 230, 800, 260)
        pygame.draw.rect(surface, (32, 43, 61), panel, border_radius=12)
        pygame.draw.rect(surface, TEXT, panel, 2, border_radius=12)
        label(surface, "Start a new game?", (280, 265), 36)
        label(surface, "Your current game will be cleared. Saved games are kept.", (280, 325), 26)
        button(surface, self.confirm_button, "Confirm Restart")
        button(surface, self.cancel_button, "Cancel (Esc)")
