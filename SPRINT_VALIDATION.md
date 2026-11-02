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

## 3. NFR-10: Error Handling (#29)

Branch: `sprint/nfr-10-error-handling`

- The application loop logs unexpected exceptions with tracebacks to `snl.log`, clears
  potentially partial live state, and rebuilds a usable setup screen with a generic message.
- Save metadata/read permission errors are contained; missing, empty, malformed, non-UTF-8,
  and deeply nested saves are rejected without replacing the live session.
- Failed writes clear stale success messages and preserve the previous save.
- Fault injection covers engine calls, event polling, updates, drawing, and display flips.
  Each recovery test also starts a new game through the real UI loop.
- Full suite: **430 passed**. Engine coverage: **99%**.

## 4. NFR-11: Recoverability (#30)

Branch: `sprint/nfr-11-recoverability`

- The existing save implementation already flushes/fsyncs the temporary file and commits
  atomically with `os.replace`; this branch documents the commit boundary and verifies it.
- Ten child saving processes are killed at partial-write, after-flush, and before-replace
  barriers. No graceful exception handler runs in those child processes.
- Every previous save remains byte-identical and resumes through a fresh controller.
  Leftover temporary files are ignored and the following successful save works.
- Ten additional failures injected between writing and replacement preserve the old save.
- Full suite: **441 passed**. Engine coverage: **99%**.

## 5. NFR-02: Usability (#23)

Branch: `sprint/nfr-02-usability`

- Setup shows numbered steps, name/colour rules, keyboard editing hints and readiness.
- Gameplay explains the goal, roll controls, movement delay and extra-roll availability.
- Automated checks set up two players and complete a real animated first turn using
  mouse and Space at 1280x720, 1366x768 and 1920x1080. A duplicate-name correction
  flow is checked without bypassing user input. The setup and game screens were
  also visually inspected at the reference resolution.
- Full suite: **448 passed**. Engine coverage: **99%**.
- **Human acceptance remains pending:** no five-participant study results are available.
  `docs/USABILITY_STUDY.md` contains the procedure and unfilled results sheet.
  Automated UI checks do not certify the four-of-five / two-minute acceptance threshold.
