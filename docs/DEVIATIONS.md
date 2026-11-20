# Deviation Report

## Snakes and Ladders Game

Version: 1.2   Date: 20 November 2026
Format: Based on the IEEE Std 1028 problem and deviation record outline
Baseline: SRS v1.0 (`SRS.md`), SDD v1.0 (`SDD.md`), Test Plan v1.2 (`TestPlan.md`)

| Field | Value |
| ----- | ----- |
| Document identifier | DEV-SNL-001 |
| Product | Snakes and Ladders Game (desktop, hot-seat, 2 to 4 players) |
| Repository | https://github.com/niffy-artist2876/snakes-and-ladders |
| Status | Current against `main` |

## Revision History

| Version | Date | Description | Author(s) |
|---|---|---|---|
| 1.0 | 02-11-2026 | First list of deviations, DEV-01 to DEV-14 | Team |
| 1.1 | 10-11-2026 | Added DEV-15 (test case mapping file) | Team |
| 1.2 | 20-11-2026 | Added IEEE document structure | Team |

---

## 1. Introduction

### 1.1 Purpose
This document records every place where the delivered product or its tests differ from the SRS, the SDD or the Test Plan. It gives the reason for each difference and says whether it is still open. It is written for the reviewer and for anyone who reads the baseline documents and needs to know what changed.

### 1.2 Scope
It covers the code, tests and tooling on `main`. It does not replace the baseline documents, which are left as written. Where the SDD needed an as-built note, section 6 of the SDD carries it.

### 1.3 Definitions and Abbreviations

| Term | Meaning |
|---|---|
| Open | The gap remains and has not been accepted. |
| Accepted | The team chose the difference and it needs no further work. |
| Pending | The difference is accepted, but evidence is still to be collected. |
| CI | Continuous integration, the GitHub Actions run on every pull request. |
| FR, NFR | Functional and non-functional requirement in the SRS. |
| UI-n | User interface requirement in SRS section 3.1.1. |
| D-n | Design decision in the SDD. |
| TC-x | Test case in the Test Plan. |

### 1.4 References
- SRS.md, Software Requirements Specification, v1.0
- SDD.md, Software Architecture and Design Specification, v1.0
- TestPlan.md, Software Test Plan, v1.2
- docs/USABILITY_STUDY.md, NFR-02 acceptance study

### 1.5 Overview
Sections 2 to 4 list deviations from the SRS, the SDD and the Test Plan. Section 5 lists the evidence that is still to be collected. Section 6 summarises the counts.

---

## 2. Deviations from the SRS

| ID | Requirement | What was built | Status |
|---|---|---|---|
| DEV-01 | FR-08 and UI-1: a setup control for the extra-turn rule | The setup screen has no such control, so games always start with extra turns off. The rule works in the engine and in saved games, and the tests switch it on directly. | Open |
| DEV-02 | UI-4: Resume is shown only if a valid save exists | Resume is always shown and is greyed out when no save file exists. Clicking it then shows "No saved game found." A file is validated only when Resume is clicked. | Accepted |
| DEV-03 | FR-15: save between turns | Saving is allowed between any two rolls, including between extra rolls. This is SDD decision D-3. | Accepted |

## 3. Deviations from the SDD

| ID | Design | What was built | Status |
|---|---|---|---|
| DEV-04 | 2.4: component names (ScreenManager, InputHandler, AnimationController, BoardRenderer, InputValidator) | The same responsibilities sit in differently named modules. Section 6.1 of the SDD maps each one. | Accepted |
| DEV-05 | 3.1: a separate Start screen | The setup screen also holds Resume and Exit. | Accepted |
| DEV-06 | 3.1 and SD-1: the result screen appears after the move animation | A winning move is not animated. The controller switches to the result screen on the winning roll. | Accepted |
| DEV-07 | 3.7: a render loop capped at 60 FPS | The cap is 60 FPS. While a token moves, the loop waits by spinning instead of sleeping. On macOS CI runners, sleeps ran long and the rate fell to about 20 FPS. The spin uses one CPU core for about 0.3 s per move. Idle screens still sleep. | Accepted |
| DEV-08 | 2.5 and 3.9: test folders `engine`, `persistence`, `controller` and `ui_smoke` | Tests sit in one `tests/` folder, plus `tests/engine/`. Every file there starts with `test_`, including the shared helpers `test_factories.py` and `test_scripted_rng.py`. | Accepted |
| DEV-09 | SRS 2.4: runtime dependencies | `psutil` was added to the dev dependencies for the NFR-14 memory check. | Accepted |

## 4. Deviations from the Test Plan

| ID | Plan | What was done | Status |
|---|---|---|---|
| DEV-10 | R1, TC-N15-1, TC-SEC04-6: redraw a failed chi-square sample once | Up to three attempts (`ATTEMPTS` in `tests/test_randomness.py`). With two, a correct generator would still turn about 3% of CI runs red across all jobs. | Accepted |
| DEV-11 | TC-N12-1: 20 moves, including long snake and ladder moves, on the minimum-hardware machine | An automated run plays 20 moves through the real loop on development and CI machines and requires an average of at least 30 FPS. It includes four ladder slides (the first move of each player) and no snake. Snake paths are checked in unit tests without timing. | Pending hardware run |
| DEV-12 | TC-N14-1: peak memory of the application | The CI check runs the 300-frame loop in a fresh Python process and measures that process. Measuring inside pytest counted memory left by about 380 earlier tests. The 30-minute run on target hardware is still to do. | Pending |
| DEV-13 | TC-N05-1: smoke script on Windows 10/11, Ubuntu 22.04+ and macOS 13+ | The headless smoke tests cover launch, setup, three turns, finishing a game and starting a new game. They have no save, exit, relaunch or resume steps. CI uses the latest macOS runner, not macOS 13. | Open |
| DEV-14 | Test setup | `tests/conftest.py` makes token moves instant in every test except those marked `real_animation`. | Accepted |
| DEV-15 | Test cases carry their plan ID in the test code | Most do. 53 cases are linked to existing tests in `scripts/test_case_map.json` instead, and the report generator checks each link. | Accepted |

## 5. Evidence still to collect

- NFR-02: the study in `docs/USABILITY_STUDY.md` has not been run (0 of 5 participants).
- NFR-01, NFR-07, NFR-12 and NFR-14: runs on the reference machine (dual-core 2 GHz, 4 GB RAM, 1280 x 720 display). CI timings do not count.
- NFR-05 and NFR-09: manual runs on a real display on each operating system.
- The Sprint 2 video.

## 6. Summary

| Status | Count | IDs |
|---|---|---|
| Open | 2 | DEV-01, DEV-13 |
| Pending | 2 | DEV-11, DEV-12 |
| Accepted | 11 | all others |
