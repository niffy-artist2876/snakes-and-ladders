"""FR-12: the current player's name and token remain visible on every frame."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.ui import game_screen
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.widgets import TEXT, TOKEN_COLOURS
from tests.engine.test_scripted_rng import ScriptedRng


@pytest.fixture
def rendered_game(monkeypatch):
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    labels = []
    original = game_screen.label

    def record(target, text, position, size=26, colour=TEXT):
        labels.append((text, position, size))
        original(target, text, position, size, colour)

    monkeypatch.setattr(game_screen, "label", record)
    yield surface, labels
    pygame.quit()


def assert_indicator(screen, rendered_game, name, colour, number):
    surface, labels = rendered_game
    labels.clear()
    screen.draw(surface)
    turns = [(text, position, size) for text, position, size in labels if text.startswith("Turn:")]
    assert len(turns) == 1
    text, position, size = turns[0]
    assert text == f"Turn: {name}"
    text_rect = pygame.font.Font(None, size).render(text, True, (255, 255, 255)).get_rect(topleft=position)
    assert surface.get_rect().contains(text_rect)
    # Sample the token away from its number, and check its matching player ID.
    assert surface.get_at((707, 95))[:3] == TOKEN_COLOURS[colour]
    assert (str(number), (714, 86), 26) in labels
    assert not screen.board_view.RECT.colliderect(text_rect)


@pytest.mark.parametrize("count", [2, 3, 4])
def test_indicator_tracks_turns_and_wraparound_for_all_player_counts(rendered_game, count):
    # Colours deliberately differ from the default setup order.
    configs = [PlayerConfig(name, colour) for name, colour in (
        ("Alex", "magenta"), ("Sam", "green"), ("Dara", "orange"), ("Alice", "blue"),
    )][:count]
    controller = GameController(GameEngine(rng=ScriptedRng([1] * (count * 2))))
    controller.start_new_game(configs)
    screen = GameScreen(controller)
    for turn in range(count * 2):
        index = turn % count
        player = configs[index]
        assert_indicator(screen, rendered_game, player.name, player.colour, index + 1)
        if turn % 2:
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.roll_button.center)
        else:
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        screen.handle_event(event)
        screen.update(1)
    assert_indicator(screen, rendered_game, configs[0].name, configs[0].colour, 1)


@pytest.mark.parametrize("phase", [Phase.AWAITING_ROLL, Phase.ANIMATING])
def test_indicator_persists_without_input_and_fits_maximum_length_name(rendered_game, phase):
    controller = GameController()
    controller.start_new_game([
        PlayerConfig("Sam", "blue"), PlayerConfig("WWWWWWWWWWWWWWW", "orange"),
    ])
    controller.state.current_index = 1
    controller.state.phase = phase
    screen = GameScreen(controller)
    for _ in range(3):
        assert_indicator(screen, rendered_game, "WWWWWWWWWWWWWWW", "orange", 2)


def test_indicator_refreshes_when_starting_another_game(rendered_game):
    controller = GameController(GameEngine(rng=ScriptedRng([1, 1])))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    screen = GameScreen(controller)
    controller.on_roll_requested()
    controller.on_animation_done()
    assert_indicator(screen, rendered_game, "Alice", "orange", 2)
    controller.state.players[1].position = 99
    controller.on_roll_requested()
    assert controller.screen == "result"
    controller.new_game_requested()
    controller.start_new_game([PlayerConfig("Dara", "green"), PlayerConfig("Alex", "magenta")])
    assert_indicator(screen, rendered_game, "Dara", "green", 1)
