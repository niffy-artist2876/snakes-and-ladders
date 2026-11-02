"""NFR-14: verify gameplay memory and save-file size limits."""

import os
import subprocess
import sys
from pathlib import Path

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine.setup import COLOURS, PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.persistence.save_manager import MAX_SAVE_SIZE

MAX_GAMEPLAY_MEMORY_BYTES = 200_000_000
REPO_ROOT = Path(__file__).resolve().parent.parent

# The gameplay loop runs in a fresh Python process so the measurement is the
# application's own memory. Inside pytest, the process also holds everything
# the hundreds of earlier tests allocated, which is not what NFR-14 limits.
GAMEPLAY_SCRIPT = """
import sys
from pathlib import Path

import psutil
import pygame

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine.setup import COLOURS, PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.viewport import LOGICAL_SIZE


def largest_player_configs():
    return [PlayerConfig(f"Player{i:02d}" + "X" * 7, COLOURS[i]) for i in range(4)]


pygame.init()
surface = pygame.display.set_mode(LOGICAL_SIZE)
controller = GameController(save_manager=SaveManager(directory=Path(sys.argv[1])))
controller.start_new_game(largest_player_configs())
screen = GameScreen(controller)
process = psutil.Process()
peak_memory = process.memory_info().rss

for _ in range(300):
    screen.draw(surface)
    pygame.display.flip()
    peak_memory = max(peak_memory, process.memory_info().rss)
    if controller.screen == "result":
        controller.new_game_requested()
        controller.start_new_game(largest_player_configs())
    else:
        controller.on_roll_requested()
        controller.on_animation_done()

pygame.quit()
print(peak_memory)
"""


def largest_player_configs():
    return [
        PlayerConfig(f"Player{i:02d}" + "X" * 7, COLOURS[i])
        for i in range(4)
    ]


def test_largest_save_stays_within_10_kibibytes(tmp_path):
    manager = SaveManager(directory=tmp_path)
    controller = GameController(save_manager=manager)
    controller.start_new_game(largest_player_configs())

    assert controller.on_save_requested()

    assert manager.save_path.stat().st_size <= MAX_SAVE_SIZE


def test_oversized_save_is_rejected_without_replacing_previous_save(tmp_path):
    manager = SaveManager(directory=tmp_path)
    controller = GameController(save_manager=manager)
    controller.start_new_game(
        [PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")]
    )
    assert controller.on_save_requested()
    previous_save = manager.save_path.read_bytes()

    controller.state.players[0].name = "X" * MAX_SAVE_SIZE

    assert controller.on_save_requested() is False
    assert controller.error_message == "Save file exceeds the 10 KB limit."
    assert manager.save_path.read_bytes() == previous_save
    assert not manager.temp_path.exists()
    assert manager.load()["players"][0]["name"] == "Sam"


def test_four_player_gameplay_stays_within_memory_limit(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", GAMEPLAY_SCRIPT, str(tmp_path)],
        cwd=REPO_ROOT,
        env={**os.environ, "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    peak_memory = int(result.stdout.strip().splitlines()[-1])
    print(f"Peak gameplay RSS: {peak_memory / 1_000_000:.1f} MB")

    assert peak_memory <= MAX_GAMEPLAY_MEMORY_BYTES, (
        f"Peak process RSS was {peak_memory / 1_000_000:.1f} MB; "
        f"limit is {MAX_GAMEPLAY_MEMORY_BYTES / 1_000_000:.0f} MB."
    )
