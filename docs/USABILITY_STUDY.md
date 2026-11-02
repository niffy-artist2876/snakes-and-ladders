# NFR-02 first-time-user acceptance study

Status: **Pending participant testing**. Automated UI checks pass separately;
they do not establish how quickly or independently a person can learn the game.

Requirement: SRS NFR-02 / TestPlan TC-N02-1. At least four of five first-time
users must set up a two-player game and complete one full turn, without external
help, within 120 seconds.

## Procedure

1. Recruit five people who have not used this application. Use participant IDs
   instead of personal details. Test the same revision and record it below.
2. Launch `python -m snakes_ladders.main` with a real display at a supported
   resolution (1280x720, 1366x768, or 1920x1080). Start with a fresh setup screen.
3. Give only this task: "Set up a two-player game and complete one full turn."
   Let the participant use the application's own instructions. Do not explain
   the controls, validate their choices, or demonstrate the task.
4. Start the stopwatch when the participant begins. Stop it once the first dice
   roll and movement finish and the next player's turn is available.
5. Record time, completion, any outside assistance, and hesitation or errors.
   A successful attempt is completed unaided in at most 120 seconds. Stop an
   unfinished attempt at 120 seconds and mark it unsuccessful.
6. Start a fresh session for each person. Count successes only after all five
   participants finish. If fewer than four succeed, address observed problems
   and repeat the study with new first-time participants.

## Results

Revision: pending. Test date: pending. OS / Python / Pygame / resolution: pending.

| Participant | Completed a full turn? | Seconds | Outside help? | Success (completed, no help, <=120 s)? | Hesitation / errors |
| --- | --- | --- | --- | --- | --- |
| P1 | Pending | Pending | Pending | Pending | Pending |
| P2 | Pending | Pending | Pending | Pending | Pending |
| P3 | Pending | Pending | Pending | Pending | Pending |
| P4 | Pending | Pending | Pending | Pending | Pending |
| P5 | Pending | Pending | Pending | Pending | Pending |

Success count: pending / 5. Acceptance decision: **Pending**.

Never substitute automated test durations or invented participant results for
this study. Commit the actual results to the usability branch when available.
