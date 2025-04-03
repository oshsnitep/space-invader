# Space Invader Game

## Overview
Space Invader is a classic arcade-style game where players control a spaceship to shoot down enemy invaders. The game features simple graphics and sound effects, providing an engaging experience for players of all ages.

## Project Structure
```
space-invader
├── assets
│   ├── images
│   │   ├── player.png        # Image file for the player character
│   │   └── enemy.png         # Image file for the enemy character
│   └── sounds
│       └── shoot.wav         # Sound file for shooting action
├── src
│   ├── main.py               # Entry point of the application
│   ├── game.py               # Contains the Game class for game logic
│   ├── settings.py           # Manages game settings and constants
│   └── sprites.py            # Manages game sprites (Player and Enemy classes)
└── README.md                 # Documentation for the project
```

## How to Run the Game
1. Ensure you have Python installed on your machine.
2. Navigate to the `src` directory in your terminal.
3. Run the game using the following command:
   ```
   python main.py
   ```

## Controls
- Use the left and right arrow keys to move the player.
- Press the spacebar to shoot.

## Dependencies
Make sure to install any required libraries before running the game. You can do this by running:
```
pip install -r requirements.txt
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.