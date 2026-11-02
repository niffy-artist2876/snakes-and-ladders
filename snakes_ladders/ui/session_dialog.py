"""Modal session confirmation shared by the game and results screens."""

import pygame

from snakes_ladders.ui.widgets import TEXT, button, label


class SessionDialog:
    def __init__(self, controller):
        self.controller = controller
        self.confirm_button = pygame.Rect(390, 400, 230, 50)
        self.restart_cancel_button = pygame.Rect(660, 400, 230, 50)
        self.save_button = pygame.Rect(240, 410, 230, 50)
        self.discard_button = pygame.Rect(490, 410, 300, 50)
        self.exit_cancel_button = pygame.Rect(810, 410, 230, 50)

    @property
    def cancel_button(self):
        if self.controller.pending_prompt == "exit":
            return self.exit_cancel_button
        return self.restart_cancel_button

    def handle_event(self, event):
        if self.controller.pending_prompt is None:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.controller.cancel_prompt()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cancel_button.collidepoint(event.pos):
                self.controller.cancel_prompt()
            elif self.controller.pending_prompt == "exit":
                if self.save_button.collidepoint(event.pos):
                    self.controller.save_and_exit()
                elif self.discard_button.collidepoint(event.pos):
                    self.controller.exit_without_saving()
            elif self.confirm_button.collidepoint(event.pos):
                self.controller.on_restart_confirmed()
        return True  # Consume every event while the prompt is open.

    def draw(self, surface):
        if self.controller.pending_prompt is None:
            return
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        surface.blit(shade, (0, 0))
        panel = pygame.Rect(200, 230, 880, 270)
        pygame.draw.rect(surface, (32, 43, 61), panel, border_radius=12)
        pygame.draw.rect(surface, TEXT, panel, 2, border_radius=12)
        if self.controller.pending_prompt == "exit":
            label(surface, "Exit the game?", (240, 265), 36)
            label(surface, "Save your progress, exit without saving, or return to the game.", (240, 320), 26)
            if self.controller.error_message:
                label(surface, self.controller.error_message, (240, 365), 24, (255, 180, 145))
            elif not self.controller.can_save_before_exit():
                label(surface, "Save becomes available when the move finishes.", (240, 365), 24)
            button(surface, self.save_button, "Save & Exit", self.controller.can_save_before_exit())
            button(surface, self.discard_button, "Exit without saving")
        else:
            label(surface, "Start a new game?", (280, 265), 36)
            label(surface, "Your current game will be cleared. Saved games are kept.", (280, 325), 26)
            button(surface, self.confirm_button, "Confirm Restart")
        button(surface, self.cancel_button, "Cancel (Esc)")
