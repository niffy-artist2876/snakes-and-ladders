"""Scale the logical UI without stretching it or changing hit targets."""

import pygame

from snakes_ladders.ui.widgets import BACKGROUND

LOGICAL_SIZE = (1280, 720)


def viewport_rect(window_size):
    scale = min(window_size[0] / LOGICAL_SIZE[0], window_size[1] / LOGICAL_SIZE[1])
    rect = pygame.Rect(0, 0, int(LOGICAL_SIZE[0] * scale), int(LOGICAL_SIZE[1] * scale))
    rect.center = (window_size[0] // 2, window_size[1] // 2)
    return rect


def logical_event(event, rect):
    """Translate pointer input; ignore clicks in the surrounding letterbox."""
    if not hasattr(event, "pos"):
        return event
    if not rect.collidepoint(event.pos):
        return None
    attributes = event.dict.copy()
    attributes["pos"] = (
        int((event.pos[0] - rect.x) * LOGICAL_SIZE[0] / rect.width),
        int((event.pos[1] - rect.y) * LOGICAL_SIZE[1] / rect.height),
    )
    if "rel" in attributes:
        attributes["rel"] = (event.rel[0] * LOGICAL_SIZE[0] / rect.width,
                             event.rel[1] * LOGICAL_SIZE[1] / rect.height)
    return pygame.event.Event(event.type, attributes)


def present(canvas, window, dirty=None):
    rect = viewport_rect(window.get_size())
    if rect.size == canvas.get_size():
        if dirty is None:
            window.fill(BACKGROUND)
            window.blit(canvas, rect)
        else:
            for area in dirty:
                window.blit(canvas, area.move(rect.topleft), area)
    else:
        window.fill(BACKGROUND)
        window.blit(pygame.transform.smoothscale(canvas, rect.size), rect)
