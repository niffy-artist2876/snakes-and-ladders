# Assigned issue validation

Each branch builds on the preceding branch. `main` is left unchanged.
Validation environment: Windows, Python 3.11.9, Pygame 2.6.1, headless SDL.

Commands run after each implementation:

```text
python -m coverage run -m pytest -q
python -m coverage report --include="snakes_ladders/engine/*" --fail-under=80
git diff --check
```

## 1. FR-14: Game Restart (#18)

Branch: `sprint/fr-14-game-restart`

- Restart from gameplay and New Game from results both require confirmation.
- Cancel/Esc keep the session; background roll/save input is blocked by the modal.
- Confirm opens fresh setup without closing the process or deleting saved games.
- Restart during animation clears the old animation.
- Full suite: **396 passed**. Engine coverage: **99%** (required: 80%).
