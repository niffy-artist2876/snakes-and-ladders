# Unit test report

- Date: 2026-11-09
- Commit: c07ddfc on branch docs-reports
- Python 3.12.4 on Windows-11-10.0.26300-SP0
- Pygame 2.6.1, run headless (SDL dummy video and audio drivers)
- Command: `python scripts/generate_reports.py`

A unit test exercises the rules, the controller or the persistence layer directly. It does not render a screen or start the application loop. This level also holds the integration tests that run without a display, such as the 100 seeded full games for NFR-03.

## Summary

| Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|
| 302 | 302 | 0 | 0 | 10.9 |

## Results by file

| File | Tests | Passed | Failed | Skipped | Time (s) | Requirements cited |
|---|---|---|---|---|---|---|
| `tests/engine/test_dice.py` | 10 | 10 | 0 | 0 | 0.1 | SEC-04 |
| `tests/engine/test_extra_turn.py` | 11 | 11 | 0 | 0 | 0.0 | FR-08 |
| `tests/engine/test_ladders.py` | 14 | 14 | 0 | 0 | 0.0 | FR-07 |
| `tests/engine/test_movement.py` | 12 | 12 | 0 | 0 | 0.0 | FR-04, FR-05, FR-06 |
| `tests/engine/test_overshoot.py` | 8 | 8 | 0 | 0 | 0.0 | FR-10 |
| `tests/engine/test_snakes.py` | 14 | 14 | 0 | 0 | 0.0 | FR-06 |
| `tests/engine/test_turns.py` | 5 | 5 | 0 | 0 | 0.0 | FR-05, FR-08 |
| `tests/engine/test_win.py` | 6 | 6 | 0 | 0 | 0.0 | FR-09 |
| `tests/test_data_integrity.py` | 1 | 1 | 0 | 0 | 0.5 | NFR-08 |
| `tests/test_finished_game_save.py` | 7 | 7 | 0 | 0 | 0.1 | FR-15 |
| `tests/test_initialization.py` | 9 | 9 | 0 | 0 | 0.0 | none cited |
| `tests/test_no_pygame.py` | 1 | 1 | 0 | 0 | 0.0 | NFR-06 |
| `tests/test_player_setup.py` | 19 | 19 | 0 | 0 | 0.0 | none cited |
| `tests/test_randomness.py` | 8 | 8 | 0 | 0 | 1.9 | NFR-15, SEC-04 |
| `tests/test_recoverability.py` | 11 | 11 | 0 | 0 | 3.6 | NFR-11 |
| `tests/test_reliability.py` | 100 | 100 | 0 | 0 | 1.5 | NFR-03 |
| `tests/test_results.py` | 8 | 8 | 0 | 0 | 0.0 | none cited |
| `tests/test_save_security.py` | 58 | 58 | 0 | 0 | 2.8 | SEC-02, SEC-03, SEC-05 |

## Failures

None.
