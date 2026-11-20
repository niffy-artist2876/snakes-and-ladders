# NFR-02 Usability Acceptance Study

## Snakes and Ladders Game

Version: 1.1   Date: 20 November 2026
Format: Based on the IEEE Std 829 test procedure and test summary outline
Baseline: SRS v1.0 (`SRS.md`), Test Plan v1.2 (`TestPlan.md`)

| Field | Value |
| ----- | ----- |
| Document identifier | UST-SNL-001 |
| Product | Snakes and Ladders Game (desktop, hot-seat, 2 to 4 players) |
| Test case | TC-N02-1 |
| Requirement | NFR-02 |
| Status | Pending participant testing (0 of 5 run) |

## Revision History

| Version | Date | Description | Author(s) |
|---|---|---|---|
| 1.0 | 02-11-2026 | Study procedure and blank results table | Team |
| 1.1 | 20-11-2026 | Added IEEE document structure | Team |

---

## 1. Introduction

### 1.1 Purpose
This document is the procedure and the results sheet for the first-time-user study required by NFR-02. It says how the study is run and where the results are recorded. It is written for the people who run the study and for the reviewer who decides whether NFR-02 is met.

### 1.2 Scope
The study covers one task: setting up a two-player game and completing one full turn. Automated UI checks pass separately (`tests/test_usability.py`). They do not show how quickly or independently a person can learn the game, so they do not count as evidence for NFR-02.

### 1.3 Definitions and Abbreviations

| Term | Meaning |
|---|---|
| First-time user | A person who has not used this application before. |
| Success | A participant completes the task unaided in at most 120 seconds. |
| Full turn | The first dice roll and movement finish, and the next player's turn is available. |

### 1.4 References
- SRS.md, NFR-02
- TestPlan.md, TC-N02-1
- docs/DEVIATIONS.md, section 5

---

## 2. Acceptance Criterion

At least four of five first-time users must set up a two-player game and complete one full turn, without external help, within 120 seconds.

## 3. Test Environment

- Five participants, identified as P1 to P5 with no personal details.
- A real display at a supported resolution: 1280x720, 1366x768 or 1920x1080.
- The same revision of the application for all participants, recorded in section 5.
- Launch command: `python -m snakes_ladders.main`
- A stopwatch and a fresh setup screen for each participant.

## 4. Procedure

1. Recruit five people who have not used this application. Use participant IDs instead of personal details. Test the same revision and record it in section 5.
2. Launch the application on the real display and start with a fresh setup screen.
3. Give only this task: "Set up a two-player game and complete one full turn." Let the participant use the application's own instructions. Do not explain the controls, validate their choices, or demonstrate the task.
4. Start the stopwatch when the participant begins. Stop it once the first dice roll and movement finish and the next player's turn is available.
5. Record time, completion, any outside assistance, and hesitation or errors. A successful attempt is completed unaided in at most 120 seconds. Stop an unfinished attempt at 120 seconds and mark it unsuccessful.
6. Start a fresh session for each person. Count successes only after all five participants finish.
7. If fewer than four succeed, address the observed problems and repeat the study with new first-time participants.

## 5. Results

Revision: pending. Test date: pending. OS / Python / Pygame / resolution: pending.

| Participant | Completed a full turn? | Seconds | Outside help? | Success (completed, no help, <=120 s)? | Hesitation / errors |
| --- | --- | --- | --- | --- | --- |
| P1 | Pending | Pending | Pending | Pending | Pending |
| P2 | Pending | Pending | Pending | Pending | Pending |
| P3 | Pending | Pending | Pending | Pending | Pending |
| P4 | Pending | Pending | Pending | Pending | Pending |
| P5 | Pending | Pending | Pending | Pending | Pending |

## 6. Summary and Decision

Success count: pending / 5. Acceptance decision: pending.

Never substitute automated test durations or invented participant results for this study. Commit the actual results to a branch when available.
