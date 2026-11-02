# snake-game

## Running the application

Install Python 3.10+ and run from the repository root:

```sh
python -m pip install -e ".[dev]"
python -m snakes_ladders.main
```

Choose 2–4 players, enter each name, and click token colours to cycle them.
Names must be unique (ignoring case), contain 1–15 ASCII letters, digits or
spaces, and cannot be blank. Colours must also be unique. Tab moves to the
next name field. Start Game becomes available only when all selected players
are valid. Players start at position 0 and take turns in setup order.
The gameplay view displays a 10 × 10 board numbered 1–100 in boustrophedon
order: 1 starts at the bottom left, rows alternate direction, and 100 is at
the top left. All eight snakes and eight ladders are drawn from the same
layout used by the rules. Numbered, coloured tokens have separate slots so
all four remain visible when sharing a square; players at position 0 appear
in the Start area below the board. Click Roll Dice or press Space to play.
During gameplay, the turn indicator always shows the current player's name
and numbered token in their chosen colour. It updates when the turn passes
to the next player.

When a player reaches square 100, the Result screen announces the winner
and lists all players by descending position alongside the final board.
Ties retain setup order.
Restart during a game and New Game on the Result screen ask for confirmation,
then return to a blank setup screen. Cancel keeps the current session.
Exit (including closing the window) offers Save & Exit, Exit without saving,
or Cancel while a game is in progress. Save becomes available once a moving
token stops. A failed save keeps the game open so it can be retried.

## First-time use (NFR-02)

The setup screen shows three steps, name/colour rules, keyboard hints and a
readiness message. Gameplay shows the goal, the current player, how to roll,
and when a move is still in progress. `tests/test_usability.py` drives setup
and a complete first turn through the real application using both mouse and
Space at each supported acceptance resolution.

The separate five-participant acceptance study has **not been run**. Use
[the study procedure and results sheet](docs/USABILITY_STUDY.md) to record
whether at least four of five first-time users succeed unaided within two minutes.

## Save and resume integrity (NFR-08)

The save/resume regression test compares every saved gameplay field through
20 round trips across two-, three- and four-player states. Five cycles also
save immediately after resuming and verify a second restore. Run
`python -m pytest tests/test_data_integrity.py -q`.

Run automated checks with `python -m pytest`.

Team members: 
1) Name: shishir hegde  SRN: PES1UG24CS438
2) Name: Shaurya singh SRN: PES1UG24CS437
3) Name: Sharat doddihal SRN: PES1UG24CS430
4) Name: Shashannk palcharla SRN: PES1UG24CS436

Introduction: 



## Functional Requirements

1. **Game Initialization**: The system shall allow 2 or more players to join a game session before it starts.
2. **Player Setup**: The system shall allow each player to select/be assigned a unique token and name.
3. **Dice Roll**: The system shall allow the current player to roll a dice (random number 1–6) on their turn.
4. **Token Movement**: The system shall move a player's token forward by the number of steps shown on the dice.
5. **Turn Management**: The system shall enforce turn order, allowing only the current player to roll and move.
6. **Snake Encounter**: The system shall move a token down to a snake's tail if it lands on the snake's head.
7. **Ladder Encounter**: The system shall move a token up to the top of a ladder if it lands on the ladder's base.
8. **Extra Turn Rule**: The system shall grant an additional roll to a player who rolls a 6 (if enabled).
9. **Win Condition Check**: The system shall check after every move whether a player has reached the final square and declare them the winner.
10. **Overshoot Handling**: The system shall prevent a token from moving past the final square, per configured rules.
11. **Board Display**: The system shall visually display the board, snakes, ladders, and current token positions.
12. **Turn Indicator**: The system shall display whose turn it currently is.
13. **Game State Update**: The system shall update each player's position on the board in real time after every move.
14. **Game Reset/Restart**: The system shall allow players to start a new game without restarting the application.
15. **Game Save/Resume (optional)**: The system shall allow the current game state to be saved and resumed later.
16. **Score/Result Display**: The system shall display the winner and final standings once the game ends.
17. **Invalid Move Handling**: The system shall prevent moves or actions outside the defined game rules.
18. **Exit Game**: The system shall allow a player to exit or quit the game at any point.




