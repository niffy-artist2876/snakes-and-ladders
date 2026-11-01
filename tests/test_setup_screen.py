import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from snakes_ladders.ui.setup_screen import SetupScreen


@pytest.fixture
def surface():
    pygame.init()
    yield pygame.display.set_mode((1280, 720))
    pygame.quit()


def test_edit_names_and_change_colours(surface):
    screen = SetupScreen()
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text=" Sam "))
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="Alice"))
    assert [p.name for p in screen.configs()] == ["Sam", "Alice"]
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.colour_rect(0).center))
    assert "unique" in screen.validation_error()
    screen.draw(surface)


def test_large_input_is_bounded_and_invalid(surface):
    screen = SetupScreen()
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="A" * 10000))
    assert len(screen.names[0]) == 64
    assert screen.validation_error()
    screen.draw(surface)


def test_start_ignores_incomplete_setup_then_starts_valid_players(surface):
    from snakes_ladders.controller.game_controller import GameController
    from snakes_ladders.ui.game_screen import GameScreen

    controller = GameController()
    screen = SetupScreen(controller.start_new_game)
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.start_button.center)
    screen.handle_event(click)
    assert controller.state is None
    screen.names[0] = "Sam"
    screen.handle_event(click)
    assert controller.state is None
    screen.names[1] = "Alice"
    screen.draw(surface)
    screen.handle_event(click)
    assert controller.screen == "game"
    game = GameScreen(controller)
    game.draw(surface)
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert controller.state.last_roll in range(1, 7)
    game.draw(surface)


def test_four_player_selection_starts_all_players(surface):
    from snakes_ladders.controller.game_controller import GameController

    controller = GameController()
    screen = SetupScreen(controller.start_new_game)
    screen.names = ["A", "B", "C", "D"]
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.count_buttons[-1][1].center))
    screen.draw(surface)
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.start_button.center))
    assert len(controller.state.players) == 4


def test_result_screen_buttons_and_rendering(surface):
    from snakes_ladders.ui.result_screen import ResultScreen
    from tests.test_results import finished_controller

    controller = finished_controller()
    screen = ResultScreen(controller)
    screen.draw(surface)
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.new_game_button.center))
    assert controller.screen == "setup"
    controller = finished_controller()
    screen = ResultScreen(controller)
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.exit_button.center))
    assert not controller.running


def test_application_flow_through_new_game_and_exit(surface, monkeypatch):
    from snakes_ladders import main as app
    from snakes_ladders.controller.game_controller import GameController
    from snakes_ladders.engine import GameEngine
    from tests.engine.test_scripted_rng import ScriptedRng

    controller = GameController(GameEngine(rng=ScriptedRng([1])))
    monkeypatch.setattr(app, "GameController", lambda: controller)
    batches = iter([
        [pygame.event.Event(pygame.TEXTINPUT, text="Sam"),
         pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
         pygame.event.Event(pygame.TEXTINPUT, text="Alice"),
         pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 640))],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=app.ResultScreen(controller).new_game_button.center)],
        [pygame.event.Event(pygame.QUIT)],
    ])
    frame = 0

    def events():
        nonlocal frame
        if controller.screen == "game" and controller.state.phase.name in ("ANIMATING", "GAME_OVER"):
            return []
        frame += 1
        if frame == 2:
            controller.state.players[0].position = 99
        if frame == 3:
            assert controller.screen == "result"
        if frame == 4:
            assert controller.screen == "setup"
            assert controller.state is None
        return next(batches)

    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert not controller.running
