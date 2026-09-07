# CLI Expense Tracker

A dependency-free Python command-line tool for tracking personal expenses,
with persistent JSON storage, input validation, and protection against
missing or corrupted data files.

## Features

- **Add** expenses with amount, category, description, and date
- **List** expenses, optionally filtered by category, month, or date range
- **Search** expenses by keyword (matches description or category)
- **Category filtering** (via `list --category ...`)
- **Monthly totals** and per-category totals via `summary`
- **Delete** an expense by id
- **Export** all expenses to CSV
- **Persistent storage** in a JSON file (default: `expenses.json`)
- **Input validation**: amount must be a positive number, dates must be
  valid `YYYY-MM-DD`, category/description length limits enforced
- **Corrupt/missing file handling**: a missing data file is treated as an
  empty tracker; a corrupt or unreadable data file is automatically backed
  up (e.g. `expenses.json.corrupt.20260907161437.bak`) instead of crashing
  or silently discarding data, and the program continues with a fresh store

## Requirements

- Python 3.8+
- No third-party packages required (standard library only)

## Installation

```bash
git clone <this-repo-url>
cd expense-tracker
```

No `pip install` needed — everything uses the Python standard library.

## Usage

All commands accept an optional `--file path/to/data.json` to use a data
file other than the default `expenses.json` (useful for tests or multiple
ledgers).

### Add an expense

```bash
python expense_tracker.py add --amount 25.50 --category food --description "Lunch with team"
python expense_tracker.py add --amount 1200 --category rent --date 2026-09-01
```

- `--amount` (required): positive number, e.g. `25.50`
- `--category` (required): short label, e.g. `food`, `rent`, `transport`
- `--description` (optional): free text note, up to 200 characters
- `--date` (optional): `YYYY-MM-DD`; defaults to today if omitted

### List expenses

```bash
python expense_tracker.py list
python expense_tracker.py list --category food
python expense_tracker.py list --month 2026-09
python expense_tracker.py list --start 2026-09-01 --end 2026-09-15
```

### Search expenses

```bash
python expense_tracker.py search --keyword lunch
```

Searches (case-insensitively) inside both the description and the category.

### Monthly / category summary

```bash
python expense_tracker.py summary
python expense_tracker.py summary --month 2026-09
```

Prints totals grouped by month and totals grouped by category, plus a grand
total.

### Delete an expense

```bash
python expense_tracker.py delete --id 3
```

### List categories in use

```bash
python expense_tracker.py categories
```

### Export to CSV

```bash
python expense_tracker.py export --output expenses_export.csv
```

## Data storage format

Expenses are stored as a JSON array of objects in `expenses.json`:

```json
[
  {
    "id": 1,
    "date": "2026-09-01",
    "amount": 25.5,
    "category": "food",
    "description": "Lunch with team"
  }
]
```

## Error handling behavior

| Situation | Behavior |
|---|---|
| Data file does not exist | Treated as an empty tracker; file is created on first save |
| Data file exists but is empty | Treated as an empty tracker |
| Data file contains invalid JSON | Original file is backed up with a timestamped `.corrupt.*.bak` suffix; program continues with an empty tracker |
| Data file is valid JSON but not a list | Same as above (backed up, treated as corrupt) |
| Individual record missing required fields or wrong types | That single record is skipped with a warning; the rest of the file still loads |
| Invalid amount / date / category on `add` | Command is rejected with a clear error message and non-zero exit code; nothing is written |
| Deleting a non-existent id | Command is rejected with an error message; no changes are made |

## Project structure

```
expense-tracker/
├── expense_tracker.py   # Main CLI application (single file, stdlib only)
├── README.md            # This file
└── LESSONS.md           # Key lessons / possible improvements
```

## Running tests manually

There is no external test framework dependency; the script was validated
manually by exercising every command, including:

- Adding valid and invalid expenses (bad amount, negative amount, bad date,
  empty category)
- Listing with no filters, category filter, month filter, and date range
- Searching with a matching and non-matching keyword
- Generating summaries across multiple months and categories
- Deleting an existing id and a non-existent id
- Running against a missing data file
- Running against a corrupt (invalid JSON) data file
- Running against a JSON file that is valid JSON but not a list

## License

MIT — feel free to reuse and adapt.
