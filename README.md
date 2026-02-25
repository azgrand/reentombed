# ReEntombed v0.0.1 🕹️

A dynamically resizing, procedurally generated maze game built with Python and Pygame. It features synthetic sound effects, a scoring system, and a chaotic secret AI mode!

## Features
* **Procedural Generation:** Every maze is uniquely generated using the Randomized Depth-First Search algorithm.
* **Responsive UI:** The maze dynamically resizes and centers itself to fit the window if you maximize it.
* **Synthetic Audio:** All sound effects (movement, victory, background music) are generated purely via math (sine waves). No external audio files are required!
* **Secret AI Mode:** Let the computer solve the maze for you at light speed while leaving a neon trail.

## Installation

1. Clone this repository or download the source code.
2. (Optional but recommended) Create a virtual environment. If you are using PyCharm, it usually creates a `.venv` folder for you automatically.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the game by executing the `main.py` file from the root directory:
   ```bash
   python main.py
   ```

### Controls
* **Arrow Keys:** Move the green player square to the red goal.
* **'A' Key:** (Secret) Press 'A' *before* making any manual moves to activate the chaotic Auto-Solve AI.
* **'N' Key:** Generate a new maze when you reach the Game Over screen.
* **ESC Key:** Exit the game.