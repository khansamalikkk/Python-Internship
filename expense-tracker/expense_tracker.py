#!/usr/bin/env python3
"""
Expense Tracker CLI
====================

A simple, dependency-free command line expense tracker.

Features
--------
- Add expenses (amount, category, description, date)
- List expenses (optionally filtered by category / month / date range)
- Search expenses by keyword (in description or category)
- Category filtering
- Monthly totals / summary report (overall + per category)
- Delete an expense by id
- Persistent storage in a JSON file
- Input validation and graceful handling of missing/corrupt data files

Usage examples
---------------
    python expense_tracker.py add --amount 25.50 --category food --description "Lunch with team"
    python expense_tracker.py add --amount 1200 --category rent --date 2026-09-01
    python expense_tracker.py list
    python expense_tracker.py list --category food
    python expense_tracker.py list --month 2026-09
    python expense_tracker.py search --keyword lunch
    python expense_tracker.py summary
    python expense_tracker.py summary --month 2026-09
    python expense_tracker.py delete --id 3

Run `python expense_tracker.py -h` or `python expense_tracker.py <command> -h`
for full help on any command.

Author: (your name here)
License: MIT
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DATA_FILE = "expenses.json"
DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"


# ---------------------------------------------------------------------------
# Storage layer
# ---------------------------------------------------------------------------

class ExpenseStorage:
    """Handles reading and writing the expenses JSON file safely.

    Design notes:
    - If the file does not exist, an empty store is created on first save.
    - If the file exists but contains invalid/corrupt JSON, the corrupt file
      is backed up (with a timestamp suffix) instead of being silently
      overwritten or crashing the program, and a fresh empty store is used.
    - All records are validated again on load, in case the file was edited
      by hand and now contains malformed rows; malformed rows are skipped
      with a warning rather than crashing the whole program.
    """

    def __init__(self, path: str = DEFAULT_DATA_FILE):
        self.path = path

    def load(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except OSError as exc:
            print(f"[Error] Could not read data file '{self.path}': {exc}")
            print("[Info] Starting with an empty in-memory expense list.")
            return []

        if not content:
            # Empty file is treated as an empty (valid) store.
            return []

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            self._quarantine_corrupt_file(exc)
            return []

        if not isinstance(data, list):
            print(
                f"[Warning] Data file '{self.path}' did not contain a JSON "
                "list as expected. Treating it as corrupt."
            )
            self._quarantine_corrupt_file(reason="unexpected JSON structure")
            return []

        clean_records = []
        for i, record in enumerate(data):
            valid, reason = self._validate_record_shape(record)
            if valid:
                clean_records.append(record)
            else:
                print(
                    f"[Warning] Skipping malformed record at index {i} "
                    f"in '{self.path}': {reason}"
                )
        return clean_records

    def save(self, expenses: List[Dict[str, Any]]) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)

        tmp_path = f"{self.path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(expenses, f, indent=2, ensure_ascii=False)
            # Atomic-ish replace: write to temp file then rename over target.
            os.replace(tmp_path, self.path)
        except OSError as exc:
            print(f"[Error] Failed to save expenses to '{self.path}': {exc}")
            raise

    def _quarantine_corrupt_file(
        self, exc: Optional[json.JSONDecodeError] = None, reason: str = ""
    ) -> None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{self.path}.corrupt.{timestamp}.bak"
        try:
            shutil.copy2(self.path, backup_path)
            msg_detail = f"({exc})" if exc else f"({reason})" if reason else ""
            print(
                f"[Warning] Data file '{self.path}' is corrupt {msg_detail}. "
                f"A backup was saved to '{backup_path}'. "
                "Starting with a fresh, empty expense list."
            )
        except OSError as copy_exc:
            print(
                f"[Warning] Data file '{self.path}' is corrupt and could not "
                f"be backed up ({copy_exc}). Starting with an empty list."
            )

    @staticmethod
    def _validate_record_shape(record: Any) -> (bool, str):
        if not isinstance(record, dict):
            return False, "record is not a JSON object"
        required = {"id", "date", "amount", "category", "description"}
        missing = required - record.keys()
        if missing:
            return False, f"missing fields: {sorted(missing)}"
        if not isinstance(record["amount"], (int, float)):
            return False, "amount is not numeric"
        try:
            datetime.strptime(record["date"], DATE_FORMAT)
        except (ValueError, TypeError):
            return False, "date is not in YYYY-MM-DD format"
        return True, ""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when user-provided input fails validation."""


