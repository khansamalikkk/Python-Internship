"""Core game logic for the Number Guessing Game.

Kept free of any I/O (no print/input calls) so it can be tested in
isolation and reused by different front ends (CLI, GUI, web, etc.).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Difficulty(Enum):
    """Difficulty presets: (lower_bound, upper_bound, max_attempts)."""

    EASY = (1, 50, 10)
    MEDIUM = (1, 100, 7)
    HARD = (1, 500, 10)

    @property
    def lower_bound(self) -> int:
        return self.value[0]

    @property
    def upper_bound(self) -> int:
        return self.value[1]

    @property
    def max_attempts(self) -> int:
        return self.value[2]


class GuessResult(Enum):
    TOO_LOW = "too_low"
    TOO_HIGH = "too_high"
    CORRECT = "correct"


class GameAlreadyOverError(Exception):
    """Raised when a guess is made after the game has already ended."""


class InvalidGuessError(Exception):
    """Raised when a guess falls outside the valid range."""


@dataclass
class GuessRecord:
    value: int
    result: GuessResult


@dataclass
class NumberGuessingGame:
    """A single round of the number guessing game.

    Usage:
        game = NumberGuessingGame(Difficulty.MEDIUM)
        result = game.guess(50)
    """

    difficulty: Difficulty = Difficulty.MEDIUM
    _secret_number: int = field(init=False, repr=False)
    _attempts_used: int = field(init=False, default=0)
    _history: List[GuessRecord] = field(init=False, default_factory=list)
    _is_over: bool = field(init=False, default=False)
    _won: bool = field(init=False, default=False)
    _rng: Optional[random.Random] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        rng = self._rng or random
        self._secret_number = rng.randint(
            self.difficulty.lower_bound, self.difficulty.upper_bound
        )

    @property
    def attempts_used(self) -> int:
        return self._attempts_used

    @property
    def attempts_remaining(self) -> int:
        return self.difficulty.max_attempts - self._attempts_used

    @property
    def is_over(self) -> bool:
        return self._is_over

    @property
    def won(self) -> bool:
        return self._won

    @property
    def history(self) -> List[GuessRecord]:
        return list(self._history)

    @property
    def secret_number(self) -> int:
        """Exposes the secret number — intended for use only after game over
        (e.g. to reveal the answer), or in tests."""
        return self._secret_number

    def guess(self, value: int) -> GuessResult:
        """Submit a guess. Returns the result and updates internal game state.

        Raises:
            GameAlreadyOverError: if called after the game has ended.
            InvalidGuessError: if the guess is outside the configured range.
        """
        if self._is_over:
            raise GameAlreadyOverError("The game has already ended.")
        if not (self.difficulty.lower_bound <= value <= self.difficulty.upper_bound):
            raise InvalidGuessError(
                f"Guess must be between {self.difficulty.lower_bound} "
                f"and {self.difficulty.upper_bound}."
            )

        self._attempts_used += 1

        if value < self._secret_number:
            result = GuessResult.TOO_LOW
        elif value > self._secret_number:
            result = GuessResult.TOO_HIGH
        else:
            result = GuessResult.CORRECT
            self._won = True
            self._is_over = True

        self._history.append(GuessRecord(value=value, result=result))

        if not self._is_over and self._attempts_used >= self.difficulty.max_attempts:
            self._is_over = True

        return result
