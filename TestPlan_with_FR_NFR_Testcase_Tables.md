# Software Test Plan

## Snakes and Ladders Game

**Version**: 1.0 **Date**: 29 September 2026
**Format**: Based on the IEEE Std 829 test plan outline (clause mapping in Section 1.5)
**Baseline**: SRS v1.0 (`SRS.md`), SDD v1.0 (`SDD.md`)

| Field | Value |
| ----- | ----- |
| Test plan identifier | STP-SNL-001 |
| Product | Snakes and Ladders Game (desktop, hot-seat, 2 to 4 players) |
| Repository | https://github.com/niffy-artist2876/snakes-and-ladders |
| Status | Draft for review |


## Revision History

| Version | Date | Description | Author(s) |
|---|---|---|---|
| 1.0 | 29-09-2026 | Initial test plan with test case specifications and SRS traceability | Team |

---

## 1. Introduction

### 1.1 Purpose
This document plans the verification of the Snakes and Ladders game. It states what will be tested, how, by whom, in which environment and against which pass/fail criteria. It also contains the test case specifications and the traceability matrices that link every SRS requirement to at least one test case. It is written for the four-person development team and for the reviewer who will approve the release.

### 1.2 Scope
In scope: every functional requirement (FR-01 to FR-18), user interface requirement (UI-1 to UI-4), non-functional requirement (NFR-01 to NFR-15), security requirement (SEC-01 to SEC-06), the external interfaces of SRS 3.1, and the constraints C1 to C4 of SRS 2.5, exercised on the three supported operating systems.

Out of scope: the items listed in Section 4.

### 1.3 Definitions, Acronyms and Abbreviations
Terms from SRS Section 1.3 and SDD Section 1.3 apply. Additional terms:

| Term | Definition |
|---|---|
| TC | Test case. IDs have the form `TC-<requirement>-<n>`, for example `TC-FR06-2` |
| Scripted RNG | A test-only random source that returns a fixed sequence of dice values, injected through the `GameEngine(rng=...)` constructor (SDD 3.9) |
| Save factory | A test helper that builds a save file for any chosen state and computes the correct SHA-256 checksum (SDD 3.5), so a rejection can only be caused by the rule under test |
| Headless | Running without a visible window, using `SDL_VIDEODRIVER=dummy` |
| Ua / Um | Unit level, automated / manual (inspection) |
| Ia | Integration level, automated |
| Sa / Sm | System level, automated / manual |
| Am | Acceptance level, manual (user study) |
| RR | Residual risk accepted after testing |
| OI | Open item to be confirmed with the SRS or SDD owner (Section 15) |

### 1.4 References
1. SRS v1.0, Snakes and Ladders Game (`SRS.md`), including the use case diagram (`uml.png`).
2. SDD v1.0, Software Architecture and Design Specification (`SDD.md`).
3. IEEE Std 829-2008, Standard for Software and System Test Documentation (test plan outline follows IEEE 829).
4. IEEE Std 830-1998 (SRS) and IEEE Std 1016-2009 (SDD), the baseline document standards.
5. Python 3.10 documentation (`json`, `hashlib`, `secrets`, `unittest.mock`); pytest and coverage.py documentation.

### 1.5 Overview
Section 2 lists the test items. Section 3 lists the features to be tested and Section 4 the features not to be tested. Section 5 gives the approach and the test case specifications, with Section 5.1 dedicated to security validation. Sections 6 to 13 cover pass/fail criteria, suspension, deliverables, tasks, environment, responsibilities, schedule and risks. Section 14 gives traceability to the SRS, Section 15 lists assumptions and open items, and Section 16 the approvals.

| IEEE 829 test plan clause | Section in this document |
|---|---|
| Test plan identifier | Title block |
| Introduction | 1 |
| Test items | 2 |
| Features to be tested | 3 |
| Features not to be tested | 4 |
| Approach | 5 (security validation in 5.1) |
| Item pass/fail criteria | 6 |
| Suspension criteria and resumption requirements | 7 |
| Test deliverables | 8 |
| Testing tasks | 9 |
| Environmental needs | 10 |
| Responsibilities, staffing and training needs | 11 |
| Schedule | 12 |
| Risks and contingencies | 13 |
| Test traceability matrix (IEEE 829-2008) | 14 |
| Approvals | 16 |

---

## 2. Test Items

### 2.1 Items Under Test

| ID | Test item | Design reference |
|---|---|---|
| TI-01 | Domain layer `engine/`: `GameEngine`, `Board`, `TurnManager`, `DiceService` | SDD C10 to C13, 3.2 |
| TI-02 | Application layer `controller/`: `GameController`, `InputValidator` | SDD C8, C9, 3.4, 3.6 |
| TI-03 | Persistence layer `persistence/`: `SaveManager`, `SaveValidator`, `ChecksumService` | SDD C14 to C16, 3.5 |
| TI-04 | Presentation layer `ui/`: `ScreenManager`, Setup / Game / Result screens, `BoardRenderer`, `InputHandler`, `AnimationController` | SDD C1 to C7 |
| TI-05 | Composition root `main.py` (wires the production RNG `secrets.SystemRandom`) | SDD 2.5, 3.9 |
| TI-06 | Save file format `savegame.json`, format version 1 | SDD 3.5 |
| TI-07 | Complete application (one source tree) on Windows 10/11, Ubuntu 22.04+, macOS 13+ | SRS 2.4 |

### 2.2 Item Documentation
SRS v1.0 and SDD v1.0 are the test basis. Where the two documents disagree or are silent, the test case follows the SDD and the difference is logged as an open item in Section 15.

### 2.3 Test Item Entry Requirements
A build is accepted for a test level only when it is tagged in the repository, installs from a clean checkout, launches to the start screen, and the Ua smoke subset passes (Section 7).

---

## 3. Features to Be Tested

### 3.1 Feature Groups

| Group | Features (SRS IDs) | Priority | Main level | Test cases in |
|---|---|---|---|---|
| G1 Game setup | FR-01, FR-02, UI-1 | H | Ua, Sm | 5.2 |
| G2 Core gameplay | FR-03 to FR-10 (FR-08 is M) | H | Ua, Ia | 5.2 |
| G3 Display and feedback | FR-11, FR-12, FR-13, UI-2, UI-3 | H | Sm, Sa | 5.2 |
| G4 Session control | FR-14 to FR-18, UI-4 (FR-15 is M) | H | Ia, Sm | 5.2 |
| G5 External interfaces and constraints | SRS 3.1.2, 3.1.3, 3.1.4; C1, C3, C4 | H | Ua, Sm | 5.2, 5.3 |
| G6 Default board configuration | SRS 4.3, assumption A3 | H | Ua | 5.2 |
| G7 Non-functional qualities | NFR-01 to NFR-15 | H | Sa, Sm, Am | 5.3 |
| G8 Security | SEC-01 to SEC-06, SO-1 to SO-4 | H | Ua, Ia, Sa | 5.1 |

### 3.2 Features by Use Case
Use cases are those of the SRS use case diagram (Appendix 4.1). UC numbers are given only where the SRS states them; the other use cases are identified by name, as in SDD 4.2.

| Use case | UC ID | Main features exercised |
|---|---|---|
| Set Up Game, Enter Player Details | not stated | FR-01, FR-02, SEC-01, UI-1 |
| Roll Dice | UC3 | FR-03, FR-05, FR-13, FR-17, SEC-04 |
| Move Token | UC4 | FR-04, FR-10 |
| Apply Snake / Ladder | UC5 | FR-06, FR-07 |
| Grant Extra Turn | UC6 | FR-08 |
| Check Win | UC7 | FR-09 |
| View Result | UC8 | FR-16, UI-3 |
| Resume Game, Validate Save File | UC10, UC13 | FR-15, NFR-08, SEC-02, SEC-03, SEC-05, UI-4 |
| Save Game | not stated | FR-15, FR-17, NFR-11 |
| Restart Game | not stated | FR-14 |
| Exit Game | not stated | FR-18 |

### 3.3 Test Priority
Execution order is risk based. P1: security (5.1), save and resume, and the rule engine (FR-03 to FR-10), because a defect there is silent or corrupts state. P2: session control, display, and NFR measurements. P3: usability and visual checks that need people or several machines.

---

## 4. Features Not to Be Tested