def validate_amount(raw_amount: str) -> float:
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        raise ValidationError(f"Amount '{raw_amount}' is not a valid number.")
    if amount <= 0:
        raise ValidationError("Amount must be a positive number greater than 0.")
    # Round to 2 decimal places for currency sanity.
    return round(amount, 2)


def validate_category(raw_category: str) -> str:
    category = (raw_category or "").strip()
    if not category:
        raise ValidationError("Category cannot be empty.")
    if len(category) > 40:
        raise ValidationError("Category must be 40 characters or fewer.")
    return category


def validate_description(raw_description: Optional[str]) -> str:
    description = (raw_description or "").strip()
    if len(description) > 200:
        raise ValidationError("Description must be 200 characters or fewer.")
    return description


def validate_date(raw_date: Optional[str]) -> str:
    if not raw_date:
        return datetime.now().strftime(DATE_FORMAT)
    try:
        parsed = datetime.strptime(raw_date, DATE_FORMAT)
    except ValueError:
        raise ValidationError(
            f"Date '{raw_date}' is invalid. Use YYYY-MM-DD format, e.g. 2026-09-07."
        )
    return parsed.strftime(DATE_FORMAT)


def validate_month(raw_month: Optional[str]) -> Optional[str]:
    if not raw_month:
        return None
    try:
        parsed = datetime.strptime(raw_month, MONTH_FORMAT)
    except ValueError:
        raise ValidationError(
            f"Month '{raw_month}' is invalid. Use YYYY-MM format, e.g. 2026-09."
        )
    return parsed.strftime(MONTH_FORMAT)


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def next_id(expenses: List[Dict[str, Any]]) -> int:
    if not expenses:
        return 1
    return max(e["id"] for e in expenses) + 1


