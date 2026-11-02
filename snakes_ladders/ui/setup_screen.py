"""Collect player details; all validation goes through the application layer."""

import pygame

from snakes_ladders.controller.input_validator import validate_setup
from snakes_ladders.engine.setup import COLOURS, InputValidationError, PlayerConfig
from snakes_ladders.ui.widgets import BACKGROUND, TEXT, TOKEN_COLOURS, _render_label, button, label


class SetupScreen:
    def __init__(self, on_start=None, on_resume=None, can_resume=None, controller=None):
        self.on_start = on_start
        self.on_resume = on_resume
        self.can_resume = can_resume
        self.controller = controller
        self.start_button = pygame.Rect(60, 620, 180, 50)
        self.resume_button = pygame.Rect(260, 620, 180, 50)
        self.exit_button = pygame.Rect(460, 620, 180, 50)
        self.count = 2
        self.names = ["", "", "", ""]
        self.colours = list(COLOURS)
        self.active = 0
        self.count_buttons = [(n, pygame.Rect(260 + (n - 2) * 80, 110, 65, 45)) for n in range(2, 5)]

    def name_rect(self, index):
        return pygame.Rect(140, 205 + index * 80, 420, 48)

    def colour_rect(self, index):
        return pygame.Rect(590, 205 + index * 80, 190, 48)

    def configs(self):
        return validate_setup([
            PlayerConfig(self.names[i], self.colours[i]) for i in range(self.count)
        ])

    def validation_error(self):
        try:
            self.configs()
        except InputValidationError as error:
            return str(error)
        return ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_button.collidepoint(event.pos) and self.controller is not None:
                self.controller.exit_requested()
                return
            if self.start_button.collidepoint(event.pos) and not self.validation_error():
                if self.on_start is not None:
                    self.on_start(self.configs())
                return
            if self.resume_button.collidepoint(event.pos):
                if self.on_resume is not None:
                    self.on_resume()
                return
            for count, rect in self.count_buttons:
                if rect.collidepoint(event.pos):
                    self.count, self.active = count, min(self.active, count - 1)
            for i in range(self.count):
                if self.name_rect(i).collidepoint(event.pos):
                    self.active = i
                if self.colour_rect(i).collidepoint(event.pos):
                    self.colours[i] = COLOURS[(COLOURS.index(self.colours[i]) + 1) % len(COLOURS)]
        elif event.type == pygame.TEXTINPUT:
            # Bound the buffer even for a very large pasted text event.
            self.names[self.active] = (self.names[self.active] + event.text)[:64]
        elif event.key_events if hasattr(event, "key_events") else False:
            pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.names[self.active] = self.names[self.active][:-1]
            elif event.key in (pygame.K_TAB, pygame.K_RETURN):
                self.active = (self.active + 1) % self.count

    def draw(self, surface):
        surface.fill(BACKGROUND)
        label(surface, "Set up your players", (60, 45), 42)
        label(surface, "1. Players:", (60, 125))
        for count, rect in self.count_buttons:
            button(surface, rect, str(count), self.count == count)
        label(surface, "2. Enter names (1-15 letters, digits or spaces). Click a colour to change it.", (60, 170), 24)
        for i in range(self.count):
            rect = self.name_rect(i)
            pygame.draw.rect(surface, (43, 53, 72), rect, border_radius=6)
            pygame.draw.rect(surface, (100, 180, 255) if i == self.active else (90, 100, 120), rect, 2, border_radius=6)
            label(surface, str(i + 1), (100, rect.y + 13))
            name = self.names[i] or "Enter name"
            preview = name
            while _render_label(preview, 26, TEXT).get_width() > rect.width - 24:
                name = name[1:]
                preview = "…" + name
            label(surface, preview, (rect.x + 12, rect.y + 13))
            colour_rect = self.colour_rect(i)
            pygame.draw.rect(surface, TOKEN_COLOURS[self.colours[i]], colour_rect, border_radius=6)
            label(surface, f"{i + 1}: {self.colours[i]}", (colour_rect.x + 12, colour_rect.y + 13), colour=(15, 20, 30))
        label(surface, "Tab / Enter: next name. Backspace: edit. Names and colours must be unique.", (60, 515), 24)
        error = self.validation_error()
        if self.controller and self.controller.error_message:
            msg = self.controller.error_message
            msg_color = (255, 180, 145)
        elif not any(self.names[:self.count]):
            msg = "Enter a name for each player to enable Start Game."
            msg_color = TEXT
        elif error:
            msg = error
            msg_color = (255, 180, 145)
        else:
            msg = "Ready! Choose Start Game below."
            msg_color = (110, 230, 165)
        label(surface, msg, (60, 560), 25, msg_color)
        label(surface, "3. Start Game, then click Roll Dice (or press Space) to take your turn.", (60, 595), 24)
        button(surface, self.start_button, "Start Game", not error and self.on_start is not None)

        can_resume = self.can_resume() if callable(self.can_resume) else (self.on_resume is not None)
        if can_resume or self.on_resume is not None:
            button(surface, self.resume_button, "Resume Game", can_resume)
        if self.controller is not None:
            button(surface, self.exit_button, "Exit")