| Feature | Reason |
|---|---|
| Online or networked multiplayer, AI opponents, user accounts, leaderboards, in-app purchases | Out of scope in SRS 1.2. Only the absence of any network access is tested (SEC-06) |
| Custom board layouts | Out of scope, assumption A3. Only the default board is tested (TC-BRD-1) |
| Unsupported platforms and settings: Windows 8 or older, macOS earlier than 13, Ubuntu earlier than 22.04, Python earlier than 3.10, screens below 1280 x 720 or above 1920 x 1080 | Outside SRS 2.4 and NFR-09. Best effort only, no pass/fail |
| Hardware below the SRS minimum | NFR-01 and NFR-12 are defined on the minimum hardware only |
| Packaging, installers and the packaged executable | SDD 1.2 excludes deployment packaging; assumption A2 allows either delivery form |
| User manual and help text | Not required by the SRS |
| Cryptographic unforgeability of save files | SO-1 requires "not silently altered", not forgery resistance. The unkeyed SHA-256 limitation is accepted (SDD 2.7). TC-SEC02-6 records the behaviour but is informational |
| Internals of Pygame, CPython `json`, `hashlib` and `secrets` | Third-party components assumed correct; tested only through how the product uses them |
| Screen readers, key remapping and other assistive technology | Only NFR-13 (font size, colour-blind safe tokens) is required |
| Non-ASCII player names | Deliberately rejected by SEC-01; tested as rejection only |
| Two application instances sharing one save file at the same time | Not specified in the SRS or SDD (see risk R11) |
| Long soak runs beyond 30 minutes | Not required; NFR-14 is checked over a 30-minute session |

---

## 5. Approach

The strategy is requirement driven and risk based. Every test case names the SRS requirement it verifies, and every requirement has at least one test case (Section 14). Rule logic is tested automatically and headless, because the SDD separates it from Pygame (C4, NFR-06). Anything that needs eyes, several machines or people (layout, colour-blind check, usability, OS smoke tests) is done manually against a written checklist.

**Test levels**

| Level | Target | How | Entry / exit |
|---|---|---|---|
| Unit (U) | `engine/`, `persistence/`, `InputValidator` | pytest with a scripted RNG and the save factory; coverage measured with `coverage.py` | Runs on every commit. Exit: all pass, engine statement coverage 80% or more (NFR-06) |
| Integration (I) | `GameController` with real engine and persistence, no visible window | pytest with `SDL_VIDEODRIVER=dummy`, scripted RNG, temporary save directory | Runs on every merge. Exit: all pass |
| System (S) | The full application on Windows, Ubuntu and macOS | Manual scripts and scripted UI runs on the production build (real RNG) | Runs per release candidate. Exit: all pass on all three systems |
| Acceptance (A) | Usability and requirement sign-off | User study for NFR-02; reviewer walk-through of Section 14 | After system testing |

**Techniques used:** boundary value analysis and equivalence partitioning (names, positions, file sizes), state-transition testing (phases `AWAITING_ROLL`, `ANIMATING`, `GAME_OVER` and the screen flow of SDD 3.1), decision-table testing (roll outcomes, 5.2.1), data-driven tests over the whole default board, scripted-RNG determinism, statistical tests (chi-square), fault injection, structured fuzzing, static analysis (AST scan and `grep` in CI), code review, and timing and resource measurement.

**Legend for the test case tables.** Level: Ua, Um, Ia, Sa, Sm, Am as defined in Section 1.3. Req: the SRS requirement or objective verified. In expected results, **SRC** (standard rejection check) means all of the following hold:
1. The user sees exactly "Save file is corrupted or has been modified." (or the E-05 text where the file is missing).
2. The application stays on the Start screen and no game state is created.
3. The file on disk is byte-identical afterwards.
4. `snl.log` records the specific `SaveError` subclass and no traceback appears on screen.
5. A New Game can still be started.

### 5.1 Security Validation

#### 5.1.1 Security Objectives and Test Focus
The system is offline, single-device and has no accounts, so the threats are a tampered save file, manipulated dice, malformed input, and any network exposure (SRS 3.4, SDD 2.7).

| Objective (SRS 3.4.1) | Threat | Trust boundary (SDD 2.7) | Requirements | Test cases |
|---|---|---|---|---|
| SO-1 Integrity of game state | Save file altered or corrupted between save and resume | TB-2 | SEC-02, SEC-03 | TC-SEC02-*, TC-SEC03-*, TC-SECX-1 |
| SO-2 Fairness | Dice outcome set, influenced or predicted | TB-3 | SEC-04 | TC-SEC04-* |
| SO-3 Robustness against malformed input | Names or files that crash the app, run code or create invalid state | TB-1, TB-2 | SEC-01, SEC-03, SEC-05 | TC-SEC01-*, TC-SEC03-*, TC-SEC05-*, TC-SECX-2 |
| SO-4 Minimal attack surface | Any network interface | TB-4 | SEC-06 | TC-SEC06-* |

#### 5.1.2 Security Test Techniques

| Technique | Used for |
|---|---|
| Negative testing with crafted files from the save factory | SEC-02, SEC-03, SEC-04, SEC-05: each file breaks exactly one rule and carries a correct checksum, so only the rule under test can reject it |
| Boundary value analysis | Name length 0/1/15/16, save size 10,240/10,241 bytes, positions -1/0/100/101 |
| Structured and random fuzzing | Name validator, JSON parser (deep nesting, huge numbers, `NaN`) |
| Static analysis (`grep` plus AST walker, run in CI) | SEC-04, SEC-05, SEC-06: banned calls and imports |
| Runtime instrumentation | SEC-06: socket trap; SEC-05: marker-file canary |
| OS-level tracing | SEC-06 and least privilege: `strace`, Process Monitor, `fs_usage`, `lsof` |
| Statistical testing | SEC-04 and NFR-15: chi-square on single rolls and on roll pairs |
| Code review checklist | SEC-05: loader uses `json` only |

#### 5.1.3 Security Test Cases

**SEC-01: player name validation (SO-3)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC01-1 | In Setup enter names of 1 character (`A`) and 15 characters (`ABCDEFGHIJKLMNO`), then 0 characters and 16 characters (`ABCDEFGHIJKLMNOP`) | 1 and 15 characters accepted. 0 and 16 rejected with "Names must be 1 to 15 letters, digits or spaces." (E-01), field highlighted, Start stays disabled | Ua, Sm | SEC-01 |
| TC-SEC01-2 | Enter each of: `Bob!`, `Al_ice`, `a-b`, `<b>x</b>`, `x;y`, `../a`, `é`, `名前`, an emoji, and names containing a tab, a newline, or a NUL character | Every name rejected with the E-01 message. No such name is stored or shown on any later screen | Ua | SEC-01 |
| TC-SEC01-3 | Enter `"   "` (spaces only), `" Sam "` and `"Player 1"` | Spaces-only rejected. `" Sam "` accepted and stored as `Sam` (SDD 3.6.4 strips). `"Player 1"` accepted, as the space is in the allowed set | Ua | SEC-01, FR-02 |
| TC-SEC01-4 | Fuzz the validator with 10,000 random strings from the whole Unicode range (length 0 to 100). In the real UI paste a 10,000-character string, press Tab, Enter and Esc, and hold a key in the name field | A string is accepted if and only if it matches `^[A-Za-z0-9 ]{1,15}$` after stripping (independent oracle in the test). Zero exceptions; UI stays responsive | Ua, Sm | SEC-01, NFR-10 |
| TC-SEC01-5 | Save factory builds otherwise valid files (correct checksum) whose player name is `Bob!`, a 16-character name, or empty. Press Resume | SRC. Names are validated again on load (defence in depth, SDD 2.7) | Ia | SEC-01, SEC-03 |

**SEC-02: save file checksum (SO-1)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC02-1 | Save through the UI, leave the file untouched, press Resume | File loads and the state equals the saved state | Ia | SEC-02, FR-15 |
| TC-SEC02-2 | Edit `position`, `current_index` or `extra_turn_enabled` inside `state` in the JSON text, one field per attempt, without changing `checksum` | SRC for every attempt | Ia | SEC-02 |
| TC-SEC02-3 | Damage the `checksum` field: flip one hex digit; cut it to 63 characters; use 64 non-hex characters; use an empty string; use `null`; delete the key | SRC for every variant | Ua | SEC-02 |
| TC-SEC02-4 | Re-format a valid save without changing any value: other indentation, keys in another order, CRLF line endings, extra spaces | File loads, because the checksum is taken over canonical JSON (SDD 3.5) | Ua | SEC-02, NFR-08 |
| TC-SEC02-5 | Trigger E-06, E-07, E-08 and E-09 in turn (oversize, bad JSON, out-of-range value, checksum mismatch) and compare the on-screen text and the log | The four screen messages are byte-identical. The specific error name (for example `SaveIntegrityError`) appears in `snl.log` only, never on screen (ADR-5) | Ia | SEC-02, SEC-03 |
| TC-SEC02-6 | Informational. Change `position` of a valid save, recompute the SHA-256 exactly as SDD 3.5 defines and write it into `checksum` | File loads. This is accepted residual risk RR-1 (5.1.4). The test fails only if a forged file with an out-of-range value is accepted | Ia | SEC-02, SO-1 |

