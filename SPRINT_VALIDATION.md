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

## 2. FR-18: Exit Game (#21)

Branch: `sprint/fr-18-exit-game`

- Exit during gameplay and window close use Save & Exit / Exit without saving / Cancel.
- Save is disabled during animation and enables after the move finishes.
- Failed saves keep the game and prompt open; retry works. Discard preserves the previous save.
- Setup and results exit immediately, with no active-game prompt.
- Existing real-loop tests now explicitly choose discard when closing an active game.
- Full suite: **407 passed**. Engine coverage: **99%**.
