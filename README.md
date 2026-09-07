# Python Mini-Projects
This repository contains standalone Python command-line projects,
each built following industry-standard practices: clean architecture,
input validation, custom exceptions, logging where relevant, and (where
applicable) a full unit test suite.
| Project | Description | Docs |
|---|---|---|
| [Student Record System](./student-record-system) | CRUD-based student record manager with JSON persistence | [README](./student-record-system/README.md) |
| [Number Guessing Game](./number-guessing-game) | CLI number guessing game with selectable difficulty | [README](./number-guessing-game/README.md) |
| [API Data Processing](./api-data-processing) | Fetches a public JSON API, cleans data, calculates stats, and exports to CSV | [README](./api-data-processing/README.md) |
| [Expense Tracker](./expense-tracker) | CLI expense tracker with add/list/search, category filtering, monthly totals, and JSON persistence | [README](./expense-tracker/README.md) |
Each project is self-contained in its own folder with its own dependencies, tests (where applicable), and README — so each can be run, tested, or extracted into its own repository independently.
## Repository Structure
```
.
├── student-record-system/
│   ├── src/student_record_system/
│   ├── tests/
|   ├── .gitignore
│   ├── README.md
│   ├── Report.pdf
│   ├── Tutorial Video.mp3
│   ├── pyproject.toml
│   └── requirements.txt
├── number-guessing-game/
│   ├── src/number_guessing_game/
│   ├── tests/
│   ├── .gitignore
│   ├── README.md
│   ├── Report.pdf
│   ├── Tutorial Video.mp3
│   ├── pyproject.toml
│   └── requirements.txt
├── api-data-processing/
│   ├── process_api_data.py   # Main script
│   ├── sample_data.json      # Local fallback dataset (same schema as the API)
│   ├── README.md
│   ├── Report.pdf
│   ├── Tutorial.mp4
│   ├── output_data.csv
│   ├── summary_stats.json
│   ├── .gitignore
│   └── LESSONS.md
├── expense-tracker/
│   ├── expense_tracker.py    # Main CLI script
│   ├── expenses.json         # Sample/persistent data file
│   ├── README.md
│   ├── Report.pdf
│   ├── Tutorial.mp4
│   ├── LESSONS.md
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
```bash
cd api-data-processing
python process_api_data.py
```
```bash
cd expense-tracker
python expense_tracker.py add --amount 25.50 --category food --description "Lunch with team"
python expense_tracker.py list
python expense_tracker.py summary
```
## Running All Tests
```bash
# From the repo root
cd student-record-system && python -m pytest tests/ -v && cd ..
cd number-guessing-game && python -m pytest tests/ -v && cd ..
```
## License
MIT — see [LICENSE](./LICENSE).