**SEC-03: validation before load (SO-1, SO-3)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC03-1 | Pad a valid save with insignificant whitespace to exactly 10,240 bytes; then to 10,241 bytes; then create a 50 MB file | 10,240 bytes loads. 10,241 bytes and 50 MB give SRC (E-06). The 50 MB file is rejected in under 1 s without being read fully; peak memory stays under 200 MB | Ia | SEC-03, NFR-14 |
| TC-SEC03-2 | Files that are not valid JSON documents: 0 bytes, spaces only, truncated JSON, random binary, UTF-16 with byte-order mark, plain text, and the JSON values `null`, `[]`, `"text"`, `123` | SRC for each (E-07). No crash | Ua | SEC-03, NFR-10 |
| TC-SEC03-3 | Parser stress within 10 KB: about 10,000 nested `[`; a 5,000-digit integer as `position`; the literals `NaN`, `Infinity` and `-Infinity` as `position` | SRC for each. No unhandled `RecursionError` or `ValueError`. Application stays usable | Ua | SEC-03, SEC-05, NFR-10 |
| TC-SEC03-4 | Schema and type violations (checksum recomputed): missing `version`, `state`, `players` or `checksum`; `players` as an object; `position` as `"37"`, `37.5`, `true` or `null`; `current_index` as `true`; `extra_turn_enabled` as `1` or `"yes"`; `last_roll` as `0`, `7` or `"3"`; an unknown extra key; `version` as `2` or `true` | Every file gives SRC. Booleans are not accepted where integers are required (Python treats `True` as `1`) | Ua | SEC-03 |
| TC-SEC03-5 | Range violations (checksum recomputed): 1 player; 5 players; `position` -1, 101, and 100 (finished game, D-4); `current_index` equal to the player count, and -1; `extra_rolls_used` 3; duplicate names, also differing only in case; duplicate colours; a colour outside the allowed set. Controls: 4 players with positions 0 and 99, and `last_roll` `null` | Each violation gives SRC (E-08). Both controls load | Ua | SEC-03 |
| TC-SEC03-6 | After each rejection above, check the hash of the file on disk, whether `savegame.json.tmp` exists and which screen is shown. Then start a New Game, and separately resume a valid save | File byte-identical, no `.tmp` file, still on the Start screen, no game state exists. New Game and a later valid Resume both work | Ia, Sm | SEC-03 |
| TC-SEC03-7 | Files with two problems: oversize and malformed; bad schema and bad checksum; bad range and bad checksum. Read the log code | Log names the first failing check in the SDD 2.7 order: size, JSON, schema and types, ranges, checksum | Ia | SEC-03 |
| TC-SEC03-8 | Hostile file-system states for `savegame.json`: it is a directory; it is unreadable (permission denied); on Linux and macOS it is a symbolic link to `/dev/zero` | E-05 or E-07 behaviour, no game started, no crash. The `/dev/zero` case returns in under 1 s with no memory growth, because the read is limited to 10 KB plus 1 byte | Ia | SEC-03, NFR-10 |

**SEC-04: dice integrity and fairness (SO-2)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC04-1 | Inspect the public API with `inspect`: signature of `GameEngine.roll_and_move` and public members of `DiceService` and `GameEngine` | `roll_and_move` has no dice argument. No public setter or attribute can set a dice value or a seed. The RNG is accepted only by the constructor (SDD 3.6.2) | Ua | SEC-04 |
| TC-SEC04-2 | During a real game press the digits 1 to 6, numpad keys, Enter, arrow keys, F-keys and Esc; click the last-dice display, the tokens and board squares | No roll happens except through the Roll Dice button or Space. The displayed dice value is never set by any other input | Sm | SEC-04, FR-03 |
| TC-SEC04-3 | Save factory files (correct checksum) with an extra key such as `next_roll`, `dice` or `rng_seed`. Separately, resume a save with `last_roll` 6 using a scripted RNG that returns 2 | Files with extra keys give SRC (allow-list schema). In the second case the next roll is 2: `last_roll` is display state and never feeds the RNG | Ia | SEC-04, SEC-03 |
| TC-SEC04-4 | Start the production entry point with `--seed 1`, with `SNL_SEED=1` and `PYTHONHASHSEED=0` in the environment, and with a stray `seed.cfg` in the working directory. Launch twice each time and log the first 20 dice values at the composition root | Unknown arguments are ignored or rejected. The two launches never give the same 20-value sequence (chance of a match is 6^-20) | Sa | SEC-04, SO-2 |
| TC-SEC04-5 | Static check over all non-test code: `engine/dice.py` uses `secrets.SystemRandom` only; no `random.seed`, `random.Random` or `numpy.random`; the only `GameEngine(rng=...)` call outside `tests/` is in `main.py` | Zero violations; the CI job fails the build otherwise | Ua | SEC-04, NFR-15 |
| TC-SEC04-6 | Take 60,000 rolls from the production `DiceService`, split them into 30,000 non-overlapping pairs and count the 36 outcomes (expected 833.3 each) | Chi-square statistic (35 degrees of freedom, 5% level) is below 49.80. Rerun policy in R1 (Section 13) | Ua | SEC-04, NFR-15 |

**SEC-05: data-only parsing (SO-3)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC05-1 | Scan all non-test code with `grep` and with an AST walker for `eval`, `exec`, `compile`, `pickle`, `marshal`, `shelve`, `yaml.load`, `os.system`, `subprocess`, `__import__` | Zero hits. The AST walker also catches aliased imports that `grep` can miss | Ua | SEC-05 |
| TC-SEC05-2 | Place hostile content in `savegame.json`: (a) a valid-checksum file whose player name is the text of a Python expression; (b) a Python pickle stream whose loading would create a marker file in a temporary directory | (a) Rejected by the name rule, nothing evaluated. (b) Rejected as invalid JSON (SRC). In both cases the marker file does not exist afterwards | Ia | SEC-05, SEC-03 |
| TC-SEC05-3 | Review `SaveManager.load` against a checklist: only `json.load` or `json.loads`; no `object_hook` or custom decoder; no dynamic import | Reviewer signs off every item | Um | SEC-05 |

**SEC-06: no network access (SO-4)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SEC06-1 | Scan all project source for imports of `socket`, `urllib`, `http`, `requests`, `ftplib`, `smtplib`, `telnetlib`, `xmlrpc`, `websocket` and asyncio streams. Check `pip freeze` of the runtime environment | No such import. The only runtime dependency is Pygame | Ua | SEC-06, SO-4 |
| TC-SEC06-2 | Patch `socket.socket`, `socket.create_connection` and `socket.getaddrinfo` to raise an error. Script a full session: setup, play to a win, save, resume, restart, exit | The trap never fires and the session completes | Ia | SEC-06 |
| TC-SEC06-3 | Run a 5-minute session under an OS-level trace: `strace -f -e trace=network` (Linux), Process Monitor or Resource Monitor (Windows), `lsof -i` and `nettop` (macOS) | No socket created, no DNS lookup, no listening port | Sm | SEC-06, NFR-04 |

**Design-derived security checks (SDD 2.7 and 3.4)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-SECX-1 | Trace file-system activity through a full session (`strace -e trace=file`, Process Monitor, `fs_usage`) | Writes go only to `savegame.json`, `savegame.json.tmp` and `snl.log` in the per-user save directory (SDD 2.8). No other path outside the install directory is written (least privilege) | Sm | SO-1, SO-3 |
| TC-SECX-2 | Fault injection: make an engine call raise `EngineInvariantError`, then raise a generic `Exception` in the main loop | Screen shows only "An unexpected error occurred. Returning to the start screen." (E-11, E-12). No traceback, path or exception name on screen; the traceback is in `snl.log`. App returns to the Start screen | Ia | NFR-10, SO-3 |

#### 5.1.4 Security Exit Criteria and Residual Risk
Exit criteria: all 33 security test cases pass, except TC-SEC02-6, which must run and have its outcome recorded; zero unhandled exceptions in all fuzz and fault-injection runs; zero network activity in TC-SEC06-3; zero open Critical or Major security defects.

| ID | Residual risk accepted | Reason |
|---|---|---|
| RR-1 | A user who edits the state and recomputes the unkeyed SHA-256 can forge an in-range save file (TC-SEC02-6) | SO-1 means "not silently altered", not unforgeable. The game is single-device with no accounts or rewards (SDD 2.7). An embedded HMAC key would not materially help |
| RR-2 | A user with a debugger or a modified copy of the source can alter dice values | SEC-04 covers every path through the application's UI, keyboard and files. A local program cannot defend its own process |

### 5.2 Functional Validation

Rule tests use a scripted RNG, so every expected position below is exact. Square numbers were checked against the default board (SRS 4.3): unless a test says otherwise, every square a token starts on or lands on is a plain square (no snake head or ladder base). "P1", "P2" are players in setup order.

#### 5.2.1 Roll-Resolution Decision Table (SDD 3.2)

