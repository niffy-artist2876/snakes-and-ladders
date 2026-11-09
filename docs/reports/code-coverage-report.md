# Code coverage report (statement coverage)

- Date: 2026-11-09
- Commit: c07ddfc on branch docs-reports
- Python 3.12.4 on Windows-11-10.0.26300-SP0
- Pygame 2.6.1, run headless (SDL dummy video and audio drivers)
- Command: `python scripts/generate_reports.py`

Statement coverage is the share of executable lines that ran at least once during the full test suite.

## Summary

Overall statement coverage is **95.3%** (1022 of 1072 statements). Coverage of `snakes_ladders/engine/` is **98.7%**, which meets the 80% requirement in NFR-06. CI fails the build below that figure.

## By package

| Package | Statements | Statement coverage | Branches | Branch coverage |
|---|---|---|---|---|
| `__init__.py` | 0 | 100.0% | 0 | n/a |
| `controller` | 130 | 100.0% | 22 | 95.5% |
| `engine` | 151 | 98.7% | 22 | 90.9% |
| `main.py` | 57 | 96.5% | 18 | 88.9% |
| `persistence` | 263 | 85.2% | 76 | 81.6% |
| `ui` | 471 | 98.5% | 172 | 92.4% |

## By file

| File | Statements | Missed | Coverage | Lines not run |
|---|---|---|---|---|
| `snakes_ladders/__init__.py` | 0 | 0 | 100.0% | none |
| `snakes_ladders/controller/__init__.py` | 0 | 0 | 100.0% | none |
| `snakes_ladders/controller/game_controller.py` | 129 | 0 | 100.0% | none |
| `snakes_ladders/controller/input_validator.py` | 1 | 0 | 100.0% | none |
| `snakes_ladders/engine/__init__.py` | 5 | 0 | 100.0% | none |
| `snakes_ladders/engine/board.py` | 15 | 0 | 100.0% | none |
| `snakes_ladders/engine/dice.py` | 8 | 0 | 100.0% | none |
| `snakes_ladders/engine/game_engine.py` | 42 | 0 | 100.0% | none |
| `snakes_ladders/engine/models.py` | 42 | 0 | 100.0% | none |
| `snakes_ladders/engine/setup.py` | 34 | 2 | 94.1% | 23, 37 |
| `snakes_ladders/engine/turn_manager.py` | 5 | 0 | 100.0% | none |
| `snakes_ladders/main.py` | 57 | 2 | 96.5% | 56, 80 |
| `snakes_ladders/persistence/__init__.py` | 5 | 0 | 100.0% | none |
| `snakes_ladders/persistence/checksum.py` | 10 | 1 | 90.0% | 17 |
| `snakes_ladders/persistence/exceptions.py` | 11 | 0 | 100.0% | none |
| `snakes_ladders/persistence/save_manager.py` | 137 | 31 | 77.4% | 35, 42-67, 96-97, 157-158 |
| `snakes_ladders/persistence/validator.py` | 100 | 7 | 93.0% | 49, 53, 64, 66, 68, 70, 84 |
| `snakes_ladders/ui/__init__.py` | 0 | 0 | 100.0% | none |
| `snakes_ladders/ui/animation.py` | 42 | 3 | 92.9% | 40, 47, 59 |
| `snakes_ladders/ui/board_view.py` | 80 | 1 | 98.8% | 30 |
| `snakes_ladders/ui/frame_pacing.py` | 17 | 0 | 100.0% | none |
| `snakes_ladders/ui/game_screen.py` | 97 | 1 | 99.0% | 109 |
| `snakes_ladders/ui/result_screen.py` | 41 | 0 | 100.0% | none |
| `snakes_ladders/ui/session_dialog.py` | 53 | 0 | 100.0% | none |
| `snakes_ladders/ui/setup_screen.py` | 102 | 2 | 98.0% | 61, 68 |
| `snakes_ladders/ui/viewport.py` | 24 | 0 | 100.0% | none |
| `snakes_ladders/ui/widgets.py` | 15 | 0 | 100.0% | none |
