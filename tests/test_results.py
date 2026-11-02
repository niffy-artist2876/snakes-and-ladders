import pytest

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.engine import GameEngine, Phase
from snakes_ladders.engine.setup import PlayerConfig
from tests.engine.test_factories import make_state
from tests.engine.test_scripted_rng import ScriptedRng


def test_standings_sorted_without_reordering_game_state():
    state = make_state(100, 45, 60, 12)
    rows = GameEngine().standings(state)
    assert [r.position for r in rows] == [100, 60, 45, 12]
    assert [r.name for r in rows] == ["P1", "P3", "P2", "P4"]
    assert [r.rank for r in rows] == [1, 2, 3, 4]
    assert [p.position for p in state.players] == [100, 45, 60, 12]
    state.players[0].position = 0
    assert rows[0].position == 100


def test_ties_preserve_setup_order():
    rows = GameEngine().standings(make_state(45, 100, 45, 45))
    assert [r.player_index for r in rows] == [1, 0, 2, 3]


@pytest.mark.parametrize("count", [2, 3, 4])
def test_every_player_appears_once(count):
    rows = GameEngine().standings(make_state(100, *([0] * (count - 1))))
    assert len(rows) == count
    assert {r.player_index for r in rows} == set(range(count))


def finished_controller():
    controller = GameController(GameEngine(rng=ScriptedRng([1])))
    controller.start_new_game([PlayerConfig("Sam", "blue"), PlayerConfig("Alice", "orange")])
    controller.state.current_index = 1
    controller.state.players[1].position = 99
    result = controller.on_roll_requested()
    assert result.winner_index == 1
    return controller


def test_winning_roll_opens_results_and_blocks_further_rolls():
    controller = finished_controller()
    assert controller.screen == "result"
    assert controller.state.phase is Phase.GAME_OVER
    assert controller.on_roll_requested() is None


def test_new_game_clears_finished_state():
    controller = finished_controller()
    old_state = controller.state
    controller.new_game_requested()
    assert controller.screen == "result"
    assert controller.pending_prompt == "restart"
    controller.on_restart_confirmed()
    assert controller.screen == "setup"
    assert controller.state is None
    assert controller.last_result is None
    controller.start_new_game([PlayerConfig("New1", "green"), PlayerConfig("New2", "magenta")])
    assert [p.position for p in controller.state.players] == [0, 0]
    assert old_state.players[1].position == 100


def test_exit_from_results():
    controller = finished_controller()
    controller.exit_requested()
    assert not controller.running