| Rule | Condition | Outcome | Covered by |
|---|---|---|---|
| R1 | Position + roll is above 100 | Token stays, turn passes, no extra roll (OVERSHOOT) | TC-FR10-1, TC-FR10-2, TC-FR08-6 |
| R2 | Lands on a plain square, not 100, no extra roll due | Token moves, turn passes | TC-FR04-1 to 3, TC-FR05-1 |
| R3 | Lands on a snake head | Token goes to the tail | TC-FR06-1 to 3 |
| R4 | Lands on a ladder base | Token goes to the ladder top | TC-FR07-1 to 3 |
| R5 | Final square is 100 | Winner declared, game over, no extra roll | TC-FR09-1, TC-FR09-2, TC-FR10-3, TC-FR08-7 |
| R6 | Roll is 6, extra-turn on, fewer than 2 extra rolls used, no win, no overshoot | Same player rolls again | TC-FR08-1, TC-FR08-5 |
| R7 | Roll is 6, extra-turn on, 2 extra rolls already used | Turn passes | TC-FR08-2 |
| R8 | Roll is 6, extra-turn off | Turn passes | TC-FR08-4 |

#### 5.2.2 Functional Test Cases

**Game setup (FR-01, FR-02, UI-1)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-FR01-1 | Open Setup with 0 valid players, then 1 valid player | Start button is disabled and clicking it does nothing (E-03) | Sm | FR-01 |
| TC-FR01-2 | Configure 2 valid players and click Start | Game screen opens with 2 tokens at position 0 (off the board) and P1 as current player | Sm | FR-01 |
| TC-FR01-3 | Configure 4 valid players and start. At engine level call `new_game` with 5 configs and with 1 config | 4 tokens shown. The count control offers only 2 to 4. The engine rejects 5 and 1 with `InputValidationError` | Sm, Ua | FR-01 |
| TC-FR02-1 | Leave one name empty in a 2-player setup | Rejected with the E-01 message, Start disabled | Sm, Ua | FR-02, SEC-01 |
| TC-FR02-2 | Give two players the name `Asha`; then `Sam` and `sam` | Rejected with "Each player needs a unique name and colour." (E-02). Comparison is case-insensitive (D-5). User stays on Setup | Ua | FR-02 |
| TC-FR02-3 | Give two players the same token colour | Rejected with the E-02 message; the colour selector flags or prevents the duplicate | Ua, Sm | FR-02 |
| TC-FR02-4 | Enter four distinct names and four distinct colours | Accepted. Each token has its own colour and a number label 1 to 4 in setup order; names appear as entered (trimmed) | Sm | FR-02, NFR-13 |

**Core gameplay (FR-03 to FR-10)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-FR03-1 | Scripted RNG returns 4. Click Roll Dice | Dice value 4 is displayed | Ia | FR-03 |
| TC-FR03-2 | Scripted RNG returns 5. Press the Space key | Value 5 displayed. Button and Space give identical results | Ia, Sm | FR-03, SRS 3.1.2 |
| TC-FR03-3 | Take 6,000 rolls from the production `DiceService` | Every value is in 1 to 6, and all six values occur | Ua | FR-03 |
| TC-FR04-1 | Token at 0, roll 3 | Position 3 | Ua | FR-04 |
| TC-FR04-2 | Token at 10, roll 5 | Position 15 | Ua | FR-04 |
| TC-FR04-3 | One token, rolls 6, 5, 2 from position 0 (extra-turn off) | Positions 6, 11, 13 in turn: exactly the dice value is added each time | Ua | FR-04 |
| TC-FR05-1 | 3 players, extra-turn off, rolls 2, 3, 5, then 2 more | Turn indicator goes P1, P2, P3, P1. Each roll moves only the current player's token | Ua | FR-05 |
| TC-FR05-2 | 4 players, 8 consecutive moves on plain squares (rolls 2,2,2,2,3,3,3,3) watched in the UI | Order repeats P1..P4, P1..P4. The indicator changes only after the move and its animation are complete | Ia, Sm | FR-05, FR-12 |
| TC-FR05-3 | In a 3-player game roll once and compare all three positions before and after | Only the current player's position changed | Ua | FR-05 |
| TC-FR06-1 | Token at 14, roll 3 (lands on 17, a snake head) | Final position 7. `TurnResult`: landed 17, final 7, event SNAKE. Token visibly moves to the head, then to the tail | Ua, Sm | FR-06 |
| TC-FR06-2 | Data-driven over all 8 snakes, each from head minus 1 with roll 1: 16 to 7, 53 to 34, 61 to 19, 63 to 60, 86 to 36, 92 to 73, 94 to 75, 97 to 79 | Final positions are the tails 7, 34, 19, 60, 36, 73, 75, 79 | Ua | FR-06 |
| TC-FR06-3 | Token at 2, roll 5 (lands on 7, a snake tail) | Token stays on 7; event NONE (a tail is not a trigger) | Ua | FR-06 |
| TC-FR07-1 | Token at 0, roll 4 (lands on 4, a ladder base) | Final position 14, event LADDER | Ua, Sm | FR-07 |
| TC-FR07-2 | Data-driven over all 8 ladders, each from base minus 1 with roll 1 (from 0 for base 1): 1 to 38, 4 to 14, 9 to 31, 21 to 42, 28 to 84, 51 to 67, 72 to 91, 80 to 99 | Final positions are the tops 38, 14, 31, 42, 84, 67, 91, 99 | Ua | FR-07 |
| TC-FR07-3 | Token at 38, roll 4 (lands on 42, the top of ladder 21 to 42) | Token stays on 42; a ladder top is not a trigger | Ua | FR-07 |
| TC-FR08-1 | Extra-turn on. P1 from 0 rolls 6 then 2 | After the 6, P1 rolls again and the indicator does not change. Position after the 2 is 8. Turn then passes to P2 | Ua | FR-08 |
| TC-FR08-2 | Extra-turn on. P1 rolls 6, 6, 6 (positions 6, 12, 18). Then P2 rolls 6 then 1 | The third 6 gives no extra roll: turn passes to P2 (limit of 2 extra rolls). The counter is reset for P2, who gets one extra roll after the 6 | Ua | FR-08 |
| TC-FR08-3 | Extra-turn on. Roll 4 | No extra roll, turn passes | Ua | FR-08 |
| TC-FR08-4 | Extra-turn off. Roll 6 | No extra roll, turn passes. Repeat after a save and resume of a game with the option off | Ua, Ia | FR-08, FR-15 |
| TC-FR08-5 | Extra-turn on. Token at 11, roll 6 (lands on snake head 17) | Token goes to 7 and an extra roll is still granted (rule R6) | Ua | FR-08, FR-06 |
| TC-FR08-6 | Extra-turn on. Token at 97, roll 6 (overshoot) | Token stays on 97, turn passes, no extra roll (design decision D-1; see OI-1) | Ua | FR-08, FR-10 |
| TC-FR08-7 | Extra-turn on. Token at 94, roll 6 (reaches 100) | Winner declared, game over, no extra roll | Ua | FR-08, FR-09 |
| TC-FR09-1 | Token at 94, roll 6. Watch the UI | Token reaches 100, the current player is declared winner, phase becomes `GAME_OVER`, Result screen appears after the animation | Ia, Sm | FR-09 |
| TC-FR09-2 | Token at 99, roll 1 | Win | Ua | FR-09 |
| TC-FR09-3 | Token at 79, roll 1 (ladder 80 to 99) | Token is on 99, no winner, game continues, turn passes. A later roll of 1 from 99 wins | Ua | FR-09, FR-07 |
| TC-FR10-1 | Token at 97, roll 4 (would be 101) | Position stays 97, event OVERSHOOT, turn passes | Ua | FR-10 |
| TC-FR10-2 | Token at 99, roll 2. Watch the UI | Dice shows 2, token does not move, next player becomes current | Ua, Sm | FR-10 |
| TC-FR10-3 | Token at 96, roll 4 (exactly 100) | Win (exact landing is not an overshoot) | Ua | FR-10, FR-09 |

**Display and feedback (FR-11 to FR-13, UI-2, UI-3)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-FR11-1 | Call `BoardRenderer` square-to-pixel mapping headless for all 100 squares | Square 1 is bottom-left, 10 bottom-right, 11 directly above 10, 20 directly above 1, 91 top-right, 100 top-left. All 100 positions are distinct and consecutive squares are adjacent | Ua | FR-11 |
| TC-FR11-2 | Compare a screenshot of the Game screen with SRS 4.3 | Numbers 1 to 100 are legible. All 8 ladders and 8 snakes are drawn between the correct squares. Nothing is hidden | Sm | FR-11 |
| TC-FR11-3 | Put 4 tokens on one square, and put tokens on snake and ladder squares | All 4 tokens remain visible and distinguishable. Tokens at position 0 are shown in a start area | Sm | FR-11 |
| TC-FR12-1 | Start a game and play 6 moves including one extra roll | Indicator shows the current player's name and colour, changes after each completed turn and stays on the same player during an extra roll | Sm | FR-12 |
| TC-FR12-2 | Observe the indicator during animation and after a Resume | Never blank. After Resume it shows the saved current player | Sm | FR-12, FR-15 |
| TC-FR13-1 | Time 20 moves from dice value shown to final token square drawn, including a 6 that ends on a snake and one on a ladder | Every move is at or below 1 s | Sa | FR-13, NFR-01 |
| TC-FR13-2 | Over 100 scripted moves compare the square drawn by the renderer with `state.players[i].position` after each move | Always equal (display never lags or differs from state) | Ia | FR-13 |
| TC-UI1-1 | Open the Setup screen | Controls exist for player count (2 to 4), a name field per player, token colour, the extra-turn toggle and Start; all work | Sm | UI-1 |
| TC-UI2-1 | Open the Game screen | Board, all tokens, Roll Dice button, last dice value, turn indicator, Save, Restart and Exit are shown and each button works | Sm | UI-2 |
| TC-UI3-1 | Finish a game | Result screen shows the winner and the final standings, with working New Game and Exit buttons | Sm | UI-3 |

