# Number Guessing Game

A command-line Number Guessing Game built in Python, following industry
best practices: game logic fully decoupled from I/O, `Enum`-based
difficulty configuration, custom exceptions, and a comprehensive unit
test suite using a seeded RNG for determinism.

## Features

- Three difficulty levels:
  | Level  | Range   | Attempts |
  |--------|---------|----------|
  | Easy   | 1–50    | 10       |
  | Medium | 1–100   | 7        |
  | Hard   | 1–500   | 10       |
- Feedback after every guess (too low / too high / correct)
- Tracks attempts used/remaining and full guess history
- Reveals the answer if the player runs out of attempts
- "Play again" loop so the player can start new rounds without restarting the program
- Input validation (rejects non-numeric input and out-of-range guesses)

## Project Structure

```
number-guessing-game/
├── src/
│   └── number_guessing_game/
│       ├── __init__.py       # Package exports
│       ├── game.py           # Core game logic (no I/O — fully testable)
│       └── cli.py            # Command-line interface (entry point)
├── tests/
│   └── test_number_guessing_game.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Design Notes

- **Logic/UI separation**: `game.py` contains zero `print()`/`input()`
  calls. `NumberGuessingGame` is a plain state machine that can be driven
  by any front end (CLI today; a GUI or web API could reuse it unchanged).
- **Testability via dependency injection**: `NumberGuessingGame` accepts
  an optional `random.Random` instance, so tests can seed the RNG and get
  fully deterministic, reproducible results instead of relying on chance.
- **`Enum`-based configuration** (`Difficulty`) keeps the range/attempt
  presets centralized and self-documenting instead of scattering magic
  numbers through the code.
- **Custom exceptions** (`InvalidGuessError`, `GameAlreadyOverError`) make
  invalid usage explicit and easy for callers to handle.

## Requirements

- Python 3.9+
- No external runtime dependencies (standard library only)
- `pytest` for running the test suite

## Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd number-guessing-game

# (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies (only needed for running tests)
pip install -r requirements.txt
```

## Usage

Run the CLI directly:

```bash
python -m number_guessing_game.cli
```

Or, if installed as a package (`pip install -e .`):

```bash
number-guessing-game
```

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

The test suite covers difficulty configuration, win/loss conditions,
range validation, attempt tracking, guess history, and post-game-over
behavior (12 tests), using a seeded RNG for determinism.

## Example Session

```
====================================
      NUMBER GUESSING GAME
====================================

Select difficulty:
1. Easy   (1-50, 10 attempts)
2. Medium (1-100, 7 attempts)
3. Hard   (1-500, 10 attempts)
Choice (1-3): 2

I'm thinking of a number between 1 and 100. You have 7 attempts. Good luck!

Enter your guess (1-100): 50
Too high! Attempts remaining: 6
Enter your guess (1-100): 25
Too low! Attempts remaining: 5
Enter your guess (1-100): 37
Correct! You guessed it in 3 attempt(s). 🎉

Play again? (y/n): n
Thanks for playing. Goodbye!
```

## Possible Future Enhancements

- Track and persist high scores (fewest attempts) across sessions
- Add a "hint" mode (e.g. tells the player if the number is even/odd)
- Build a GUI (tkinter) or web (Flask) front end on top of the existing `game.py`

## License

MIT — see repository root for details.
