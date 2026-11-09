# System validation report

- Date: 2026-11-10
- Commit: 38dab5f on branch test-plan-sync
- Python 3.12.4 on Windows-11-10.0.26300-SP0
- Pygame 2.6.1, run headless (SDL dummy video and audio drivers)
- Command: `python scripts/generate_reports.py`

System validation drives whole screens or the real application loop. These tests render the setup, game and result screens, play moves through `main()`, and measure the non-functional requirements end to end. They run headless, so they do not replace the manual checks listed below.

## Automated results

| Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|
| 177 | 176 | 0 | 1 | 34.6 |

| File | Tests | Passed | Failed | Skipped | Time (s) | Requirements cited |
|---|---|---|---|---|---|---|
| `tests/test_accessibility.py` | 12 | 12 | 0 | 0 | 1.0 | NFR-13 |
| `tests/test_availability.py` | 2 | 2 | 0 | 0 | 0.3 | NFR-04, SEC-06 |
| `tests/test_board_view.py` | 5 | 5 | 0 | 0 | 0.7 | none cited |
| `tests/test_error_handling.py` | 23 | 23 | 0 | 0 | 2.6 | NFR-10 |
| `tests/test_exit.py` | 11 | 11 | 0 | 0 | 1.3 | FR-18 |
| `tests/test_invalid_actions.py` | 8 | 8 | 0 | 0 | 0.4 | FR-17 |
| `tests/test_plan_gaps.py` | 24 | 23 | 0 | 1 | 5.3 | FR-17, NFR-06, SEC-01, SEC-03, SEC-04, SEC-06 |
| `tests/test_portability.py` | 31 | 31 | 0 | 0 | 0.7 | NFR-05 |
| `tests/test_resolution_compatibility.py` | 8 | 8 | 0 | 0 | 2.5 | NFR-09 |
| `tests/test_resource_efficiency.py` | 3 | 3 | 0 | 0 | 1.6 | NFR-14 |
| `tests/test_restart.py` | 6 | 6 | 0 | 0 | 0.8 | FR-14 |
| `tests/test_roll_performance.py` | 2 | 2 | 0 | 0 | 2.1 | NFR-01, NFR-07 |
| `tests/test_save_resume.py` | 7 | 7 | 0 | 0 | 0.3 | FR-15, NFR-08, NFR-11 |
| `tests/test_setup_screen.py` | 6 | 6 | 0 | 0 | 0.9 | none cited |
| `tests/test_token_animation.py` | 16 | 16 | 0 | 0 | 10.1 | FR-13, FR-17, NFR-12 |
| `tests/test_turn_indicator.py` | 6 | 6 | 0 | 0 | 0.8 | FR-12 |
| `tests/test_usability.py` | 7 | 7 | 0 | 0 | 3.1 | NFR-02 |

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

The Test Plan has 126 cases. A case counts as run when an automated test cites its ID, or when `scripts/test_case_map.json` names a test for it. The generator checks that every named test exists and did not fail.

| Status | Cases |
|---|---|
| Automated part passed; manual part not run | 46 |
| Not run (manual) | 9 |
| Passed | 71 |

