"""A save is dropped once the game it holds is finished (FR-15, SDD D-4)."""

from pathlib import Path

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from snakes_ladders.persistence import SaveManager
from tests.engine.test_scripted_rng import ScriptedRng

PLAYERS = [PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")]


def new_controller(directory, rolls=()):
    return GameController(GameEngine(rng=ScriptedRng(list(rolls))), SaveManager(directory))


def win_next_roll(controller):
    """Put the current player on 99 and roll a 1 (the scripted roll)."""
    controller.state.players[controller.state.current_index].position = 99
    assert controller.on_roll_requested().winner_index is not None


def test_finishing_a_resumed_game_removes_its_save(tmp_path):
    first = new_controller(tmp_path)
    first.start_new_game(PLAYERS)
    assert first.on_save_requested()

    second = new_controller(tmp_path, [1])
    assert second.on_resume_requested()
    win_next_roll(second)

    assert second.screen == "result"
    assert second.can_resume() is False
    assert not (tmp_path / "savegame.json").exists()


def test_finishing_a_game_saved_this_session_removes_its_save(tmp_path):
    controller = new_controller(tmp_path, [1])
    controller.start_new_game(PLAYERS)
    assert controller.on_save_requested()
    win_next_roll(controller)
    assert controller.can_resume() is False


def test_a_save_from_a_different_game_is_kept(tmp_path):
    saved = new_controller(tmp_path)
    saved.start_new_game(PLAYERS)
    assert saved.on_save_requested()

    other = new_controller(tmp_path, [1])
    other.start_new_game(PLAYERS)  # A fresh game, never saved.
    win_next_roll(other)

    assert other.can_resume() is True  # The earlier save is still there.


def test_restarting_after_resume_keeps_the_save_for_the_new_game(tmp_path):
    first = new_controller(tmp_path)
    first.start_new_game(PLAYERS)
    assert first.on_save_requested()

    second = new_controller(tmp_path, [1])
    assert second.on_resume_requested()
    second.new_game_requested()
    second.on_restart_confirmed()
    second.start_new_game(PLAYERS)
    win_next_roll(second)

    assert second.can_resume() is True


def test_unfinished_game_keeps_its_save(tmp_path):
    controller = new_controller(tmp_path, [3])
    controller.start_new_game(PLAYERS)
    assert controller.on_save_requested()
    controller.on_roll_requested()
    assert controller.state.phase is Phase.ANIMATING
    assert controller.can_resume() is True


def test_failure_to_remove_the_save_does_not_stop_the_win(tmp_path, monkeypatch):
    controller = new_controller(tmp_path, [1])
    controller.start_new_game(PLAYERS)
    assert controller.on_save_requested()

    def refuse(self, missing_ok=False):
        raise PermissionError("locked")

    monkeypatch.setattr(Path, "unlink", refuse)
    win_next_roll(controller)
    assert controller.screen == "result"


def test_clearing_a_missing_save_is_harmless(tmp_path):
    manager = SaveManager(tmp_path)
    manager.clear()
    assert manager.exists() is False