**Session control (FR-14 to FR-18, UI-4)**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-FR14-1 | Click Restart on the Game screen, then Cancel | Confirmation prompt appears. Cancel leaves positions and turn unchanged | Sm | FR-14 |
| TC-FR14-2 | Click Restart, then Confirm | Setup screen opens. A new game starts with all positions 0 and P1 to move. The process ID is unchanged (application not closed) | Sm | FR-14 |
| TC-FR14-3 | On the Result screen click New Game | Confirmation prompt, then the Setup screen | Sm | FR-14 |
| TC-FR15-1 | 3 players at positions 12, 37 and 0, P3 to move, extra-turn on, last roll 4. Save, exit, relaunch, Resume | Names, colours, positions, rule setting, current turn and last dice value are identical; the board looks the same | Sm | FR-15, NFR-08 |
| TC-FR15-2 | Save while an extra roll is pending (after a 6, `extra_rolls_used` 1), then resume and roll 6, 6 | Same player continues. The next 6 gives the last extra roll and the one after gives none (D-2, D-3; see OI-2) | Ia | FR-15, FR-08 |
| TC-FR15-3 | Save twice with different states, then Resume | Only the latest save is loaded. No `savegame.json.tmp` remains | Ia | FR-15 |
| TC-FR15-4 | Save a game with extra-turn off; resume; roll a 6 | Option is still off: no extra roll | Ia | FR-15, FR-08 |
| TC-FR15-5 | Save at the start of a game (all positions 0) and again with a player on 99; Resume each | Save is possible at both points and each resumes correctly | Ia | FR-15 |
| TC-FR16-1 | Finish a game with positions 100, 45, 60, 12 | Result shows the winner's name and standings in the order 100, 60, 45, 12 (descending position) | Ua, Sm | FR-16 |
| TC-FR16-2 | Two players tied at 45 | Tied players are ranked in setup order (SDD 3.6.2) | Ua | FR-16 |
| TC-FR16-3 | Finish a 2-player, a 3-player and a 4-player game | Every player appears in the standings | Sm | FR-16 |
| TC-FR17-1 | Press Space 10 times quickly while a token is animating. Count scripted-RNG calls | Exactly 1 roll is processed and the RNG is called once | Ia | FR-17 |
| TC-FR17-2 | After a win call `on_roll_requested()` and press Space on the Result screen | Ignored, no state change | Ia | FR-17 |
| TC-FR17-3 | Call `on_save_requested()` and click Save while a move is animating | Ignored (Save disabled). Save file hash and modification time unchanged | Ia, Sm | FR-17 |
| TC-FR17-4 | Look at the Roll Dice and Save buttons during animation and after game over | Roll Dice is disabled or greyed during animation and after game over; Save is disabled during animation | Sm | FR-17 |
| TC-FR17-5 | Run the ignored actions above and read the log | No message on screen (E-04), no exception; entry at DEBUG level only | Ia | FR-17 |
| TC-FR18-1 | Click Exit during a game | Prompt with Save, Exit without saving and Cancel | Sm | FR-18 |
| TC-FR18-2 | Choose Save in the prompt | A valid save is written (loads through Resume), then the application closes | Sm | FR-18, FR-15 |
| TC-FR18-3 | Choose Exit without saving | Application closes. The existing save file is unchanged (hash equal) | Sm | FR-18 |
| TC-FR18-4 | Choose Cancel | Prompt closes, game state unchanged, rolling still works | Sm | FR-18 |
| TC-FR18-5 | Exit from the Start, Setup and Result screens; also close the window (window button, Alt+F4, Cmd+Q) during a game | No prompt without a game in progress. Window close during a game behaves like the Exit button | Sm | FR-18 |
| TC-FR18-6 | Request Exit while a token is animating | No crash and no partial save file. The prompt appears; Save is deferred or unavailable until the move ends (see OI-4) | Sm | FR-18, FR-17 |
| TC-UI4-1 | Open the Start screen with no save file; save a game and return; delete the file and return. Force `on_resume_requested()` with no file | Resume is hidden or disabled without a file and present with one. The forced call shows "No saved game found." (E-05). Behaviour with a corrupt file: see OI-3 | Sm, Ia | UI-4 |

**Interfaces, constraints and board configuration**

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-HW-1 | Play a complete game using only the mouse (names typed on the keyboard); then use a trackpad; then roll with Space | All actions work by mouse or trackpad. The keyboard is needed only for names and Space | Sm | SRS 3.1.2 |
| TC-C1-1 | Inspect `requirements.txt` and run the suite on Python 3.10 and on the newest stable Python 3 | Only Python 3.10+ and Pygame 2.x are required; the game runs on both interpreters | Um, Sa | C1, SRS 3.1.3 |
| TC-C3-1 | Open a saved file with an independent tool (`python -m json.tool`, `jq`) and compare with SDD 3.5 | Valid UTF-8 JSON with keys `version`, `state`, `checksum` and the documented fields | Ua | C3, SRS 3.1.3 |
| TC-BRD-1 | Validate the `Board` data against SRS 4.3 | Exactly 8 ladders and 8 snakes as listed. Every snake head is above its tail and every ladder base below its top. No square is both a head and a base. No tail or top lands on a head or base. No snake head on 100 | Ua | A3, FR-06, FR-07 |

### 5.3 Non-Functional Validation

| ID | Scenario and input | Expected result | Level | Req |
|---|---|---|---|---|
| TC-N01-1 | On the minimum-hardware reference machine, 2 players, log the time from roll input to dice value and final token position for 50 rolls | All 50 are at or below 1 s | Sa | NFR-01 |
| TC-N02-1 | 5 first-time users, no help: set up a 2-player game and complete one full turn. Time each with a stopwatch and note where they hesitate | At least 4 of 5 succeed within 2 minutes | Am | NFR-02 |
| TC-N03-1 | Play 100 automated full games with the production RNG through the controller. After every move assert the SDD 3.2 invariants (position 0 to 100, valid current index, one winner at most, nobody on a snake head or ladder base, correct turn order and extra-roll counts). Cap each game at 5,000 rolls | 100 games finish with zero rule violations and none hits the cap. The seed of any failing game is logged so it can be replayed | Ia | NFR-03 |
| TC-N04-1 | On each of the 3 operating systems disable the network (airplane mode or adapter off), launch, and run setup, a few turns, save and resume | Application reaches the Start screen and works normally | Sm | NFR-04, C2 |
| TC-N05-1 | Run the same source tree on Windows 10/11, Ubuntu 22.04+ and macOS 13+. Smoke script: launch, setup, 3 turns, save, exit, relaunch, resume, restart, exit; then a game finished from a save factory state near square 94 | The script passes on every system with no source change | Sm | NFR-05 |
| TC-N06-1 | Run `coverage run -m pytest tests/engine tests/persistence tests/controller` and report by package | Statement coverage of `engine/` is 80% or more. `persistence/` and `controller/` are reported (target 80%, not gating) | Ua | NFR-06 |
| TC-N06-2 | AST scan of `engine/` for Pygame imports; also run the engine tests with the `pygame` module made unavailable | No Pygame import in `engine/`. Engine tests pass without Pygame | Ua | NFR-06, C4 |
| TC-N07-1 | Repeat TC-N01-1 with 4 players | All 50 rolls at or below 1 s. Mean and maximum are reported next to the 2-player result | Sa | NFR-07 |
| TC-N08-1 | 20 save and resume cycles over varied states: 2, 3 and 4 players; positions 0 and 99; last roll `null` and 6; extra roll pending; extra-turn on and off. Compare every field before and after. In 5 of them save again right after resume and compare a third time | All fields identical in all 20 cycles, and a second save/resume changes nothing | Ia | NFR-08 |
| TC-N09-1 | Check the Start, Setup, Game and Result screens at 1280 x 720, 1366 x 768 and 1920 x 1080, windowed and full screen, with a checklist | No clipped, overlapping or unreachable element at any size | Sm | NFR-09 |
| TC-N10-1 | Fault matrix: missing save file, 0-byte file, corrupted file, non-UTF-8 file, read-only save directory, full disk (small temporary file system), invalid names, hostile key sequences | Zero unhandled exceptions or tracebacks. Each case shows a message ("Could not save the game." for E-10) and leaves a usable screen | Ia, Sm | NFR-10, A4 |
| TC-N11-1 | Interrupt a save 10 times: kill the process at random moments, and inject a failure after the temporary file is written but before `os.replace`. Keep a previous valid save | The previous `savegame.json` is byte-identical and loads each time. A leftover `.tmp` file is ignored and replaced by the next save | Ia, Sm | NFR-11 |
| TC-N12-1 | Log frame times during 20 moves (including long snake and ladder moves) on the minimum-hardware machine | Frame rate is 30 FPS or more (per-second average during animation, OI-7) | Sa | NFR-12 |
| TC-N13-1 | Audit every text element at 1280 x 720 | All text is at least 14 pt (about 19 px at 96 DPI, OI-8) | Um | NFR-13 |
| TC-N13-2 | Take screenshots of the Game screen and run them through protanopia, deuteranopia and tritanopia simulators | The 4 tokens can be told apart, and each also shows its number label | Um | NFR-13 |
| TC-N14-1 | Sample the application's memory every second over a 30-minute session that includes 10 save/resume cycles and 4-player games | Peak memory is 200 MB or less | Sa | NFR-14 |
| TC-N14-2 | Save the largest possible state (4 players, longest allowed names) and check the file size | Below 10 KB (10,240 bytes, OI-5) | Ua | NFR-14 |
| TC-N15-1 | Take 60,000 rolls from the production `DiceService` and count each value (expected 10,000 each) | Chi-square statistic (5 degrees of freedom, 5% level) is below 11.07. Rerun policy in R1 | Ua | NFR-15 |


