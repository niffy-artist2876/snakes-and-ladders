# snake-game
Team members: 
1) Name: shishir hegde  SRN: PES1UG24CS438
2) Name: Shaurya singh SRN: PES1UG24CS437
3) Name: Sharat doddihal SRN: PES1UG24CS430
4) Name: Shashank palcharla SRN: PES1UG24CS436

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



