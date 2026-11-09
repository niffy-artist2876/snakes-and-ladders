# Branch coverage report

- Date: 2026-11-10
- Commit: 38dab5f on branch test-plan-sync
- Python 3.12.4 on Windows-11-10.0.26300-SP0
- Pygame 2.6.1, run headless (SDL dummy video and audio drivers)
- Command: `python scripts/generate_reports.py`

Branch coverage counts each outcome of every decision point, such as the true and false side of an `if`. A line can run while one of its branches never does, so this figure is stricter than statement coverage.

## Summary

Overall branch coverage is **89.7%** (278 of 310 branches taken, 28 partially covered). Combined statement and branch coverage, as `coverage.py` reports it, is **94.1%**.

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

| File | Branches | Taken | Partial | Branch coverage |
|---|---|---|---|---|
| `snakes_ladders/__init__.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/controller/__init__.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/controller/game_controller.py` | 22 | 21 | 1 | 95.5% |
| `snakes_ladders/controller/input_validator.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/engine/__init__.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/engine/board.py` | 4 | 4 | 0 | 100.0% |
| `snakes_ladders/engine/dice.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/engine/game_engine.py` | 6 | 6 | 0 | 100.0% |
| `snakes_ladders/engine/models.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/engine/setup.py` | 12 | 10 | 2 | 83.3% |
| `snakes_ladders/engine/turn_manager.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/main.py` | 18 | 16 | 2 | 88.9% |
| `snakes_ladders/persistence/__init__.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/persistence/checksum.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/persistence/exceptions.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/persistence/save_manager.py` | 18 | 11 | 3 | 61.1% |
| `snakes_ladders/persistence/validator.py` | 58 | 51 | 7 | 87.9% |
| `snakes_ladders/ui/__init__.py` | 0 | 0 | 0 | n/a |
| `snakes_ladders/ui/animation.py` | 12 | 9 | 3 | 75.0% |
| `snakes_ladders/ui/board_view.py` | 24 | 23 | 1 | 95.8% |
| `snakes_ladders/ui/frame_pacing.py` | 4 | 4 | 0 | 100.0% |
| `snakes_ladders/ui/game_screen.py` | 40 | 38 | 2 | 95.0% |
| `snakes_ladders/ui/result_screen.py` | 10 | 9 | 1 | 90.0% |
| `snakes_ladders/ui/session_dialog.py` | 26 | 25 | 1 | 96.2% |
| `snakes_ladders/ui/setup_screen.py` | 48 | 43 | 5 | 89.6% |
| `snakes_ladders/ui/viewport.py` | 8 | 8 | 0 | 100.0% |
| `snakes_ladders/ui/widgets.py` | 0 | 0 | 0 | n/a |

## Branches never taken

Each entry is `line→target line`, or `line→exit` when the branch leaves the function.

- `snakes_ladders/controller/game_controller.py`: 138→exit
- `snakes_ladders/engine/setup.py`: 22→23, 36→37
- `snakes_ladders/main.py`: 55→56, 79→80
- `snakes_ladders/persistence/save_manager.py`: 34→35, 37→44, 45→46, 45→52, 54→55, 54→61, 155→159
- `snakes_ladders/persistence/validator.py`: 48→49, 52→53, 63→64, 65→66, 67→68, 69→70, 83→84
- `snakes_ladders/ui/animation.py`: 39→40, 42→47, 58→59
- `snakes_ladders/ui/board_view.py`: 29→30
- `snakes_ladders/ui/game_screen.py`: 49→exit, 108→109
- `snakes_ladders/ui/result_screen.py`: 24→exit
- `snakes_ladders/ui/session_dialog.py`: 36→38
- `snakes_ladders/ui/setup_screen.py`: 49→51, 53→55, 60→61, 67→68, 69→exit
