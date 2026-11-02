"""NFR-02: automate the guided first-turn flow; human study remains separate."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.persistence import SaveManager
from snakes_ladders.ui.setup_screen import SetupScreen
from snakes_ladders.ui.viewport import viewport_rect
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.mark.real_animation
@pytest.mark.parametrize("size", [(1280, 720), (1366, 768), (1920, 1080)])
@pytest.mark.parametrize("input_method", ["mouse", "space"])
def test_setup_and_first_complete_turn_through_real_ui(size, input_method, tmp_path, monkeypatch):
    controller = GameController(GameEngine(rng=ScriptedRng([3])), SaveManager(tmp_path))
    monkeypatch.setattr(app, "GameController", lambda: controller)
    rect = viewport_rect(size)
    frame = 0
    completed = False

    def click(point):
        position = (rect.x + round(point[0] * rect.width / 1280),
                    rect.y + round(point[1] * rect.height / 720))
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position)

    def events():
        nonlocal frame, completed
        frame += 1
        assert frame <= 180, "First turn failed to complete"
        if frame == 1:
            return [pygame.event.Event(pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]),
                    pygame.event.Event(pygame.TEXTINPUT, text="Sam"),
                    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
                    pygame.event.Event(pygame.TEXTINPUT, text="Alice")]
        if frame == 2:
            assert controller.screen == "setup" and controller.state is None
            return [click((150, 645))]
        if frame == 3:
            assert controller.screen == "game"
            assert [player.name for player in controller.state.players] == ["Sam", "Alice"]
            assert [player.position for player in controller.state.players] == [0, 0]
            return [click((810, 585))] if input_method == "mouse" else [
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
        if controller.state.phase is Phase.ANIMATING:
            return []
        assert controller.state.phase is Phase.AWAITING_ROLL
        assert controller.state.current_index == 1 and controller.state.last_roll == 3
        assert [player.position for player in controller.state.players] == [3, 0]
        completed = True
        return [pygame.event.Event(pygame.QUIT), click((600, 435))]

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert completed and not controller.running


def test_user_can_correct_duplicate_names_and_start_without_reentering_setup(tmp_path):
    pygame.init()
    try:
        surface = pygame.display.set_mode((1280, 720))
        controller = GameController(save_manager=SaveManager(tmp_path))
        screen = SetupScreen(controller.start_new_game, controller=controller)
        screen.draw(surface)
        click_start = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.start_button.center)
        for event in [pygame.event.Event(pygame.TEXTINPUT, text="Sam"),
                      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
                      pygame.event.Event(pygame.TEXTINPUT, text="sam"), click_start]:
            screen.handle_event(event)
        assert controller.state is None and "unique" in screen.validation_error()
        screen.draw(surface)
        for _ in range(3):
            screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
        screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="Alice"))
        screen.draw(surface)
        screen.handle_event(click_start)
        assert controller.screen == "game"
        assert [player.name for player in controller.state.players] == ["Sam", "Alice"]
    finally:
        pygame.quit()
