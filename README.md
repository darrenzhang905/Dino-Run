# Dino Run

## Description

This game is a personal adaptation of Google Chrome's Dinosaur Game with additional features such as powerups and beat detection. The game is completely controlled by the player's voice. High pitch is for jumping and low pitch is for ducking. If the player wants to listen to music while playing the game, they can upload a .wav file and the obstacles generate based on that beat.

## Setup Instructions

### Setting up a Python Environment

1. Create a new virtual environment:

   ```
   python -m venv dinorun_env
   ```

2. Activate virtual environment:

   ```
   source dinorun_env/bin/activate
   ```

### Installing Dependencies

Once your Python environment is set up and activated, install the required packages:

```
pip install -r requirements.txt
```

## How to run

After setting up your environment and installing dependencies:

1. Run the game file:
   ```
   python dino_run.py
   ```

## Shortcuts

- **P key**: Pause/Unpause the game
- **Esc key**: While paused, press to return to the main menu

## Features

- Voice-controlled gameplay (high pitch to jump, low pitch to duck)
- Power-ups:
  - Health boost
  - Score multiplier
  - Invincibility
- Music integration (upload .wav files to generate obstacles based on the beat)
- Bot mode for automatic play
- Local scoreboard

## Music

Place the .wav files in the "music" folder to use them in the game.
