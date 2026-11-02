"""NFR-11 / TC-N11-1: kill ten saving processes before the atomic commit."""

import subprocess
import sys
import time
from pathlib import Path

import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager, SaveWriteError


INTERRUPTED_SAVE = r'''
import builtins
import os
import sys
import time
from pathlib import Path

from snakes_ladders.engine import GameEngine
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager
from snakes_ladders.persistence import save_manager as module

directory = Path(sys.argv[1])
stage = sys.argv[2]
manager = SaveManager(directory)
state = GameEngine().new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
state.players[0].position = 25

def stop_at_barrier():
    (directory / "save-barrier.ready").write_text(stage, encoding="utf-8")
    while True:
        time.sleep(0.05)

class PartialWriter:
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()

    def write(self, data):
        self.stream.write(data[:len(data) // 2])
        self.stream.flush()
        os.fsync(self.stream.fileno())
        stop_at_barrier()

if stage == "partial-write":
    def partial_open(path, mode):
        return PartialWriter(builtins.open(path, mode))
    module.open = partial_open
elif stage == "after-flush":
    sync = os.fsync
    def paused_sync(fd):
        sync(fd)
        stop_at_barrier()
    os.fsync = paused_sync
else:
    os.replace = lambda *args: stop_at_barrier()

manager.save(state)
raise AssertionError("The save barrier was not reached")
'''


def initial_save(tmp_path):
    manager = SaveManager(tmp_path)
    state = GameEngine().new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    state.players[0].position = 12
    state.current_index = 1
    manager.save(state)
    return manager, state


@pytest.mark.parametrize("attempt", range(10))
def test_ten_process_interruptions_keep_previous_save_loadable(tmp_path, attempt):
    manager, state = initial_save(tmp_path)
    original = manager.save_path.read_bytes()
    expected = manager.load()
    stage = ("partial-write", "after-flush", "before-replace")[attempt % 3]
    ready = tmp_path / "save-barrier.ready"
    process = subprocess.Popen(
        [sys.executable, "-c", INTERRUPTED_SAVE, str(tmp_path), stage],
        cwd=Path(__file__).resolve().parents[1],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists(), "Saving subprocess failed to reach the interruption barrier"
        assert ready.read_text(encoding="utf-8") == stage
        assert process.poll() is None
        process.kill()  # Abrupt termination: no Python exception handler or cleanup runs.
        process.communicate(timeout=10)
    finally:
        if process.poll() is None:
            process.kill()
        stdout, stderr = process.communicate(timeout=10)
    assert not stderr, (stdout, stderr)
    assert manager.save_path.read_bytes() == original
    assert manager.temp_path.exists()  # The interrupted process left its temporary file.

    # Relaunch through the public controller API; the leftover temp file is ignored.
    resumed = GameController(save_manager=SaveManager(tmp_path))
    assert resumed.on_resume_requested()
    assert resumed.state == state
    assert resumed.save_manager.load() == expected

    # A subsequent successful save replaces stale temporary data and can also resume.
    resumed.state.players[0].position = 25
    assert resumed.on_save_requested()
    assert not manager.temp_path.exists()
    assert SaveManager(tmp_path).load()["players"][0]["position"] == 25


def test_failure_after_temp_write_before_replace_preserves_save(tmp_path, monkeypatch):
    manager, state = initial_save(tmp_path)
    original = manager.save_path.read_bytes()
    state.players[0].position = 25

    def fail_replace(source, destination):
        assert Path(source).read_bytes() != original
        assert Path(destination).read_bytes() == original
        raise OSError("Injected failure before atomic replacement")

    monkeypatch.setattr("os.replace", fail_replace)
    for _ in range(10):
        with pytest.raises(SaveWriteError):
            manager.save(state)
        assert manager.save_path.read_bytes() == original
        assert manager.load()["players"][0]["position"] == 12
        assert not manager.temp_path.exists()
