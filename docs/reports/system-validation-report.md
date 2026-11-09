# System validation report

- Date: 2026-11-09
- Commit: c07ddfc on branch docs-reports
- Python 3.12.4 on Windows-11-10.0.26300-SP0
- Pygame 2.6.1, run headless (SDL dummy video and audio drivers)
- Command: `python scripts/generate_reports.py`

System validation drives whole screens or the real application loop. These tests render the setup, game and result screens, play moves through `main()`, and measure the non-functional requirements end to end. They run headless, so they do not replace the manual checks listed below.

## Automated results

| Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|
| 153 | 153 | 0 | 0 | 28.7 |

| File | Tests | Passed | Failed | Skipped | Time (s) | Requirements cited |
|---|---|---|---|---|---|---|
| `tests/test_accessibility.py` | 12 | 12 | 0 | 0 | 1.0 | NFR-13 |
| `tests/test_availability.py` | 2 | 2 | 0 | 0 | 0.3 | NFR-04, SEC-06 |
| `tests/test_board_view.py` | 5 | 5 | 0 | 0 | 0.7 | none cited |
| `tests/test_error_handling.py` | 23 | 23 | 0 | 0 | 2.5 | NFR-10 |
| `tests/test_exit.py` | 11 | 11 | 0 | 0 | 1.2 | FR-18 |
| `tests/test_invalid_actions.py` | 8 | 8 | 0 | 0 | 0.3 | FR-17 |
| `tests/test_portability.py` | 31 | 31 | 0 | 0 | 0.7 | NFR-05 |
| `tests/test_resolution_compatibility.py` | 8 | 8 | 0 | 0 | 2.4 | NFR-09 |
| `tests/test_resource_efficiency.py` | 3 | 3 | 0 | 0 | 1.3 | NFR-14 |
| `tests/test_restart.py` | 6 | 6 | 0 | 0 | 0.7 | FR-14 |
| `tests/test_roll_performance.py` | 2 | 2 | 0 | 0 | 2.1 | NFR-01, NFR-07 |
| `tests/test_save_resume.py` | 7 | 7 | 0 | 0 | 0.4 | FR-15, NFR-08, NFR-11 |
| `tests/test_setup_screen.py` | 6 | 6 | 0 | 0 | 0.9 | none cited |
| `tests/test_token_animation.py` | 16 | 16 | 0 | 0 | 10.0 | FR-13, FR-17, NFR-12 |
| `tests/test_turn_indicator.py` | 6 | 6 | 0 | 0 | 1.1 | FR-12 |
| `tests/test_usability.py` | 7 | 7 | 0 | 0 | 3.2 | NFR-02 |

### Failures

None.

## Manual and hardware checks

Nobody has run these yet. They need a person, a real display or the minimum-hardware machine named in the Test Plan.

| Requirements | Check | Status | Where it is defined |
|---|---|---|---|
| NFR-02 | Usability study with five first-time users | Not run | docs/USABILITY_STUDY.md |
| NFR-01, NFR-07 | Roll-to-display time on the reference machine (2 and 4 players) | Not run | Test Plan TC-N01-1, TC-N07-1 |
| NFR-12 | Animation frame rate on the reference machine | Not run | Test Plan TC-N12-1 |
| NFR-14 | Peak memory over a 30-minute session on the reference machine | Not run | Test Plan TC-N14-1 |
| NFR-05 | Smoke run on a real display on Windows, Ubuntu and macOS | Not run | Test Plan TC-N05-1 |
| NFR-09 | Visual check of native windows at 1280x720, 1366x768 and 1920x1080 | Not run | Test Plan TC-N09-1 |

## Test Plan execution

The Test Plan has 123 cases. A case counts as run when an automated test cites its ID.

| Status | Cases |
|---|---|
| Automated part passed; manual part not run | 9 |
| No automated test cites this ID | 38 |
| Not run (manual) | 31 |
| Passed | 45 |

