# Python Mini-Projects

This repository contains two standalone Python command-line projects,
each built following industry-standard practices: clean architecture,
input validation, custom exceptions, logging where relevant, and a full
unit test suite.

| Project | Description | Docs |
|---|---|---|
| [Student Record System](./student-record-system) | CRUD-based student record manager with JSON persistence | [README](./student-record-system/README.md) |
| [Number Guessing Game](./number-guessing-game) | CLI number guessing game with selectable difficulty | [README](./number-guessing-game/README.md) |

Each project is self-contained in its own folder with its own
`pyproject.toml`, `requirements.txt`, tests, and README — so each can be
run, tested, or extracted into its own repository independently.

## Repository Structure

```
.
├── Python-Internship/
│   ├── src/student_record_system/
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── README.md
│   └── .gitignore
├── number-guessing-game/
│   ├── src/number_guessing_game/
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── README.md
│   └── .gitignore
├── .gitignore
├── LICENSE
└── README.md
```

## Quick Start

Each project is independent. Pick a folder and follow its README, e.g.:

```bash
cd student-record-system
pip install -r requirements.txt
python -m student_record_system.cli
```

```bash
cd number-guessing-game
pip install -r requirements.txt
python -m number_guessing_game.cli
```

## Running All Tests

```bash
# From the repo root
cd student-record-system && python -m pytest tests/ -v && cd ..
cd number-guessing-game && python -m pytest tests/ -v && cd ..
```

## License

MIT — see [LICENSE](./LICENSE).