Non functional requirements: 
1) Performance: The game should respond to user actions such as rolling the dice or moving a token within 1 second.
2) Usability: The interface should be simple and intuitive so that a new user can understand how to play without requiring detailed instructions.
3) Reliability: The game should correctly maintain player positions, turns, snake movements, and ladder movements throughout the game without losing game state.
4) Availability: The application should be available whenever the user launches it and should not depend on unnecessary external services.
5) Portability: The game should run correctly on the intended operating systems or platforms without major changes.
6) Maintainability: The code should be modular so that features such as new boards, multiplayer modes, or rule changes can be added easily.
7) Scalability: The system should support the intended number of players without noticeable degradation in performance.
8) Security: If player accounts, usernames, scores, or login details are stored, the system should prevent unauthorized access to that information.
9) Data Integrity: Saved scores, player positions, and game results should not become corrupted during gameplay or saving/loading.
10) Compatibility: The game should display and function correctly on the supported screen resolutions and devices.
11) Error Handling: Invalid inputs or unexpected errors should be handled gracefully without crashing the application.
12) Recoverability: If the game supports saving, the user should be able to resume a saved game from the correct previous state.
13) Responsiveness: UI elements such as buttons, animations, dice rolls, and player movement should remain smooth during gameplay.
14) Accessibility: Text, buttons, player tokens, snakes, and ladders should be clearly visible and distinguishable.
15) Resource Efficiency: The game should not consume excessive CPU, memory, or storage while running.




## Accessible text and tokens (NFR-13)

UI text is clamped to at least 19 pixels, equivalent to 14 pt at the
reference 96 DPI. Board token labels use the same minimum and have larger,
non-overlapping slots; snake and ladder endpoints have their own corner.
The four token colours use the Okabe-Ito palette and always carry distinct
player numbers in the board, player legend, turn indicator and results.

Run `python -m pytest tests/test_accessibility.py -q` for the minimum font
size and token label checks. The suite simulates full protanopia,
deuteranopia and tritanopia using the published Machado et al. (2009)
linear-sRGB matrices. It checks pairwise CIE Lab separation (Delta E 76
at least 10) and at least 4.5:1 number contrast in normal and simulated
vision. These are regression checks, not a substitute for testing with users;
number labels provide identification independently of colour perception.

## Roll performance (NFR-01)

Repeated UI labels use a bounded 512-entry rendered-text cache; fixed board
artwork is already cached. Roll handling updates the engine synchronously,
and the next frame presents the dice result and moved token without a delay.
Run `python -m pytest tests/test_roll_performance.py -q -s` to time 50 roll
inputs through the application's real event loop and display flip, checking
the displayed dice result and token after every roll. Each sample must be
at most one second. Headless SDL checks run in CI; repeat on the SRS 2.4
minimum hardware (dual-core 2 GHz CPU, 4 GB RAM, 1280 x 720 display) with a
real display to establish hardware acceptance. Cloud timings do not certify
that hardware.

## Portability (NFR-05)

The same source tree must run on Windows 10/11, Ubuntu 22.04+ and macOS 13+.
CI runs the full test suite on Windows, Ubuntu 22.04, the latest Ubuntu and
the latest macOS, on Python 3.10 and 3.12. `tests/test_portability.py` adds
two checks: a scan that fails the build if source code branches on the
operating system or hard-codes an absolute path, and headless smoke runs of
the real application loop (launch, setup, three turns, finish a game, new
game, exit).

CI uses SDL's dummy video driver, so it does not prove a window opens on a
real desktop. For each release candidate, a person repeats the smoke steps
by hand on each OS with a real display: launch with
`python -m snakes_ladders.main`, set up two players, take three turns,
finish a game, start a new game, and exit. The save, exit and resume steps
of TC-N05-1 are added once FR-15 exists.