| Case | Procedure | Level | Requirement | Status | Evidence |
|---|---|---|---|---|---|
| TC-SEC01-1 | In Setup enter names of 1 character (`A`) and 15 characters (`ABCDEFGH | Ua, Sm | SEC-01 | Automated part passed; manual part not run | `test_player_setup.py::test_valid_names_normalized`; `test_player_setup.py::test_invalid_names_rejected` |
| TC-SEC01-2 | Enter each of: `Bob!`, `Al_ice`, `a-b`, `<b>x</b>`, `x;y`, `../a`, `é` | Ua | SEC-01 | Passed | `test_plan_gaps.py`; `test_player_setup.py::test_invalid_names_rejected` |
| TC-SEC01-3 | Enter `"   "` (spaces only), `" Sam "` and `"Player 1"` | Ua | SEC-01, FR-02 | Passed | `test_player_setup.py::test_invalid_names_rejected`; `test_player_setup.py::test_valid_names_normalized` |
| TC-SEC01-4 | Fuzz the validator with 10,000 random strings from the whole Unicode r | Ua, Sm | SEC-01, NFR-10 | Automated part passed; manual part not run | `test_plan_gaps.py` |
| TC-SEC01-5 | Save factory builds otherwise valid files (correct checksum) whose pla | Ia | SEC-01, SEC-03 | Passed | `test_plan_gaps.py`; `test_save_security.py::test_tc_sec03_5_range_violations`; empty and 16-character names |
| TC-SEC02-1 | Save through the UI, leave the file untouched, press Resume | Ia | SEC-02, FR-15 | Passed | `test_save_security.py` |
| TC-SEC02-2 | Edit `position`, `current_index` or `extra_turn_enabled` inside `state | Ia | SEC-02 | Passed | `test_save_security.py` |
| TC-SEC02-3 | Damage the `checksum` field: flip one hex digit; cut it to 63 characte | Ua | SEC-02 | Passed | `test_save_security.py` |
| TC-SEC02-4 | Re-format a valid save without changing any value: other indentation,  | Ua | SEC-02, NFR-08 | Passed | `test_save_security.py` |
| TC-SEC02-5 | Trigger E-06, E-07, E-08 and E-09 in turn (oversize, bad JSON, out-of- | Ia | SEC-02, SEC-03 | Passed | `test_save_security.py` |
| TC-SEC02-6 | Informational. Change `position` of a valid save, recompute the SHA-25 | Ia | SEC-02, SO-1 | Passed | `test_save_security.py` |
| TC-SEC03-1 | Pad a valid save with insignificant whitespace to exactly 10,240 bytes | Ia | SEC-03, NFR-14 | Passed | `test_save_security.py` |
| TC-SEC03-2 | Files that are not valid JSON documents: 0 bytes, spaces only, truncat | Ua | SEC-03, NFR-10 | Passed | `test_save_security.py` |
| TC-SEC03-3 | Parser stress within 10 KB: about 10,000 nested `[`; a 5,000-digit int | Ua | SEC-03, SEC-05, NFR-10 | Passed | `test_save_security.py` |
| TC-SEC03-4 | Schema and type violations (checksum recomputed): missing `version`, ` | Ua | SEC-03 | Passed | `test_save_security.py` |
| TC-SEC03-5 | Range violations (checksum recomputed): 1 player; 5 players; `position | Ua | SEC-03 | Passed | `test_save_security.py` |
| TC-SEC03-6 | After each rejection above, check the hash of the file on disk, whethe | Ia, Sm | SEC-03 | Automated part passed; manual part not run | `test_plan_gaps.py` |
| TC-SEC03-7 | Files with two problems: oversize and malformed; bad schema and bad ch | Ia | SEC-03 | Passed | `test_save_security.py` |
| TC-SEC03-8 | Hostile file-system states for `savegame.json`: it is a directory; it  | Ia | SEC-03, NFR-10 | Passed | `test_plan_gaps.py`; `test_error_handling.py::test_save_read_permission_failure_is_reported`; unreadable file |
| TC-SEC04-1 | Inspect the public API with `inspect`: signature of `GameEngine.roll_a | Ua | SEC-04 | Passed | `test_plan_gaps.py` |
| TC-SEC04-2 | During a real game press the digits 1 to 6, numpad keys, Enter, arrow  | Sm | SEC-04, FR-03 | Not run (manual) | none |
| TC-SEC04-3 | Save factory files (correct checksum) with an extra key such as `next_ | Ia | SEC-04, SEC-03 | Passed | `test_plan_gaps.py`; `test_save_security.py::test_tc_sec03_4_schema_and_type_violations`; extra keys |
| TC-SEC04-4 | Start the production entry point with `--seed 1`, with `SNL_SEED=1` an | Sa | SEC-04, SO-2 | Passed | `test_plan_gaps.py` |
| TC-SEC04-5 | Static check over all non-test code: `engine/dice.py` uses `secrets.Sy | Ua | SEC-04, NFR-15 | Passed | `test_randomness.py` |
| TC-SEC04-6 | Take 60,000 rolls from the production `DiceService`, split them into 3 | Ua | SEC-04, NFR-15 | Passed | `test_randomness.py` |
| TC-SEC05-1 | Scan all non-test code with `grep` and with an AST walker for `eval`,  | Ua | SEC-05 | Passed | `test_save_security.py` |
| TC-SEC05-2 | Place hostile content in `savegame.json`: (a) a valid-checksum file wh | Ia | SEC-05, SEC-03 | Passed | `test_save_security.py` |
| TC-SEC05-3 | Review `SaveManager.load` against a checklist: only `json.load` or `js | Um | SEC-05 | Not run (manual) | none |
| TC-SEC06-1 | Scan all project source for imports of `socket`, `urllib`, `http`, `re | Ua | SEC-06, SO-4 | Passed | `test_availability.py::test_application_does_not_import_network_modules` |
| TC-SEC06-2 | Patch `socket.socket`, `socket.create_connection` and `socket.getaddri | Ia | SEC-06 | Passed | `test_plan_gaps.py` |
| TC-SEC06-3 | Run a 5-minute session under an OS-level trace: `strace -f -e trace=ne | Sm | SEC-06, NFR-04 | Not run (manual) | none |
| TC-SECX-1 | Trace file-system activity through a full session (`strace -e trace=fi | Sm | SO-1, SO-3 | Not run (manual) | none |
| TC-SECX-2 | Fault injection: make an engine call raise `EngineInvariantError`, the | Ia | NFR-10, SO-3 | Passed | `test_error_handling.py::test_real_loop_recovers_logs_traceback_and_can_start_again` |
| TC-FR01-1 | Open Setup with 0 valid players, then 1 valid player | Sm | FR-01 | Automated part passed; manual part not run | `test_setup_screen.py::test_start_ignores_incomplete_setup_then_starts_valid_players` |
| TC-FR01-2 | Configure 2 valid players and click Start | Sm | FR-01 | Automated part passed; manual part not run | `test_setup_screen.py::test_start_ignores_incomplete_setup_then_starts_valid_players` |
| TC-FR01-3 | Configure 4 valid players and start. At engine level call `new_game` w | Sm, Ua | FR-01 | Automated part passed; manual part not run | `test_initialization.py::test_invalid_count_rejected_by_engine_and_controller`; `test_setup_screen.py::test_four_player_selection_starts_all_players` |
| TC-FR02-1 | Leave one name empty in a 2-player setup | Sm, Ua | FR-02, SEC-01 | Automated part passed; manual part not run | `test_player_setup.py::test_invalid_names_rejected` |
| TC-FR02-2 | Give two players the name `Asha`; then `Sam` and `sam` | Ua | FR-02 | Passed | `test_player_setup.py::test_duplicate_or_unsupported_player_details_rejected` |
| TC-FR02-3 | Give two players the same token colour | Ua, Sm | FR-02 | Automated part passed; manual part not run | `test_player_setup.py::test_duplicate_or_unsupported_player_details_rejected` |
| TC-FR02-4 | Enter four distinct names and four distinct colours | Sm | FR-02, NFR-13 | Automated part passed; manual part not run | `test_setup_screen.py::test_edit_names_and_change_colours`; `test_setup_screen.py::test_four_player_selection_starts_all_players` |
| TC-FR03-1 | Scripted RNG returns 4. Click Roll Dice | Ia | FR-03 | Passed | `test_dice.py` |
| TC-FR03-2 | Scripted RNG returns 5. Press the Space key | Ia, Sm | FR-03, SRS 3.1.2 | Automated part passed; manual part not run | `test_dice.py` |
| TC-FR03-3 | Take 6,000 rolls from the production `DiceService` | Ua | FR-03 | Passed | `test_dice.py` |
| TC-FR04-1 | Token at 0, roll 3 | Ua | FR-04 | Passed | `test_movement.py` |
| TC-FR04-2 | Token at 10, roll 5 | Ua | FR-04 | Passed | `test_movement.py` |
| TC-FR04-3 | One token, rolls 6, 5, 2 from position 0 (extra-turn off) | Ua | FR-04 | Passed | `test_movement.py` |
| TC-FR05-1 | 3 players, extra-turn off, rolls 2, 3, 5, then 2 more | Ua | FR-05 | Passed | `test_turns.py` |
| TC-FR05-2 | 4 players, 8 consecutive moves on plain squares (rolls 2,2,2,2,3,3,3,3 | Ia, Sm | FR-05, FR-12 | Automated part passed; manual part not run | `test_turns.py` |
| TC-FR05-3 | In a 3-player game roll once and compare all three positions before an | Ua | FR-05 | Passed | `test_movement.py::test_only_current_player_moves` |
| TC-FR06-1 | Token at 14, roll 3 (lands on 17, a snake head) | Ua, Sm | FR-06 | Automated part passed; manual part not run | `test_snakes.py`; `test_token_animation.py` |
| TC-FR06-2 | Data-driven over all 8 snakes, each from head minus 1 with roll 1: 16  | Ua | FR-06 | Passed | `test_snakes.py` |
| TC-FR06-3 | Token at 2, roll 5 (lands on 7, a snake tail) | Ua | FR-06 | Passed | `test_snakes.py` |
| TC-FR07-1 | Token at 0, roll 4 (lands on 4, a ladder base) | Ua, Sm | FR-07 | Automated part passed; manual part not run | `test_ladders.py` |
| TC-FR07-2 | Data-driven over all 8 ladders, each from base minus 1 with roll 1 (fr | Ua | FR-07 | Passed | `test_ladders.py` |
| TC-FR07-3 | Token at 38, roll 4 (lands on 42, the top of ladder 21 to 42) | Ua | FR-07 | Passed | `test_ladders.py` |
| TC-FR08-1 | Extra-turn on. P1 from 0 rolls 6 then 2 | Ua | FR-08 | Passed | `test_extra_turn.py` |
| TC-FR08-2 | Extra-turn on. P1 rolls 6, 6, 6 (positions 6, 12, 18). Then P2 rolls 6 | Ua | FR-08 | Passed | `test_extra_turn.py` |
| TC-FR08-3 | Extra-turn on. Roll 4 | Ua | FR-08 | Passed | `test_extra_turn.py` |
| TC-FR08-4 | Extra-turn off. Roll 6 | Ua, Ia | FR-08, FR-15 | Passed | `test_extra_turn.py` |
| TC-FR08-5 | Extra-turn on. Token at 11, roll 6 (lands on snake head 17) | Ua | FR-08, FR-06 | Passed | `test_extra_turn.py` |
| TC-FR08-6 | Extra-turn on. Token at 97, roll 6 (overshoot) | Ua | FR-08, FR-10 | Passed | `test_extra_turn.py` |
| TC-FR08-7 | Extra-turn on. Token at 94, roll 6 (reaches 100) | Ua | FR-08, FR-09 | Passed | `test_extra_turn.py` |
| TC-FR09-1 | Token at 94, roll 6. Watch the UI | Ia, Sm | FR-09 | Automated part passed; manual part not run | `test_win.py` |
| TC-FR09-2 | Token at 99, roll 1 | Ua | FR-09 | Passed | `test_win.py` |
| TC-FR09-3 | Token at 79, roll 1 (ladder 80 to 99) | Ua | FR-09, FR-07 | Passed | `test_win.py` |
| TC-FR10-1 | Token at 97, roll 4 (would be 101) | Ua | FR-10 | Passed | `test_overshoot.py` |
| TC-FR10-2 | Token at 99, roll 2. Watch the UI | Ua, Sm | FR-10 | Automated part passed; manual part not run | `test_overshoot.py` |
| TC-FR10-3 | Token at 96, roll 4 (exactly 100) | Ua | FR-10, FR-09 | Passed | `test_overshoot.py` |
| TC-FR11-1 | Call `BoardRenderer` square-to-pixel mapping headless for all 100 squa | Ua | FR-11 | Passed | `test_board_view.py::test_all_numbers_follow_boustrophedon_order` |
| TC-FR11-2 | Compare a screenshot of the Game screen with SRS 4.3 | Sm | FR-11 | Automated part passed; manual part not run | `test_board_view.py::test_all_numbers_follow_boustrophedon_order`; `test_board_view.py::test_every_snake_and_ladder_has_visible_endpoints` |
| TC-FR11-3 | Put 4 tokens on one square, and put tokens on snake and ladder squares | Sm | FR-11 | Automated part passed; manual part not run | `test_board_view.py::test_four_tokens_remain_distinct_on_every_square_and_at_start` |
| TC-FR12-1 | Start a game and play 6 moves including one extra roll | Sm | FR-12 | Automated part passed; manual part not run | `test_turn_indicator.py::test_indicator_tracks_turns_and_wraparound_for_all_player_counts`; `test_extra_turn.py::test_six_grants_an_extra_roll` |
| TC-FR12-2 | Observe the indicator during animation and after a Resume | Sm | FR-12, FR-15 | Automated part passed; manual part not run | `test_turn_indicator.py::test_indicator_persists_without_input_and_fits_maximum_length_name`; `test_save_resume.py::test_tc_fr15_1_save_and_resume_exact_state` |
| TC-FR13-1 | Time 20 moves from dice value shown to final token square drawn, inclu | Sa | FR-13, NFR-01 | Passed | `test_token_animation.py::test_twenty_moves_in_the_real_loop_render_at_30_fps_or_better`; `test_board_view.py::test_token_position_render_updates_within_one_second_of_roll_display` |
| TC-FR13-2 | Over 100 scripted moves compare the square drawn by the renderer with  | Ia | FR-13 | Passed | `test_roll_performance.py::test_fifty_rolls_are_presented_within_one_second`; 50 rolls through the real loop, not 100 |
| TC-UI1-1 | Open the Setup screen | Sm | UI-1 | Not run (manual) | none |
| TC-UI2-1 | Open the Game screen | Sm | UI-2 | Not run (manual) | none |
| TC-UI3-1 | Finish a game | Sm | UI-3 | Automated part passed; manual part not run | `test_setup_screen.py::test_result_screen_buttons_and_rendering` |
| TC-FR14-1 | Click Restart on the Game screen, then Cancel | Sm | FR-14 | Automated part passed; manual part not run | `test_restart.py::test_restart_cancel_preserves_entire_state_and_blocks_background_input` |
| TC-FR14-2 | Click Restart, then Confirm | Sm | FR-14 | Automated part passed; manual part not run | `test_restart.py::test_confirm_restart_clears_session_keeps_save_and_starts_fresh`; process ID check is manual |
| TC-FR14-3 | On the Result screen click New Game | Sm | FR-14 | Automated part passed; manual part not run | `test_restart.py::test_confirm_restart_clears_session_keeps_save_and_starts_fresh` |
| TC-FR15-1 | 3 players at positions 12, 37 and 0, P3 to move, extra-turn on, last r | Sm | FR-15, NFR-08 | Automated part passed; manual part not run | `test_save_resume.py` |
| TC-FR15-2 | Save while an extra roll is pending (after a 6, `extra_rolls_used` 1), | Ia | FR-15, FR-08 | Passed | `test_save_resume.py` |
| TC-FR15-3 | Save twice with different states, then Resume | Ia | FR-15 | Passed | `test_save_resume.py` |
| TC-FR15-4 | Save a game with extra-turn off; resume; roll a 6 | Ia | FR-15, FR-08 | Passed | `test_save_resume.py` |
| TC-FR15-5 | Save at the start of a game (all positions 0) and again with a player  | Ia | FR-15 | Passed | `test_save_resume.py` |
| TC-FR15-6 | Save a game, resume it, play it to a win, then check Resume. Separatel | Ia | FR-15 | Passed | `test_finished_game_save.py::*` |
| TC-FR16-1 | Finish a game with positions 100, 45, 60, 12 | Ua, Sm | FR-16 | Automated part passed; manual part not run | `test_results.py::test_standings_sorted_without_reordering_game_state` |
| TC-FR16-2 | Two players tied at 45 | Ua | FR-16 | Passed | `test_results.py::test_ties_preserve_setup_order` |
| TC-FR16-3 | Finish a 2-player, a 3-player and a 4-player game | Sm | FR-16 | Automated part passed; manual part not run | `test_results.py::test_every_player_appears_once` |
| TC-FR17-1 | Press Space 10 times quickly while a token is animating. Count scripte | Ia | FR-17 | Passed | `test_plan_gaps.py` |
| TC-FR17-2 | After a win call `on_roll_requested()` and press Space on the Result s | Ia | FR-17 | Passed | `test_plan_gaps.py` |
| TC-FR17-3 | Call `on_save_requested()` and click Save while a move is animating | Ia, Sm | FR-17 | Automated part passed; manual part not run | `test_plan_gaps.py` |
| TC-FR17-4 | Look at the Roll Dice and Save buttons during animation and after game | Sm | FR-17 | Not run (manual) | none |
| TC-FR17-5 | Run the ignored actions above and read the log | Ia | FR-17 | Passed | `test_plan_gaps.py` |
| TC-FR18-1 | Click Exit during a game | Sm | FR-18 | Automated part passed; manual part not run | `test_exit.py::test_window_close_uses_prompt_and_cancel_then_discard` |
| TC-FR18-2 | Choose Save in the prompt | Sm | FR-18, FR-15 | Automated part passed; manual part not run | `test_exit.py::test_save_and_exit_writes_loadable_current_state` |
| TC-FR18-3 | Choose Exit without saving | Sm | FR-18 | Automated part passed; manual part not run | `test_exit.py::test_exit_without_saving_preserves_existing_save` |
| TC-FR18-4 | Choose Cancel | Sm | FR-18 | Automated part passed; manual part not run | `test_exit.py::test_cancel_preserves_session_and_rolling_still_works` |
| TC-FR18-5 | Exit from the Start, Setup and Result screens; also close the window ( | Sm | FR-18 | Automated part passed; manual part not run | `test_exit.py::test_exit_without_active_game_needs_no_prompt`; `test_exit.py::test_setup_exit_button_closes_application` |
| TC-FR18-6 | Request Exit while a token is animating | Sm | FR-18, FR-17 | Automated part passed; manual part not run | `test_exit.py::test_exit_during_move_disables_save_until_animation_finishes` |
| TC-UI4-1 | Open the Start screen with no save file; save a game and return; delet | Sm, Ia | UI-4 | Automated part passed; manual part not run | `test_plan_gaps.py`; `test_save_resume.py::test_ui_save_and_resume_buttons` |
| TC-HW-1 | Play a complete game using only the mouse (names typed on the keyboard | Sm | SRS 3.1.2 | Not run (manual) | none |
| TC-C1-1 | Inspect `requirements.txt` and run the suite on Python 3.10 and on the | Um, Sa | C1, SRS 3.1.3 | Automated part passed; manual part not run | `test_portability.py::test_supported_python_versions_are_declared`; CI runs Python 3.10 and 3.12 |
| TC-C3-1 | Open a saved file with an independent tool (`python -m json.tool`, `jq | Ua | C3, SRS 3.1.3 | Passed | `test_plan_gaps.py` |
| TC-BRD-1 | Validate the `Board` data against SRS 4.3 | Ua | A3, FR-06, FR-07 | Passed | `test_ladders.py`; `test_snakes.py` |
| TC-N01-1 | On the minimum-hardware reference machine, 2 players, log the time fro | Sa, Sm | NFR-01 | Automated part passed; manual part not run | `test_roll_performance.py::test_fifty_rolls_are_presented_within_one_second`; CI variant; reference-machine run pending |
| TC-N02-1 | 5 first-time users, no help: set up a 2-player game and complete one f | Am | NFR-02 | Automated part passed; manual part not run | `test_usability.py::test_setup_and_first_complete_turn_through_real_ui`; automated flow only; the five-user study is pending |
| TC-N03-1 | Play 100 automated full games with the production RNG through the cont | Ia | NFR-03 | Passed | `test_reliability.py` |
| TC-N04-1 | On each of the 3 operating systems disable the network (airplane mode  | Sm | NFR-04, C2 | Automated part passed; manual part not run | `test_availability.py::test_application_launches_to_setup_when_network_is_blocked`; CI variant; the run with the network off on each system is manual |
| TC-N05-1 | Run the same source tree on Windows 10/11, Ubuntu 22.04+ and macOS 13+ | Sm | NFR-05 | Automated part passed; manual part not run | `test_portability.py` |
| TC-N05-2 | Scan all source for operating-system checks (`sys.platform`, `os.name` | Sa | NFR-05 | Passed | `test_portability.py::*` |
| TC-N06-1 | Run `coverage run -m pytest tests/engine tests/persistence tests/contr | Ua | NFR-06 | Passed | CI coverage gate and docs/reports/code-coverage-report.md |
| TC-N06-2 | AST scan of `engine/` for Pygame imports; also run the engine tests wi | Ua | NFR-06, C4 | Passed | `test_plan_gaps.py`; `test_no_pygame.py::test_engine_does_not_import_pygame` |
| TC-N07-1 | Repeat TC-N01-1 with 4 players | Sa, Sm | NFR-07 | Automated part passed; manual part not run | `test_roll_performance.py::test_fifty_rolls_are_presented_within_one_second`; CI variant; reference-machine run pending |
| TC-N08-1 | `tests/test_data_integrity.py`: 20 save and resume cycles over varied  | Ia | NFR-08 | Passed | `test_data_integrity.py::test_twenty_save_resume_cycles_preserve_every_state_field` |
| TC-N09-1 | Check the Start, Setup, Game and Result screens at 1280 x 720, 1366 x  | Sm | NFR-09 | Not run (manual) | none |
| TC-N10-1 | Fault matrix: missing save file, 0-byte file, corrupted file, non-UTF- | Ia, Sm | NFR-10, A4 | Automated part passed; manual part not run | `test_error_handling.py::test_missing_empty_corrupt_saves_preserve_live_state`; `test_error_handling.py::test_save_read_permission_failure_is_reported` |
| TC-N11-1 | Interrupt a save 10 times: kill the process at random moments, and inj | Ia, Sm | NFR-11 | Automated part passed; manual part not run | `test_recoverability.py` |
| TC-N12-1 | Log frame times during 20 moves (including long snake and ladder moves | Sa, Sm | NFR-12 | Automated part passed; manual part not run | `test_token_animation.py` |
| TC-N12-2 | Play 6 moves through the real loop with a clock whose every sleep over | Sa | NFR-12 | Passed | `test_token_animation.py::test_frame_rate_holds_when_the_os_sleep_overshoots` |
| TC-N13-1 | Audit every text element at 1280 x 720 | Um | NFR-13 | Automated part passed; manual part not run | `test_accessibility.py::test_all_screens_use_at_least_fourteen_point_text` |
| TC-N13-2 | Take screenshots of the Game screen and run them through protanopia, d | Um | NFR-13 | Automated part passed; manual part not run | `test_accessibility.py::test_palette_stays_separated_under_colour_vision_simulation`; `test_accessibility.py::test_token_number_contrast_in_normal_and_simulated_vision`; simulated, not a human check |
| TC-N14-1 | CI samples process RSS during 300 rendered gameplay frames; for releas | Sa, Sm | NFR-14 | Automated part passed; manual part not run | `test_resource_efficiency.py::test_four_player_gameplay_stays_within_memory_limit`; CI variant; 30-minute run pending |
| TC-N14-2 | Save the largest possible state (4 players, longest allowed names), ch | Ua | NFR-14 | Passed | `test_resource_efficiency.py::test_largest_save_stays_within_10_kibibytes`; `test_resource_efficiency.py::test_oversized_save_is_rejected_without_replacing_previous_save` |
| TC-N15-1 | Take 60,000 rolls from the production `DiceService` and count each val | Ua | NFR-15 | Passed | `test_randomness.py` |