### Functional Requirement Test Cases

| Test Case ID | Requirement | Test Scenario / Input | Expected Result |
|---|---|---|---|
| TC-FR01-2 | FR-01 | Configure 2 valid players and click Start | Game screen opens with 2 tokens at position 0 and P1 as current player |
| TC-FR02-4 | FR-02 | Enter four distinct names and four distinct colours | Accepted. Each token has its own colour and number label 1 to 4 in setup order; names appear as entered after trimming |
| TC-FR03-1 | FR-03 | Scripted RNG returns 4. Click Roll Dice | Dice value 4 is displayed |
| TC-FR04-1 | FR-04 | Token at 0, roll 3 | Position becomes 3 |
| TC-FR05-1 | FR-05 | 3 players, extra-turn off, rolls 2, 3, 5, then 2 more | Turn indicator goes P1, P2, P3, P1. Each roll moves only the current player's token |
| TC-FR06-1 | FR-06 | Token at 14, roll 3, landing on snake head 17 | Final position is 7; token visibly moves to the snake head and then to the tail |
| TC-FR07-1 | FR-07 | Token at 0, roll 4, landing on ladder base 4 | Final position is 14 and the event is LADDER |
| TC-FR08-1 | FR-08 | Extra-turn enabled. P1 rolls 6 and then 2 | P1 gets another roll after the 6; after rolling 2 the position is 8 and turn passes to P2 |
| TC-FR09-1 | FR-09 | Token at 94, roll 6 | Token reaches 100, current player is declared winner and the Result screen appears |
| TC-FR10-1 | FR-10 | Token at 97, roll 4 | Position remains 97, event is OVERSHOOT and turn passes |

### Non-Functional Requirement Test Cases

| Test Case ID | Requirement | Test Scenario / Input | Expected Result |
|---|---|---|---|
| TC-N01-1 | NFR-01 | On the minimum-hardware reference machine, perform 50 rolls and measure response time | All 50 rolls complete within 1 second |
| TC-N02-1 | NFR-02 | 5 first-time users set up a 2-player game and complete one full turn without help | At least 4 of 5 users succeed within 2 minutes |
| TC-N03-1 | NFR-03 | Play 100 automated full games and verify game-state invariants after every move | All 100 games finish with zero rule violations and none reaches the 5,000-roll cap |
| TC-N04-1 | NFR-04 | Disable network access on each supported OS and run setup, gameplay, save and resume | Application works normally without network access |
| TC-N05-1 | NFR-05 | Run the same source tree on Windows 10/11, Ubuntu 22.04+ and macOS 13+ | Smoke test passes on every supported OS with no source-code changes |
| TC-N06-1 | NFR-06 | Run coverage on engine, persistence and controller tests | Statement coverage of `engine/` is at least 80% |
| TC-N08-1 | NFR-08 | Perform 20 save-and-resume cycles over varied game states | All saved fields remain identical after every resume cycle |
| TC-N09-1 | NFR-09 | Check all screens at 1280×720, 1366×768 and 1920×1080 in windowed and full-screen modes | No clipped, overlapping or unreachable UI elements |
| TC-N10-1 | NFR-10 | Test missing/corrupt save files, invalid input, read-only directory, full disk and hostile key sequences | Zero unhandled exceptions or tracebacks; application remains usable |
| TC-N14-1 | NFR-14 | Monitor memory usage during a 30-minute session with save/resume cycles and 4-player games | Peak memory usage is 200 MB or less |


### 5.4 Test Data and Tools

| Item | Use |
|---|---|
| Scripted RNG | Gives exact dice sequences in unit and integration tests (constructor injection only, SDD 3.9) |
| Save factory | Builds any valid or deliberately faulty save with a correct or wrong checksum, using the SDD 3.5 definition |
| Default board (SRS 4.3) | Source of all snake and ladder test data |
| pytest, coverage.py, pytest-timeout | Automation and coverage (NFR-06) |
| psutil | Memory sampling (NFR-14) |
| `SDL_VIDEODRIVER=dummy` | Headless Pygame for integration tests |
| `strace`, Process Monitor, `fs_usage`, `lsof`, `nettop` | Network and file-system tracing (5.1) |
| Colour-blindness simulator (for example Color Oracle) | NFR-13 |
| CI (for example GitHub Actions on Windows, Ubuntu, macOS runners) | Runs the Ua and Ia suites and the static checks on every push |

### 5.5 Defect Management and Regression
Defects are logged in the repository issue tracker with the test case ID, build tag, steps and evidence. Severity: **Critical** (crash, data loss, security bypass, wrong winner), **Major** (a requirement fails with no workaround), **Minor** (a requirement is met but with a visible flaw), **Trivial** (cosmetic). Every fixed defect gets a new or updated automated test where the level allows it. After each fix the affected test cases and the whole Ua and Ia suites are rerun. The system-level smoke script (TC-N05-1) is rerun on each release candidate.

---

## 6. Item Pass/Fail Criteria

A test case **passes** when the actual result equals the expected result and no unexpected exception, traceback or hang occurs. It **fails** otherwise. TC-SEC02-6 is informational: it passes when its outcome is recorded.

The release candidate is accepted when all of these hold:
1. 100% of test cases for H-priority requirements pass.
2. 100% of security test cases (5.1) pass, with RR-1 and RR-2 accepted in writing.
3. Every NFR meets its own measurable criterion in SRS 3.3.
4. Engine statement coverage is 80% or more (NFR-06).
5. There are no open Critical or Major defects. Minor and Trivial defects may remain if each has an owner and a waiver.
6. The M-priority requirements (FR-08, FR-15) pass; if either fails, the release is held or the requirement is formally deferred.
7. Section 14 shows no requirement without an executed, passing test case.

## 7. Suspension Criteria and Resumption Requirements

| Suspend testing when | Resume when |
|---|---|
| The build does not install or does not reach the Start screen (smoke test fails) | A new build passes the smoke test |
| A Critical defect blocks more than 20% of the remaining test cases | The fix is delivered and the blocked cases are rerun |
| The test environment fails (machine, CI runner, trace tool) | Environment is restored and the last completed test case is repeated |
| The SRS or SDD changes in a way that alters expected results | This plan and the affected test cases are updated and re-approved |
| A statistical test fails twice in a row (R1) | The defect is fixed; the statistical tests are rerun |

After a suspension the last failed test case and all cases that share its component are rerun before new cases are started.

## 8. Test Deliverables

| Deliverable | Description |
|---|---|
| Test plan | This document (STP-SNL-001) |
| Test case specifications | Sections 5.1 to 5.3 |
| Automated test suites | `tests/engine`, `tests/persistence`, `tests/controller`, `tests/ui_smoke` (SDD 2.5), the save factory and the scripted RNG |
| CI check scripts | Banned-call scan, import scan, no-Pygame-in-engine check |
| Test logs and evidence | pytest reports, coverage report, timing and frame-rate logs, memory log, trace captures, screenshots |
| Defect log | Issue tracker export |
| Usability study record | Notes and timings from TC-N02-1 |
| Test summary report | Results per test case, coverage, open defects, RR-1 and RR-2 sign-off |

## 9. Testing Tasks

| Task | Depends on | Output |
|---|---|---|
| T1 Review SRS and SDD, settle open items (Section 15) | SRS and SDD baselines | Updated expected results |
| T2 Build the scripted RNG, save factory and CI checks | SDD 3.9 | Test harness |
| T3 Write and run unit tests (engine, persistence, validator) | T2, code in `engine/` and `persistence/` | Ua results, coverage |
| T4 Write and run integration tests, security and fault-injection tests | T3, controller | Ia results |
| T5 Run system tests on the 3 operating systems | Release candidate | Sa and Sm results |
| T6 Run NFR measurements on the reference machine | Release candidate | Timing, FPS, memory logs |
| T7 Run the usability study | Release candidate | Am results |
| T8 Regression run and summary report | T3 to T7 | Test summary report |

