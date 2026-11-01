"""NFR-05 / TC-N05-1: the same source runs on Windows, Ubuntu and macOS.

CI runs this file on every supported OS. The smoke tests drive the real
main() loop headlessly; a person still repeats the run on a real display
(see README, "Portability").
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ast
import re
from pathlib import Path

import pygame
import pytest

from snakes_ladders import main as app
from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from tests.engine.test_scripted_rng import ScriptedRng

SOURCE_DIR = Path(__file__).resolve().parent.parent / "snakes_ladders"
PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"

# Calls and names that make behaviour depend on the operating system.
OS_SPECIFIC_ATTRIBUTES = {
    ("sys", "platform"), ("os", "name"), ("os", "system"), ("os", "startfile"),
    ("platform", "system"), ("platform", "platform"), ("platform", "uname"),
}
OS_SPECIFIC_MODULES = {"subprocess", "ctypes", "winreg", "msvcrt", "fcntl", "posix", "nt"}
ABSOLUTE_PATH = re.compile(r"^(?:[A-Za-z]:[\\/]|/(?:home|Users|tmp|var|etc|usr)\b)")


def source_files():
    return sorted(SOURCE_DIR.rglob("*.py"))


def test_source_files_are_found():
    assert len(source_files()) >= 10  # Guards the scans below against an empty glob.


@pytest.mark.parametrize("path", source_files(), ids=lambda p: p.relative_to(SOURCE_DIR).as_posix())
def test_no_os_specific_code(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            modules = {(node.module or "").split(".")[0]}
        else:
            modules = set()
        assert not modules & OS_SPECIFIC_MODULES, f"{path.name}:{node.lineno} imports {modules}"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            assert (node.value.id, node.attr) not in OS_SPECIFIC_ATTRIBUTES, (
                f"{path.name}:{node.lineno} uses {node.value.id}.{node.attr}"
            )
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not ABSOLUTE_PATH.match(node.value), (
                f"{path.name}:{node.lineno} hard-codes the path {node.value!r}"
            )


def test_supported_python_versions_are_declared():
    text = PYPROJECT.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.10"' in text  # SRS 2.4
    assert re.search(r'"pygame>=2,\s*<3"', text)  # SRS 2.4: Pygame 2.x


def run_script(monkeypatch, controller_factory, steps):
    """Run the real main() loop, feeding one (events, check) step per frame.

    A step's check runs at the start of the next frame, after its events were
    handled and the screen drawn. The loop ends with a QUIT event.
    """
    created = []

    def factory():
        controller = controller_factory()
        created.append(controller)
        return controller

    frame = 0

    def events():
        nonlocal frame
        if created and created[0].screen == "game" and created[0].state.phase in (Phase.ANIMATING, Phase.GAME_OVER):
            return []
        if frame:
            steps[frame - 1][1](created[0])
        if frame == len(steps):
            frame += 1
            return [pygame.event.Event(pygame.QUIT)]
        batch = steps[frame][0]
        frame += 1
        return batch

    monkeypatch.setattr(app, "GameController", factory)
    monkeypatch.setattr(pygame.event, "get", events)
    app.main()
    assert frame == len(steps) + 1  # Every step ran and the loop quit cleanly.
    return created[0]


def text(value):
    return pygame.event.Event(pygame.TEXTINPUT, text=value)


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def click(position):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position)


START_BUTTON = (150, 645)
NEW_GAME_BUTTON = (790, 605)


def test_smoke_launch_setup_and_three_turns(monkeypatch):
    # TC-N05-1 steps: launch, setup, 3 turns, exit.
    def on_setup(controller):
        assert controller.screen == "setup"

    def on_started(controller):
        assert controller.screen == "game"
        assert [p.name for p in controller.state.players] == ["Sam", "Alice"]

    def after_turn(turn):
        def check(controller):
            state = controller.state
            assert controller.last_result.player_index == (turn - 1) % 2
            assert state.current_index == turn % 2
            assert 1 <= state.last_roll <= 6
            assert all(0 <= p.position <= 100 for p in state.players)
            assert state.phase is Phase.AWAITING_ROLL
        return check

    steps = [
        ([], on_setup),
        ([text("Sam"), key(pygame.K_TAB), text("Alice")], lambda c: None),
        ([click(START_BUTTON)], on_started),
        ([key(pygame.K_SPACE)], after_turn(1)),
        ([key(pygame.K_SPACE)], after_turn(2)),
        ([key(pygame.K_SPACE)], after_turn(3)),
    ]
    controller = run_script(monkeypatch, GameController, steps)
    assert controller.running is False  # The QUIT event ended the loop.


def test_smoke_finish_a_game_and_return_to_setup(monkeypatch):
    # TC-N05-1 steps: a game finished from a state near square 94, then a new game.
    def factory():
        controller = GameController(GameEngine(rng=ScriptedRng([6])))
        controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
        controller.state.players[0].position = 94
        return controller

    def on_win(controller):
        assert controller.screen == "result"
        assert controller.state.phase is Phase.GAME_OVER
        assert controller.last_result.winner_index == 0
        assert controller.state.players[0].position == 100

    def still_result(controller):
        assert controller.screen == "result"  # Rolling after the game is ignored.

    def on_setup(controller):
        assert controller.screen == "setup"
        assert controller.state is None

    steps = [
        ([key(pygame.K_SPACE)], on_win),
        ([key(pygame.K_SPACE)], still_result),
        ([click(NEW_GAME_BUTTON)], on_setup),
    ]
    run_script(monkeypatch, factory, steps)