## Offline availability (NFR-04)

The application has no network service dependency. `tests/test_availability.py`
scans application imports for networking modules and launches the real app
while Python socket creation, connection and DNS APIs are blocked. The test
verifies that the setup screen is drawn and runs in CI on Windows, Ubuntu and
macOS. For release acceptance, also repeat the launch and gameplay smoke test
with the network adapter disabled on each supported OS; the automated socket
trap does not replace OS-level network tracing.

## Four-player scalability (NFR-07)

The same performance check runs separately with two and four players, with
50 roll inputs per configuration and the same one-second limit for every
sample. Both keyboard and mouse inputs run through the actual application
event loop. Each presented frame is checked for a newly executed roll,
correct turn order, the visible dice result and all players' tokens.
Run `python -m pytest tests/test_roll_performance.py -q -s` to print both
timing reports. No relative speed threshold replaces the one-second limit.
Repeat this check on the SRS 2.4 minimum hardware for hardware acceptance;
headless cloud results validate the workflow on the current machine only.

## Save interruption recovery (NFR-11)

Saves are written to a temporary file in the save directory, flushed and synced,
then committed with `os.replace`. Closing the application before that replacement
preserves the previous valid save. Resume ignores leftover temporary files; the
next successful save replaces them. After replacement, the new save is committed.

`tests/test_recoverability.py` abruptly terminates ten child processes during
partial writes, after flushing, and just before replacement. Each run verifies
that the old save is byte-identical, resumes correctly, and can be saved again.
It also injects ten write failures immediately before replacement.

## Resource efficiency (NFR-14)

Save files are limited to 10 KiB (10,240 bytes) before any temporary file is
written. Run `python -m pytest tests/test_resource_efficiency.py -q` to check
the largest valid four-player save, oversized-save rejection, and process RSS
during 300 rendered gameplay frames. The test uses `psutil` and gates peak
resident memory at 200 MB.

For release acceptance, sample the standalone application's working set at
one-second intervals for 30 minutes, including four-player games and 10
save/resume cycles, using the OS task manager or an equivalent process monitor.
The peak must remain at or below 200 MB; also verify the resulting
`savegame.json` is at most 10,240 bytes. The automated test is a regression
check, not a substitute for this full-duration run on target hardware.

## Display compatibility (NFR-09)

The window can be resized from the minimum 1280 x 720 up to 1920 x 1080.
Setup, gameplay and results share a logical 1280 x 720 canvas, scaled
uniformly to fit the window without cropping or stretching. Different
aspect ratios leave centred margins. Mouse positions are mapped back to
the logical controls; clicks in margins are ignored. Text entry retains
the full buffer and shows an ellipsis preview when pasted text exceeds
the name field's width.

Run `python -m pytest tests/test_resolution_compatibility.py -q` to check
1280x720, 1366x768 and 1920x1080. Tests render all screens with four
maximum-length player names, check text bounds and overlap, and exercise
resized mouse input through setup, rolling, results and New Game. PNGs
for visual inspection are written to pytest's temporary directory (use
`--basetemp=/tmp/nfr09-validation` for a predictable location). The screens
were visually inspected at all three sizes in headless SDL; native desktop
window-manager behaviour remains a manual check on each supported OS.

## Responsiveness (NFR-12)

Token moves are animated over 0.3 s at up to 60 frames per second. Position is
computed from elapsed time, so a slow frame makes the movement coarser but never
longer. `tests/test_token_animation.py` checks the path, the snake and ladder
slides, and input blocking while a token moves. It also plays 20 moves through
the real application loop, logs the frame rate of each, and requires the
average over all 20 to be at least 30 FPS. The average is used deliberately: a
single stalled frame on a shared CI machine does not show the game renders
below 30 FPS. Cloud timings do not certify the SRS 2.4 minimum hardware; repeat
`python -m pytest tests/test_token_animation.py -q -s` there.
