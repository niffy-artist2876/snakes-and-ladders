# Deviations from the SRS, SDD and Test Plan

Checked against `main` on 2 November 2026. Status "Open" means the gap remains, "Accepted" means the team chose it, and "Pending" means evidence is still to be collected.

## SRS

| ID | Requirement | What was built | Status |
|---|---|---|---|
| DEV-01 | FR-08 and UI-1: a setup control for the extra-turn rule | The setup screen has no such control, so games always start with extra turns off. The rule works in the engine and in saved games, and the tests switch it on directly. | Open |
| DEV-02 | UI-4: Resume is shown only if a valid save exists | Resume is always shown and is greyed out when no save file exists. Clicking it then shows "No saved game found." A file is validated only when Resume is clicked. | Accepted |
| DEV-03 | FR-15: save between turns | Saving is allowed between any two rolls, including between extra rolls. This is SDD decision D-3. | Accepted |

## SDD

| ID | Design | What was built | Status |
|---|---|---|---|
| DEV-04 | 2.4: component names (ScreenManager, InputHandler, AnimationController, BoardRenderer, InputValidator) | The same responsibilities sit in differently named modules. Section 6.1 of the SDD maps each one. | Accepted |
| DEV-05 | 3.1: a separate Start screen | The setup screen also holds Resume and Exit. | Accepted |
| DEV-06 | 3.1 and SD-1: the result screen appears after the move animation | A winning move is not animated. The controller switches to the result screen on the winning roll. | Accepted |
| DEV-07 | 3.7: a render loop capped at 60 FPS | The cap is 60 FPS. While a token moves, the loop waits by spinning instead of sleeping. On macOS CI runners, sleeps ran long and the rate fell to about 20 FPS. The spin uses one CPU core for about 0.3 s per move. Idle screens still sleep. | Accepted |
| DEV-08 | 2.5 and 3.9: test folders `engine`, `persistence`, `controller` and `ui_smoke` | Tests sit in one `tests/` folder, plus `tests/engine/`. Every file there starts with `test_`, including the shared helpers `test_factories.py` and `test_scripted_rng.py`. | Accepted |
| DEV-09 | SRS 2.4: runtime dependencies | `psutil` was added to the dev dependencies for the NFR-14 memory check. | Accepted |

## Test Plan

| ID | Plan | What was done | Status |
|---|---|---|---|
| DEV-10 | R1, TC-N15-1, TC-SEC04-6: redraw a failed chi-square sample once | Up to three attempts (`ATTEMPTS` in `tests/test_randomness.py`). With two, a correct generator would still turn about 3% of CI runs red across all jobs. | Accepted |
| DEV-11 | TC-N12-1: 20 moves, including long snake and ladder moves, on the minimum-hardware machine | An automated run plays 20 moves through the real loop on development and CI machines and requires an average of at least 30 FPS. It includes four ladder slides (the first move of each player) and no snake. Snake paths are checked in unit tests without timing. | Pending hardware run |
| DEV-12 | TC-N14-1: peak memory of the application | The CI check runs the 300-frame loop in a fresh Python process and measures that process. Measuring inside pytest counted memory left by about 380 earlier tests. The 30-minute run on target hardware is still to do. | Pending |
| DEV-13 | TC-N05-1: smoke script on Windows 10/11, Ubuntu 22.04+ and macOS 13+ | The headless smoke tests cover launch, setup, three turns, finishing a game and starting a new game. They have no save, exit, relaunch or resume steps. CI uses the latest macOS runner, not macOS 13. | Open |
| DEV-14 | Test setup | `tests/conftest.py` makes token moves instant in every test except those marked `real_animation`. | Accepted |
| DEV-15 | Test cases carry their plan ID in the test code | Most do. 53 cases are linked to existing tests in `scripts/test_case_map.json` instead, and the report generator checks each link. | Accepted |

## Evidence still to collect

- NFR-02: the study in `docs/USABILITY_STUDY.md` has not been run (0 of 5 participants).
- NFR-01, NFR-07, NFR-12 and NFR-14: runs on the reference machine (dual-core 2 GHz, 4 GB RAM, 1280 x 720 display). CI timings do not count.
- NFR-05 and NFR-09: manual runs on a real display on each operating system.
- The Sprint 2 video.