## 10. Environmental Needs

| Need | Detail |
|---|---|
| Operating systems | Windows 10 or 11, Ubuntu 22.04 or later, macOS 13 or later (SRS 2.4) |
| Reference machine for NFR-01, NFR-07, NFR-12, NFR-14 | Dual-core 2 GHz CPU, 4 GB RAM, 100 MB free disk, 1280 x 720 display (a virtual machine limited to these values is acceptable) |
| Runtime | Python 3.10 (floor) and the newest stable Python 3, with Pygame 2.x |
| Screens | 1280 x 720, 1366 x 768 and 1920 x 1080 |
| Network | A way to disable it on each machine; tracing tools for SEC-06 |
| Tools | As listed in 5.4 |
| Data | Save factory output in a temporary per-test directory; the real save directory is never used by automated tests |
| People | 5 first-time users for TC-N02-1 who are not on the development team |

## 11. Responsibilities, Staffing and Training

| Area | Responsibility | Owner |
|---|---|---|
| Test lead | Owns this plan, the schedule, the summary report and the defect triage | To be assigned |
| Engine and controller tests | Section 5.2 rule tests, TC-N03-1, TC-N06 | To be assigned |
| Persistence and security tests | Section 5.1, TC-N08-1, TC-N10-1, TC-N11-1 | To be assigned |
| UI, system and NFR tests | TC-UI, TC-FR11 to FR13, TC-N01, TC-N02, TC-N04, TC-N05, TC-N09, TC-N12 to TC-N14 | To be assigned |

A developer does not sign off the tests of the layer that developer wrote; a teammate reviews them. Training needed: pytest and `coverage.py` basics, use of the save factory, and use of one tracing tool per operating system.

## 12. Schedule

Durations are planned working days and are counted from the approval of this plan (T0). Dates are fixed once the semester calendar (constraint C5) is known.

| Phase | Tasks | Planned duration | Entry | Exit |
|---|---|---|---|---|
| P1 Preparation | T1, T2 | T0 + 3 days | Plan approved | Harness and CI checks working |
| P2 Unit testing | T3 | Runs alongside development, ends T0 + 10 days | Modules committed | Engine coverage 80% or more |
| P3 Integration and security testing | T4 | T0 + 10 to T0 + 14 days | Controller complete | All Ia cases pass |
| P4 System and NFR testing | T5, T6 | T0 + 14 to T0 + 18 days | Release candidate tagged | All Sa and Sm cases run |
| P5 Usability study | T7 | T0 + 18 to T0 + 20 days | System tests mostly complete | 5 participants finished |
| P6 Regression and report | T8 | T0 + 20 to T0 + 22 days | All defects fixed or waived | Summary report approved |

## 13. Risks and Contingencies

| ID | Risk | Likelihood | Impact | Contingency |
|---|---|---|---|---|
| R1 | A correct random source fails a 5% chi-square test about 1 run in 20 (TC-N15-1, TC-SEC04-6) | Medium | Low | Rerun once with a fresh 60,000-roll sample. Two failures in a row are treated as a defect |
| R2 | No macOS or Windows machine available for system tests | Medium | High | Use CI runners for the automated cases and borrow a device for TC-N05-1 and TC-SEC06-3 |
| R3 | Minimum-hardware machine not available | Medium | Medium | Use a virtual machine limited to 2 cores and 4 GB; state this in the report |
| R4 | Test-only RNG injection weakens SEC-04 | Low | High | Injection only through the constructor; TC-SEC04-1, TC-SEC04-4 and TC-SEC04-5 check the production build |
| R5 | SRS and SDD ambiguities change expected results (Section 15) | High | Medium | Settle open items in P1; mark affected cases in the report |
| R6 | Fewer than 5 usability participants | Medium | Low | Recruit early; if only 4 are available the 4-of-5 criterion cannot be evaluated and this is reported |
| R7 | Timing tests are flaky on a busy machine | Medium | Medium | Close other programs, repeat runs, keep raw logs, judge the maximum |
| R8 | Hand-edited save files hide the real cause of a rejection | Medium | Medium | Use the save factory so every file breaks exactly one rule |
| R9 | Headless Pygame behaves differently from a real window | Low | Medium | Repeat the critical flows in system tests on a real display |
| R10 | Late defects near the semester deadline | Medium | High | Run the smoke script and Ua/Ia suites on every merge; keep P6 short and reserved |
| R11 | Two instances of the game overwrite each other's save file (not specified) | Low | Low | Excluded (Section 4); noted for the SRS owner |

---

## 14. Traceability to the SRS

Every test case in Section 5 lists the SRS requirement it verifies. The matrices below give the reverse view: for each SRS item, the test cases that cover it. Priority is taken from SRS 3.2 (H = must have, M = should have).

### 14.1 Functional Requirements to Test Cases

| Req | Name | Priority | Test cases |
|---|---|---|---|
| FR-01 | Game Initialization | H | TC-FR01-1, TC-FR01-2, TC-FR01-3, TC-UI1-1 |
| FR-02 | Player Setup | H | TC-FR02-1, TC-FR02-2, TC-FR02-3, TC-FR02-4, TC-SEC01-3, TC-UI1-1 |
| FR-03 | Dice Roll | H | TC-FR03-1, TC-FR03-2, TC-FR03-3, TC-SEC04-2, TC-N15-1 |
| FR-04 | Token Movement | H | TC-FR04-1, TC-FR04-2, TC-FR04-3 |
| FR-05 | Turn Management | H | TC-FR05-1, TC-FR05-2, TC-FR05-3 |
| FR-06 | Snake Encounter | H | TC-FR06-1, TC-FR06-2, TC-FR06-3, TC-FR08-5, TC-BRD-1 |
| FR-07 | Ladder Encounter | H | TC-FR07-1, TC-FR07-2, TC-FR07-3, TC-FR09-3, TC-BRD-1 |
| FR-08 | Extra Turn Rule | M | TC-FR08-1, TC-FR08-2, TC-FR08-3, TC-FR08-4, TC-FR08-5, TC-FR08-6, TC-FR08-7, TC-FR15-2, TC-FR15-4 |
| FR-09 | Win Condition Check | H | TC-FR09-1, TC-FR09-2, TC-FR09-3, TC-FR08-7, TC-FR10-3 |
| FR-10 | Overshoot Handling | H | TC-FR10-1, TC-FR10-2, TC-FR10-3, TC-FR08-6 |
| FR-11 | Board Display | H | TC-FR11-1, TC-FR11-2, TC-FR11-3, TC-BRD-1, TC-N09-1 |
| FR-12 | Turn Indicator | H | TC-FR12-1, TC-FR12-2, TC-FR05-2 |
| FR-13 | Game State Update | H | TC-FR13-1, TC-FR13-2, TC-N01-1 |
| FR-14 | Game Restart | H | TC-FR14-1, TC-FR14-2, TC-FR14-3 |
| FR-15 | Save and Resume | M | TC-FR15-1, TC-FR15-2, TC-FR15-3, TC-FR15-4, TC-FR15-5, TC-FR18-2, TC-FR08-4, TC-N08-1, TC-SEC02-1 |
| FR-16 | Result Display | H | TC-FR16-1, TC-FR16-2, TC-FR16-3, TC-UI3-1 |
| FR-17 | Invalid Action Handling | H | TC-FR17-1, TC-FR17-2, TC-FR17-3, TC-FR17-4, TC-FR17-5, TC-FR18-6 |
| FR-18 | Exit Game | H | TC-FR18-1, TC-FR18-2, TC-FR18-3, TC-FR18-4, TC-FR18-5, TC-FR18-6 |

### 14.2 User Interface, Interfaces, Constraints and Assumptions to Test Cases

| SRS item | Description | Test cases |
|---|---|---|
| UI-1 | Setup screen | TC-UI1-1 |
| UI-2 | Game screen | TC-UI2-1 |
| UI-3 | Result screen | TC-UI3-1 |
| UI-4 | Resume option only when a save exists | TC-UI4-1 |
| SRS 3.1.2 | Hardware interfaces (mouse, keyboard, Space key) | TC-HW-1, TC-FR03-2 |
| SRS 3.1.3 | Software interfaces (Python library, Pygame, file system) | TC-C1-1, TC-C3-1, TC-SEC05-3 |
| SRS 3.1.4 | Communication interfaces: none | TC-SEC06-1, TC-SEC06-2, TC-SEC06-3 |
| C1 | Python and Pygame | TC-C1-1 |
| C2 | No internet connection at any point | TC-N04-1, TC-SEC06-2 |
| C3 | Save files in JSON | TC-C3-1 |
| C4 | Game logic separate from UI | TC-N06-2 |
| C5 | Completed within the semester by a team of four | Not testable (project constraint); tracked in Section 12 |
| A3 | Default board layout only | TC-BRD-1 |
| A4 | User-writable save directory | TC-N10-1 |

