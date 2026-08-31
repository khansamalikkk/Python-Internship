"""Number Guessing Game package."""
from .game import (
    Difficulty,
    GuessResult,
    GuessRecord,
    NumberGuessingGame,
    GameAlreadyOverError,
    InvalidGuessError,
)

__version__ = "1.0.0"
__all__ = [
    "Difficulty",
    "GuessResult",
    "GuessRecord",
    "NumberGuessingGame",
    "GameAlreadyOverError",
    "InvalidGuessError",
]
