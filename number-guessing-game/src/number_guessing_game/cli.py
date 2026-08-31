"""Command-line interface for the Number Guessing Game."""
from __future__ import annotations

from .game import (
    Difficulty,
    GuessResult,
    InvalidGuessError,
    NumberGuessingGame,
)

DIFFICULTY_MENU = {
    "1": Difficulty.EASY,
    "2": Difficulty.MEDIUM,
    "3": Difficulty.HARD,
}


def choose_difficulty() -> Difficulty:
    print("\nSelect difficulty:")
    print(f"1. Easy   (1-{Difficulty.EASY.upper_bound}, {Difficulty.EASY.max_attempts} attempts)")
    print(f"2. Medium (1-{Difficulty.MEDIUM.upper_bound}, {Difficulty.MEDIUM.max_attempts} attempts)")
    print(f"3. Hard   (1-{Difficulty.HARD.upper_bound}, {Difficulty.HARD.max_attempts} attempts)")
    while True:
        choice = input("Choice (1-3): ").strip()
        if choice in DIFFICULTY_MENU:
            return DIFFICULTY_MENU[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")


def prompt_guess(difficulty: Difficulty) -> int:
    while True:
        raw = input(
            f"Enter your guess ({difficulty.lower_bound}-{difficulty.upper_bound}): "
        ).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def play_round() -> None:
    difficulty = choose_difficulty()
    game = NumberGuessingGame(difficulty)
    print(
        f"\nI'm thinking of a number between {difficulty.lower_bound} and "
        f"{difficulty.upper_bound}. You have {difficulty.max_attempts} attempts. Good luck!\n"
    )

    while not game.is_over:
        guess_value = prompt_guess(difficulty)
        try:
            result = game.guess(guess_value)
        except InvalidGuessError as exc:
            print(f"Error: {exc}")
            continue

        if result == GuessResult.CORRECT:
            print(f"\nCorrect! You guessed it in {game.attempts_used} attempt(s). 🎉")
        elif result == GuessResult.TOO_LOW:
            print(f"Too low! Attempts remaining: {game.attempts_remaining}")
        else:
            print(f"Too high! Attempts remaining: {game.attempts_remaining}")

    if not game.won:
        print(f"\nOut of attempts! The number was {game.secret_number}.")


def main() -> None:
    print("=" * 36)
    print("      NUMBER GUESSING GAME")
    print("=" * 36)

    while True:
        play_round()
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing. Goodbye!")
            break


if __name__ == "__main__":
    main()
