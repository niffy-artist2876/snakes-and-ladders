"""NFR-09: render and operate all screens at the three acceptance sizes."""

import os
from itertools import combinations

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui import game_screen, result_screen, setup_screen
from snakes_ladders.ui.viewport import LOGICAL_SIZE, logical_event, present, viewport_rect
from snakes_ladders.ui.widgets import TEXT, label
from tests.engine.test_scripted_rng import ScriptedRng

RESOLUTIONS = [(1280, 720), (1366, 768), (1920, 1080)]


@pytest.mark.parametrize("size", RESOLUTIONS)
def test_screen_text_fits_without_overlap_and_all_views_render(size, monkeypatch, tmp_path):
    pygame.init()
    try:
        window = pygame.display.set_mode(size)
        canvas = pygame.Surface(LOGICAL_SIZE)
        boxes = []

        def record(surface, text, position, size=26, colour=TEXT):
            font = pygame.font.Font(None, size)
            boxes.append((text, font.render(text, True, colour).get_rect(topleft=position)))
            label(surface, text, position, size, colour)

        for module in (setup_screen, game_screen, result_screen):
            monkeypatch.setattr(module, "label", record)
        controller = GameController(GameEngine(rng=ScriptedRng([1])))
        configs = [PlayerConfig("W" * 14 + str(i), colour) for i, colour in enumerate(("blue", "orange", "green", "magenta"))]
        controller.start_new_game(configs)
        setup = setup_screen.SetupScreen(controller.start_new_game)
        setup.count = 4
        setup.names = [config.name for config in configs]
        game = game_screen.GameScreen(controller)
        controller.state.players[0].position = 99
        controller.on_roll_requested()
        result = result_screen.ResultScreen(controller)
        for name, screen in (("setup", setup), ("game", game), ("result", result)):
            boxes.clear()
            screen.draw(canvas)
            assert all(canvas.get_rect().contains(rect) for _, rect in boxes), boxes
            for first, second in combinations(boxes, 2):
                assert not first[1].colliderect(second[1]), (first, second)
            present(canvas, window)
            assert window.get_rect().contains(viewport_rect(size))
            pygame.image.save(window, str(tmp_path / f"{name}-{size[0]}x{size[1]}.png"))
    finally:
        pygame.quit()


@pytest.mark.parametrize("size", RESOLUTIONS)
def test_resized_application_mouse_flow_through_all_screens(size, monkeypatch):
    controller = GameController(GameEngine(rng=ScriptedRng([1, 1])))
    monkeypatch.setattr(app, "GameController", lambda: controller)
    rect = viewport_rect(size)

    def click(point):
        x = rect.x + round(point[0] * rect.width / 1280)
        y = rect.y + round(point[1] * rect.height / 720)
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y))

    batches = iter([
        [pygame.event.Event(pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]),
         pygame.event.Event(pygame.TEXTINPUT, text="Sam"),
         pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
         pygame.event.Event(pygame.TEXTINPUT, text="Alice"), click((150, 645))],
        [click((810, 585))], [click((810, 585))],
        [click((790, 605))], [pygame.event.Event(pygame.QUIT)],
    ])
    frame = 0

    def events():
        nonlocal frame
        if controller.screen == "game" and controller.state.phase.name in ("ANIMATING", "GAME_OVER"):
            return []
        frame += 1
        if frame == 2:
            assert controller.screen == "game"
        if frame == 3:
            assert controller.last_result.roll == 1
            controller.state.players[1].position = 99
        if frame == 4:
            assert controller.screen == "result"
        if frame == 5:
            assert controller.screen == "setup" and controller.state is None
        return next(batches)

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert frame == 5


def test_letterbox_clicks_are_ignored_and_pointer_motion_is_scaled():
    rect = viewport_rect((1920, 720))
    assert logical_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 100)), rect) is None
    rect = viewport_rect((1920, 1080))
    event = pygame.event.Event(pygame.MOUSEMOTION, pos=(960, 540), rel=(15, 30), buttons=(0, 0, 0))
    mapped = logical_event(event, rect)
    assert mapped.pos == (640, 360) and mapped.rel == (10, 20)
    assert event.pos == (960, 540)  # Preserve the original event.


def test_long_invalid_name_preview_stays_inside_its_field(monkeypatch):
    pygame.init()
    try:
        canvas = pygame.Surface(LOGICAL_SIZE)
        screen = setup_screen.SetupScreen()
        screen.names[0] = "W" * 64
        recorded = []

        def record(surface, text, position, size=26, colour=TEXT):
            recorded.append((text, position, size))
            label(surface, text, position, size, colour)

        monkeypatch.setattr(setup_screen, "label", record)
        screen.draw(canvas)
        text, position, size = next(item for item in recorded if item[1] == (152, 218))
        assert text.startswith("…")
        bounds = pygame.font.Font(None, size).render(text, True, TEXT).get_rect(topleft=position)
        assert screen.name_rect(0).contains(bounds)
        assert screen.names[0] == "W" * 64 and screen.validation_error()
    finally:
        pygame.quit()