### 14.3 Non-Functional Requirements to Test Cases

| Req | Category | Test cases |
|---|---|---|
| NFR-01 | Performance | TC-N01-1, TC-FR13-1 |
| NFR-02 | Usability | TC-N02-1 |
| NFR-03 | Reliability | TC-N03-1 |
| NFR-04 | Availability | TC-N04-1, TC-SEC06-3 |
| NFR-05 | Portability | TC-N05-1 |
| NFR-06 | Maintainability | TC-N06-1, TC-N06-2 |
| NFR-07 | Scalability | TC-N07-1 |
| NFR-08 | Data Integrity | TC-N08-1, TC-FR15-1, TC-SEC02-4 |
| NFR-09 | Compatibility | TC-N09-1 |
| NFR-10 | Error Handling | TC-N10-1, TC-SEC01-4, TC-SEC03-2, TC-SEC03-3, TC-SEC03-8, TC-SECX-2 |
| NFR-11 | Recoverability | TC-N11-1 |
| NFR-12 | Responsiveness | TC-N12-1 |
| NFR-13 | Accessibility | TC-N13-1, TC-N13-2, TC-FR02-4 |
| NFR-14 | Resource Efficiency | TC-N14-1, TC-N14-2, TC-SEC03-1 |
| NFR-15 | Randomness Quality | TC-N15-1, TC-SEC04-5, TC-SEC04-6 |

### 14.4 Security Requirements and Objectives to Test Cases

| Req | Objective | Test cases |
|---|---|---|
| SEC-01 | SO-3 | TC-SEC01-1, TC-SEC01-2, TC-SEC01-3, TC-SEC01-4, TC-SEC01-5, TC-FR02-1 |
| SEC-02 | SO-1 | TC-SEC02-1, TC-SEC02-2, TC-SEC02-3, TC-SEC02-4, TC-SEC02-5, TC-SEC02-6 |
| SEC-03 | SO-1, SO-3 | TC-SEC03-1, TC-SEC03-2, TC-SEC03-3, TC-SEC03-4, TC-SEC03-5, TC-SEC03-6, TC-SEC03-7, TC-SEC03-8, TC-SEC01-5, TC-SEC02-5, TC-SEC04-3, TC-SEC05-2 |
| SEC-04 | SO-2 | TC-SEC04-1, TC-SEC04-2, TC-SEC04-3, TC-SEC04-4, TC-SEC04-5, TC-SEC04-6, TC-N15-1 |
| SEC-05 | SO-3 | TC-SEC05-1, TC-SEC05-2, TC-SEC05-3, TC-SEC03-3 |
| SEC-06 | SO-4 | TC-SEC06-1, TC-SEC06-2, TC-SEC06-3, TC-N04-1 |

| Objective | Requirements | Test cases (families) |
|---|---|---|
| SO-1 Integrity of game state | SEC-02, SEC-03 | TC-SEC02-*, TC-SEC03-*, TC-SECX-1 |
| SO-2 Fairness | SEC-04 | TC-SEC04-* |
| SO-3 Robustness against malformed input | SEC-01, SEC-03, SEC-05 | TC-SEC01-*, TC-SEC03-*, TC-SEC05-*, TC-SECX-1, TC-SECX-2 |
| SO-4 Minimal attack surface | SEC-06 | TC-SEC06-* |

### 14.5 Use Cases to Test Cases (SRS Appendix 4.1 and 4.2)

| Use case | UC ID | Test cases |
|---|---|---|
| Set Up Game, Enter Player Details | not stated | TC-FR01-*, TC-FR02-*, TC-SEC01-*, TC-UI1-1 |
| Roll Dice | UC3 | TC-FR03-*, TC-FR05-*, TC-FR13-1, TC-FR17-1, TC-SEC04-* |
| Move Token | UC4 | TC-FR04-*, TC-FR10-* |
| Apply Snake / Ladder | UC5 | TC-FR06-*, TC-FR07-*, TC-BRD-1 |
| Grant Extra Turn | UC6 | TC-FR08-* |
| Check Win | UC7 | TC-FR09-*, TC-FR10-3 |
| View Result | UC8 | TC-FR16-*, TC-UI3-1 |
| Resume Game | UC10 | TC-FR15-*, TC-UI4-1, TC-SEC02-1 |
| Validate Save File | UC13 | TC-SEC02-*, TC-SEC03-*, TC-SEC05-2 |
| Save Game | not stated | TC-FR15-1, TC-FR15-3, TC-FR15-5, TC-FR17-3, TC-N11-1 |
| Restart Game | not stated | TC-FR14-* |
| Exit Game | not stated | TC-FR18-* |

**Flow coverage of the two written use cases**

| Use case flow | Test cases |
|---|---|
| UC3 main flow 1 and 2: click or Space, value 1 to 6 shown | TC-FR03-1, TC-FR03-2, TC-FR03-3 |
| UC3 step 3, move token (UC4) | TC-FR04-1, TC-FR04-2, TC-FR04-3 |
| UC3 step 4, snake or ladder (UC5) | TC-FR06-1, TC-FR06-2, TC-FR07-1, TC-FR07-2 |
| UC3 step 5, win check (UC7) | TC-FR09-1, TC-FR09-2, TC-FR09-3 |
| UC3 step 6, pass the turn | TC-FR05-1, TC-FR05-2 |
| UC3 precondition (own turn, no animation) | TC-FR17-1, TC-FR17-2, TC-FR17-3 |
| UC3 alternate 2a, overshoot | TC-FR10-1, TC-FR10-2 |
| UC3 alternate 5a, player has won | TC-FR09-1 |
| UC3 alternate 6a, extra turn | TC-FR08-1, TC-FR08-2 |
| UC10 step 1, click Resume | TC-FR15-1 |
| UC10 step 2, validate save (UC13) | TC-SEC02-2, TC-SEC03-4, TC-SEC03-5 |
| UC10 steps 3 and 4, restore and open on saved turn | TC-N08-1, TC-FR12-2, TC-FR15-1 |
| UC10 alternate 2a, validation fails | TC-SEC03-6 |

**Diagram relationship checks.** Roll Dice includes Move Token, which includes Check Win: TC-FR09-1 runs the whole chain. Apply Snake / Ladder extends Move Token: TC-FR06-1 and TC-FR07-1 take the optional branch, TC-FR04-1 does not. Grant Extra Turn extends Roll Dice: TC-FR08-1 takes the branch, TC-FR08-3 does not. Resume Game includes Validate Save File: TC-SEC02-2. Saving during Exit Game is optional: TC-FR18-2 (Save) against TC-FR18-3 (no save).

### 14.6 SDD Error Catalogue to Test Cases

| Code | Condition | Test cases |
|---|---|---|
| E-01 | Invalid name | TC-SEC01-1, TC-SEC01-2, TC-FR02-1 |
| E-02 | Duplicate name or colour | TC-FR02-2, TC-FR02-3 |
| E-03 | Fewer than 2 players | TC-FR01-1 |
| E-04 | Action not allowed in this phase | TC-FR17-5 |
| E-05 | No save file | TC-UI4-1 |
| E-06 | Save file over 10 KB | TC-SEC03-1 |
| E-07 | Invalid JSON or schema | TC-SEC03-2, TC-SEC03-3, TC-SEC03-4, TC-SEC03-8 |
| E-08 | Field out of range | TC-SEC03-5 |
| E-09 | Checksum mismatch | TC-SEC02-2, TC-SEC02-3 |
| E-10 | OS error while saving | TC-N10-1, TC-N11-1 |
| E-11 | Engine invariant broken | TC-SECX-2 |
| E-12 | Unhandled exception in the main loop | TC-SECX-2 |

### 14.7 Coverage Summary

| Category | Items | Items with at least one test case | Test cases |
|---|---|---|---|
| Functional requirements FR-01 to FR-18 | 18 | 18 | 64 (family TC-FR) |
| UI requirements UI-1 to UI-4 | 4 | 4 | 4 |
| Interfaces, constraints and board (TC-HW, TC-C, TC-BRD) | 8 (3.1.2, 3.1.3, 3.1.4, C1 to C4, A3) | 8 | 4 |
| Non-functional requirements NFR-01 to NFR-15 | 15 | 15 | 18 |
| Security requirements SEC-01 to SEC-06 | 6 | 6 | 33 (including 2 design-derived) |
| Security objectives SO-1 to SO-4 | 4 | 4 | shared with SEC |
| Total test cases | | | 123 |

C5 is a project constraint and has no test. No test case is without an SRS reference. The two design-derived security checks (TC-SECX-1, TC-SECX-2) reference SO-1, SO-3 and NFR-10.

---

## 15. Approvals

| Role | Name | Signature | Date |
|---|---|---|---|
| Test lead | | | |
| Development team member (reviewer) | | | |
| SRS / SDD owner | | | |
| Course reviewer | | | |