| Case | Procedure | Level | Requirement | Status |
|---|---|---|---|---|
| TC-SEC01-1 | In Setup enter names of 1 character (`A`) and 15 characters (`ABCDEFGH | Ua, Sm | SEC-01 | No automated test cites this ID |
| TC-SEC01-2 | Enter each of: `Bob!`, `Al_ice`, `a-b`, `<b>x</b>`, `x;y`, `../a`, `é` | Ua | SEC-01 | No automated test cites this ID |
| TC-SEC01-3 | Enter `"   "` (spaces only), `" Sam "` and `"Player 1"` | Ua | SEC-01, FR-02 | No automated test cites this ID |
| TC-SEC01-4 | Fuzz the validator with 10,000 random strings from the whole Unicode r | Ua, Sm | SEC-01, NFR-10 | No automated test cites this ID |
| TC-SEC01-5 | Save factory builds otherwise valid files (correct checksum) whose pla | Ia | SEC-01, SEC-03 | No automated test cites this ID |
| TC-SEC02-1 | Save through the UI, leave the file untouched, press Resume | Ia | SEC-02, FR-15 | Passed |
| TC-SEC02-2 | Edit `position`, `current_index` or `extra_turn_enabled` inside `state | Ia | SEC-02 | Passed |
| TC-SEC02-3 | Damage the `checksum` field: flip one hex digit; cut it to 63 characte | Ua | SEC-02 | Passed |
| TC-SEC02-4 | Re-format a valid save without changing any value: other indentation,  | Ua | SEC-02, NFR-08 | Passed |
| TC-SEC02-5 | Trigger E-06, E-07, E-08 and E-09 in turn (oversize, bad JSON, out-of- | Ia | SEC-02, SEC-03 | Passed |
| TC-SEC02-6 | Informational. Change `position` of a valid save, recompute the SHA-25 | Ia | SEC-02, SO-1 | Passed |
| TC-SEC03-1 | Pad a valid save with insignificant whitespace to exactly 10,240 bytes | Ia | SEC-03, NFR-14 | Passed |
| TC-SEC03-2 | Files that are not valid JSON documents: 0 bytes, spaces only, truncat | Ua | SEC-03, NFR-10 | Passed |
| TC-SEC03-3 | Parser stress within 10 KB: about 10,000 nested `[`; a 5,000-digit int | Ua | SEC-03, SEC-05, NFR-10 | Passed |
| TC-SEC03-4 | Schema and type violations (checksum recomputed): missing `version`, ` | Ua | SEC-03 | Passed |
| TC-SEC03-5 | Range violations (checksum recomputed): 1 player; 5 players; `position | Ua | SEC-03 | Passed |
| TC-SEC03-6 | After each rejection above, check the hash of the file on disk, whethe | Ia, Sm | SEC-03 | No automated test cites this ID |
| TC-SEC03-7 | Files with two problems: oversize and malformed; bad schema and bad ch | Ia | SEC-03 | Passed |
| TC-SEC03-8 | Hostile file-system states for `savegame.json`: it is a directory; it  | Ia | SEC-03, NFR-10 | No automated test cites this ID |
| TC-SEC04-1 | Inspect the public API with `inspect`: signature of `GameEngine.roll_a | Ua | SEC-04 | No automated test cites this ID |
| TC-SEC04-2 | During a real game press the digits 1 to 6, numpad keys, Enter, arrow  | Sm | SEC-04, FR-03 | Not run (manual) |
| TC-SEC04-3 | Save factory files (correct checksum) with an extra key such as `next_ | Ia | SEC-04, SEC-03 | No automated test cites this ID |
| TC-SEC04-4 | Start the production entry point with `--seed 1`, with `SNL_SEED=1` an | Sa | SEC-04, SO-2 | No automated test cites this ID |
| TC-SEC04-5 | Static check over all non-test code: `engine/dice.py` uses `secrets.Sy | Ua | SEC-04, NFR-15 | Passed |
| TC-SEC04-6 | Take 60,000 rolls from the production `DiceService`, split them into 3 | Ua | SEC-04, NFR-15 | Passed |
| TC-SEC05-1 | Scan all non-test code with `grep` and with an AST walker for `eval`,  | Ua | SEC-05 | Passed |
| TC-SEC05-2 | Place hostile content in `savegame.json`: (a) a valid-checksum file wh | Ia | SEC-05, SEC-03 | Passed |
| TC-SEC05-3 | Review `SaveManager.load` against a checklist: only `json.load` or `js | Um | SEC-05 | Not run (manual) |
| TC-SEC06-1 | Scan all project source for imports of `socket`, `urllib`, `http`, `re | Ua | SEC-06, SO-4 | No automated test cites this ID |
| TC-SEC06-2 | Patch `socket.socket`, `socket.create_connection` and `socket.getaddri | Ia | SEC-06 | No automated test cites this ID |
| TC-SEC06-3 | Run a 5-minute session under an OS-level trace: `strace -f -e trace=ne | Sm | SEC-06, NFR-04 | Not run (manual) |
| TC-SECX-1 | Trace file-system activity through a full session (`strace -e trace=fi | Sm | SO-1, SO-3 | Not run (manual) |
| TC-SECX-2 | Fault injection: make an engine call raise `EngineInvariantError`, the | Ia | NFR-10, SO-3 | No automated test cites this ID |
| TC-FR01-1 | Open Setup with 0 valid players, then 1 valid player | Sm | FR-01 | Not run (manual) |
| TC-FR01-2 | Configure 2 valid players and click Start | Sm | FR-01 | Not run (manual) |
| TC-FR01-3 | Configure 4 valid players and start. At engine level call `new_game` w | Sm, Ua | FR-01 | No automated test cites this ID |
| TC-FR02-1 | Leave one name empty in a 2-player setup | Sm, Ua | FR-02, SEC-01 | No automated test cites this ID |
| TC-FR02-2 | Give two players the name `Asha`; then `Sam` and `sam` | Ua | FR-02 | No automated test cites this ID |
| TC-FR02-3 | Give two players the same token colour | Ua, Sm | FR-02 | No automated test cites this ID |
| TC-FR02-4 | Enter four distinct names and four distinct colours | Sm | FR-02, NFR-13 | Not run (manual) |
| TC-FR03-1 | Scripted RNG returns 4. Click Roll Dice | Ia | FR-03 | Passed |
| TC-FR03-2 | Scripted RNG returns 5. Press the Space key | Ia, Sm | FR-03, SRS 3.1.2 | Automated part passed; manual part not run |
| TC-FR03-3 | Take 6,000 rolls from the production `DiceService` | Ua | FR-03 | Passed |
| TC-FR04-1 | Token at 0, roll 3 | Ua | FR-04 | Passed |
| TC-FR04-2 | Token at 10, roll 5 | Ua | FR-04 | Passed |
| TC-FR04-3 | One token, rolls 6, 5, 2 from position 0 (extra-turn off) | Ua | FR-04 | Passed |
| TC-FR05-1 | 3 players, extra-turn off, rolls 2, 3, 5, then 2 more | Ua | FR-05 | Passed |
| TC-FR05-2 | 4 players, 8 consecutive moves on plain squares (rolls 2,2,2,2,3,3,3,3 | Ia, Sm | FR-05, FR-12 | Automated part passed; manual part not run |
| TC-FR05-3 | In a 3-player game roll once and compare all three positions before an | Ua | FR-05 | No automated test cites this ID |
| TC-FR06-1 | Token at 14, roll 3 (lands on 17, a snake head) | Ua, Sm | FR-06 | Automated part passed; manual part not run |
| TC-FR06-2 | Data-driven over all 8 snakes, each from head minus 1 with roll 1: 16  | Ua | FR-06 | Passed |
| TC-FR06-3 | Token at 2, roll 5 (lands on 7, a snake tail) | Ua | FR-06 | Passed |
| TC-FR07-1 | Token at 0, roll 4 (lands on 4, a ladder base) | Ua, Sm | FR-07 | Automated part passed; manual part not run |
| TC-FR07-2 | Data-driven over all 8 ladders, each from base minus 1 with roll 1 (fr | Ua | FR-07 | Passed |
| TC-FR07-3 | Token at 38, roll 4 (lands on 42, the top of ladder 21 to 42) | Ua | FR-07 | Passed |
| TC-FR08-1 | Extra-turn on. P1 from 0 rolls 6 then 2 | Ua | FR-08 | Passed |
| TC-FR08-2 | Extra-turn on. P1 rolls 6, 6, 6 (positions 6, 12, 18). Then P2 rolls 6 | Ua | FR-08 | Passed |
| TC-FR08-3 | Extra-turn on. Roll 4 | Ua | FR-08 | Passed |
| TC-FR08-4 | Extra-turn off. Roll 6 | Ua, Ia | FR-08, FR-15 | Passed |
| TC-FR08-5 | Extra-turn on. Token at 11, roll 6 (lands on snake head 17) | Ua | FR-08, FR-06 | Passed |
| TC-FR08-6 | Extra-turn on. Token at 97, roll 6 (overshoot) | Ua | FR-08, FR-10 | Passed |
| TC-FR08-7 | Extra-turn on. Token at 94, roll 6 (reaches 100) | Ua | FR-08, FR-09 | Passed |
| TC-FR09-1 | Token at 94, roll 6. Watch the UI | Ia, Sm | FR-09 | Automated part passed; manual part not run |
| TC-FR09-2 | Token at 99, roll 1 | Ua | FR-09 | Passed |
| TC-FR09-3 | Token at 79, roll 1 (ladder 80 to 99) | Ua | FR-09, FR-07 | Passed |
| TC-FR10-1 | Token at 97, roll 4 (would be 101) | Ua | FR-10 | Passed |
| TC-FR10-2 | Token at 99, roll 2. Watch the UI | Ua, Sm | FR-10 | Automated part passed; manual part not run |
| TC-FR10-3 | Token at 96, roll 4 (exactly 100) | Ua | FR-10, FR-09 | Passed |
| TC-FR11-1 | Call `BoardRenderer` square-to-pixel mapping headless for all 100 squa | Ua | FR-11 | No automated test cites this ID |
| TC-FR11-2 | Compare a screenshot of the Game screen with SRS 4.3 | Sm | FR-11 | Not run (manual) |
| TC-FR11-3 | Put 4 tokens on one square, and put tokens on snake and ladder squares | Sm | FR-11 | Not run (manual) |
| TC-FR12-1 | Start a game and play 6 moves including one extra roll | Sm | FR-12 | Not run (manual) |
| TC-FR12-2 | Observe the indicator during animation and after a Resume | Sm | FR-12, FR-15 | Not run (manual) |
| TC-FR13-1 | Time 20 moves from dice value shown to final token square drawn, inclu | Sa | FR-13, NFR-01 | No automated test cites this ID |
| TC-FR13-2 | Over 100 scripted moves compare the square drawn by the renderer with  | Ia | FR-13 | No automated test cites this ID |
| TC-UI1-1 | Open the Setup screen | Sm | UI-1 | Not run (manual) |
| TC-UI2-1 | Open the Game screen | Sm | UI-2 | Not run (manual) |
| TC-UI3-1 | Finish a game | Sm | UI-3 | Not run (manual) |
| TC-FR14-1 | Click Restart on the Game screen, then Cancel | Sm | FR-14 | Not run (manual) |
| TC-FR14-2 | Click Restart, then Confirm | Sm | FR-14 | Not run (manual) |
| TC-FR14-3 | On the Result screen click New Game | Sm | FR-14 | Not run (manual) |
| TC-FR15-1 | 3 players at positions 12, 37 and 0, P3 to move, extra-turn on, last r | Sm | FR-15, NFR-08 | Automated part passed; manual part not run |
| TC-FR15-2 | Save while an extra roll is pending (after a 6, `extra_rolls_used` 1), | Ia | FR-15, FR-08 | Passed |
| TC-FR15-3 | Save twice with different states, then Resume | Ia | FR-15 | Passed |
| TC-FR15-4 | Save a game with extra-turn off; resume; roll a 6 | Ia | FR-15, FR-08 | Passed |
| TC-FR15-5 | Save at the start of a game (all positions 0) and again with a player  | Ia | FR-15 | Passed |
| TC-FR16-1 | Finish a game with positions 100, 45, 60, 12 | Ua, Sm | FR-16 | No automated test cites this ID |
| TC-FR16-2 | Two players tied at 45 | Ua | FR-16 | No automated test cites this ID |
| TC-FR16-3 | Finish a 2-player, a 3-player and a 4-player game | Sm | FR-16 | Not run (manual) |
| TC-FR17-1 | Press Space 10 times quickly while a token is animating. Count scripte | Ia | FR-17 | No automated test cites this ID |
| TC-FR17-2 | After a win call `on_roll_requested()` and press Space on the Result s | Ia | FR-17 | No automated test cites this ID |
| TC-FR17-3 | Call `on_save_requested()` and click Save while a move is animating | Ia, Sm | FR-17 | No automated test cites this ID |
| TC-FR17-4 | Look at the Roll Dice and Save buttons during animation and after game | Sm | FR-17 | Not run (manual) |
| TC-FR17-5 | Run the ignored actions above and read the log | Ia | FR-17 | No automated test cites this ID |
| TC-FR18-1 | Click Exit during a game | Sm | FR-18 | Not run (manual) |
| TC-FR18-2 | Choose Save in the prompt | Sm | FR-18, FR-15 | Not run (manual) |
| TC-FR18-3 | Choose Exit without saving | Sm | FR-18 | Not run (manual) |
| TC-FR18-4 | Choose Cancel | Sm | FR-18 | Not run (manual) |
| TC-FR18-5 | Exit from the Start, Setup and Result screens; also close the window ( | Sm | FR-18 | Not run (manual) |
| TC-FR18-6 | Request Exit while a token is animating | Sm | FR-18, FR-17 | Not run (manual) |
| TC-UI4-1 | Open the Start screen with no save file; save a game and return; delet | Sm, Ia | UI-4 | No automated test cites this ID |
| TC-HW-1 | Play a complete game using only the mouse (names typed on the keyboard | Sm | SRS 3.1.2 | Not run (manual) |
| TC-C1-1 | Inspect `requirements.txt` and run the suite on Python 3.10 and on the | Um, Sa | C1, SRS 3.1.3 | No automated test cites this ID |
| TC-C3-1 | Open a saved file with an independent tool (`python -m json.tool`, `jq | Ua | C3, SRS 3.1.3 | No automated test cites this ID |
| TC-BRD-1 | Validate the `Board` data against SRS 4.3 | Ua | A3, FR-06, FR-07 | Passed |
| TC-N01-1 | On the minimum-hardware reference machine, 2 players, log the time fro | Sa | NFR-01 | No automated test cites this ID |
| TC-N02-1 | 5 first-time users, no help: set up a 2-player game and complete one f | Am | NFR-02 | Not run (manual) |
| TC-N03-1 | Play 100 automated full games with the production RNG through the cont | Ia | NFR-03 | Passed |
| TC-N04-1 | On each of the 3 operating systems disable the network (airplane mode  | Sm | NFR-04, C2 | Not run (manual) |
| TC-N05-1 | Run the same source tree on Windows 10/11, Ubuntu 22.04+ and macOS 13+ | Sm | NFR-05 | Automated part passed; manual part not run |
| TC-N06-1 | Run `coverage run -m pytest tests/engine tests/persistence tests/contr | Ua | NFR-06 | No automated test cites this ID |
| TC-N06-2 | AST scan of `engine/` for Pygame imports; also run the engine tests wi | Ua | NFR-06, C4 | No automated test cites this ID |
| TC-N07-1 | Repeat TC-N01-1 with 4 players | Sa | NFR-07 | No automated test cites this ID |
| TC-N08-1 | `tests/test_data_integrity.py`: 20 save and resume cycles over varied  | Ia | NFR-08 | No automated test cites this ID |
| TC-N09-1 | Check the Start, Setup, Game and Result screens at 1280 x 720, 1366 x  | Sm | NFR-09 | Not run (manual) |
| TC-N10-1 | Fault matrix: missing save file, 0-byte file, corrupted file, non-UTF- | Ia, Sm | NFR-10, A4 | No automated test cites this ID |
| TC-N11-1 | Interrupt a save 10 times: kill the process at random moments, and inj | Ia, Sm | NFR-11 | Automated part passed; manual part not run |
| TC-N12-1 | Log frame times during 20 moves (including long snake and ladder moves | Sa | NFR-12 | Passed |
| TC-N13-1 | Audit every text element at 1280 x 720 | Um | NFR-13 | Not run (manual) |
| TC-N13-2 | Take screenshots of the Game screen and run them through protanopia, d | Um | NFR-13 | Not run (manual) |
| TC-N14-1 | CI samples process RSS during 300 rendered gameplay frames; for releas | Sa | NFR-14 | No automated test cites this ID |
| TC-N14-2 | Save the largest possible state (4 players, longest allowed names), ch | Ua | NFR-14 | No automated test cites this ID |
| TC-N15-1 | Take 60,000 rolls from the production `DiceService` and count each val | Ua | NFR-15 | Passed |