def cmd_add(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    try:
        amount = validate_amount(args.amount)
        category = validate_category(args.category)
        description = validate_description(args.description)
        date = validate_date(args.date)
    except ValidationError as exc:
        print(f"[Error] {exc}")
        return 1

    expenses = storage.load()
    record = {
        "id": next_id(expenses),
        "date": date,
        "amount": amount,
        "category": category,
        "description": description,
    }
    expenses.append(record)
    storage.save(expenses)
    print(
        f"Added expense #{record['id']}: {date} | {category} | "
        f"{amount:.2f} | {description or '(no description)'}"
    )
    return 0


def cmd_list(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    try:
        month = validate_month(args.month)
        start = validate_date(args.start) if args.start else None
        end = validate_date(args.end) if args.end else None
    except ValidationError as exc:
        print(f"[Error] {exc}")
        return 1

    expenses = storage.load()
    filtered = _apply_filters(
        expenses,
        category=args.category,
        month=month,
        start=start,
        end=end,
    )
    _print_table(filtered)
    if filtered:
        total = sum(e["amount"] for e in filtered)
        print(f"\nTotal ({len(filtered)} record(s)): {total:.2f}")
    return 0


def cmd_search(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    keyword = (args.keyword or "").strip().lower()
    if not keyword:
        print("[Error] Please provide a non-empty --keyword to search for.")
        return 1

    expenses = storage.load()
    matches = [
        e
        for e in expenses
        if keyword in e["description"].lower() or keyword in e["category"].lower()
    ]
    _print_table(matches)
    print(f"\n{len(matches)} match(es) for '{args.keyword}'.")
    return 0


def cmd_summary(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    try:
        month = validate_month(args.month)
    except ValidationError as exc:
        print(f"[Error] {exc}")
        return 1

    expenses = storage.load()
    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]

    if not expenses:
        scope = f" for {month}" if month else ""
        print(f"No expenses found{scope}.")
        return 0

    by_month: Dict[str, float] = {}
    by_category: Dict[str, float] = {}
    for e in expenses:
        m = e["date"][:7]  # YYYY-MM
        by_month[m] = by_month.get(m, 0.0) + e["amount"]
        by_category[e["category"]] = by_category.get(e["category"], 0.0) + e["amount"]

    print("Monthly totals:")
    for m in sorted(by_month):
        print(f"  {m}: {by_month[m]:.2f}")

    print("\nTotals by category:")
    for cat in sorted(by_category, key=lambda c: -by_category[c]):
        print(f"  {cat:<20} {by_category[cat]:.2f}")

    grand_total = sum(e["amount"] for e in expenses)
    print(f"\nGrand total: {grand_total:.2f} across {len(expenses)} record(s)")
    return 0


def cmd_delete(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    expenses = storage.load()
    remaining = [e for e in expenses if e["id"] != args.id]
    if len(remaining) == len(expenses):
        print(f"[Error] No expense found with id {args.id}.")
        return 1
    storage.save(remaining)
    print(f"Deleted expense #{args.id}.")
    return 0


def cmd_categories(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    expenses = storage.load()
    cats = sorted({e["category"] for e in expenses})
    if not cats:
        print("No categories recorded yet.")
        return 0
    print("Categories in use:")
    for c in cats:
        print(f"  - {c}")
    return 0


def cmd_export(args: argparse.Namespace, storage: ExpenseStorage) -> int:
    expenses = storage.load()
    if not expenses:
        print("[Info] No expenses to export.")
        return 0
    out_path = args.output
    try:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["id", "date", "amount", "category", "description"]
            )
            writer.writeheader()
            for e in sorted(expenses, key=lambda x: x["date"]):
                writer.writerow(e)
    except OSError as exc:
        print(f"[Error] Could not write CSV export to '{out_path}': {exc}")
        return 1
    print(f"Exported {len(expenses)} record(s) to '{out_path}'.")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_filters(
    expenses: List[Dict[str, Any]],
    category: Optional[str] = None,
    month: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Dict[str, Any]]:
    result = expenses
    if category:
        cat_lower = category.strip().lower()
        result = [e for e in result if e["category"].lower() == cat_lower]
    if month:
        result = [e for e in result if e["date"].startswith(month)]
    if start:
        result = [e for e in result if e["date"] >= start]
    if end:
        result = [e for e in result if e["date"] <= end]
    return sorted(result, key=lambda e: e["date"])


def _print_table(expenses: List[Dict[str, Any]]) -> None:
    if not expenses:
        print("No matching expenses found.")
        return
    header = f"{'ID':<4} {'Date':<12} {'Category':<15} {'Amount':>10}  Description"
    print(header)
    print("-" * len(header))
    for e in expenses:
        print(
            f"{e['id']:<4} {e['date']:<12} {e['category']:<15} "
            f"{e['amount']:>10.2f}  {e['description']}"
        )


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense_tracker.py",
        description="A simple command-line expense tracker with persistent JSON storage.",
    )
    parser.add_argument(
        "--file",
        dest="data_file",
        default=DEFAULT_DATA_FILE,
        help=f"Path to the JSON data file (default: {DEFAULT_DATA_FILE})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a new expense")
    p_add.add_argument("--amount", required=True, help="Expense amount, e.g. 25.50")
    p_add.add_argument("--category", required=True, help="Expense category, e.g. food")
    p_add.add_argument("--description", default="", help="Optional description/note")
    p_add.add_argument(
        "--date", default=None, help="Date in YYYY-MM-DD (default: today)"
    )
    p_add.set_defaults(func=cmd_add)

    p_list = subparsers.add_parser("list", help="List expenses, with optional filters")
    p_list.add_argument("--category", default=None, help="Filter by category")
    p_list.add_argument("--month", default=None, help="Filter by month, YYYY-MM")
    p_list.add_argument("--start", default=None, help="Start date, YYYY-MM-DD")
    p_list.add_argument("--end", default=None, help="End date, YYYY-MM-DD")
    p_list.set_defaults(func=cmd_list)

    p_search = subparsers.add_parser(
        "search", help="Search expenses by keyword in description or category"
    )
    p_search.add_argument("--keyword", required=True, help="Keyword to search for")
    p_search.set_defaults(func=cmd_search)

    p_summary = subparsers.add_parser(
        "summary", help="Show monthly totals and per-category totals"
    )
    p_summary.add_argument(
        "--month", default=None, help="Restrict summary to one month, YYYY-MM"
    )
    p_summary.set_defaults(func=cmd_summary)

    p_delete = subparsers.add_parser("delete", help="Delete an expense by id")
    p_delete.add_argument("--id", required=True, type=int, help="Expense id to delete")
    p_delete.set_defaults(func=cmd_delete)

    p_categories = subparsers.add_parser(
        "categories", help="List all distinct categories currently in use"
    )
    p_categories.set_defaults(func=cmd_categories)

    p_export = subparsers.add_parser("export", help="Export all expenses to a CSV file")
    p_export.add_argument(
        "--output", default="expenses_export.csv", help="Output CSV file path"
    )
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = ExpenseStorage(args.data_file)
    try:
        return args.func(args, storage)
    except ValidationError as exc:
        print(f"[Error] {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level safety net for a CLI tool
        print(f"[Fatal Error] An unexpected error occurred: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
