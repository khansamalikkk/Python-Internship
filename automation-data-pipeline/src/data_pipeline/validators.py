"""
validators.py
-------------
Validation rules for a single raw record.

A record is expected to (eventually, after cleaning) look like:

    {
        "id": "1001",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "age": "34",
        "country": "us",
        "signup_date": "2023-01-15",
        "amount": "129.99",
        "currency": "USD",
    }

``validate_record`` never raises for bad data - it returns a list of
``ValidationIssue`` describing every problem found, so the caller can
decide whether to keep, quarantine, or drop the record. It only
raises for programmer errors (e.g. passing something that isn't a
dict).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

REQUIRED_FIELDS = ("id", "name", "email", "age", "signup_date", "amount")
MIN_AGE, MAX_AGE = 0, 120
KNOWN_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d")


@dataclass
class ValidationIssue:
    """A single validation problem found in a record."""

    row: Any          # original source row/index (or None if unknown)
    field: str         # field name the issue relates to ("" for record-level)
    code: str          # short machine-readable error code
    message: str       # human-readable explanation
    raw_record: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row": self.row,
            "field": self.field,
            "code": self.code,
            "message": self.message,
            "raw_record": self.raw_record,
        }


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _try_parse_date(value: str) -> datetime | None:
    for fmt in KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _try_parse_number(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def validate_record(record: Dict[str, Any], row: Any = None) -> List[ValidationIssue]:
    """Validate a single raw record and return all issues found.

    An empty list means the record is valid. The record itself is
    NOT mutated.
    """
    if not isinstance(record, dict):
        raise TypeError(f"validate_record expects a dict, got {type(record).__name__}")

    issues: List[ValidationIssue] = []

    def add(field: str, code: str, message: str) -> None:
        issues.append(ValidationIssue(row=row, field=field, code=code, message=message, raw_record=record))

    # 1. Required fields present and non-blank
    for field in REQUIRED_FIELDS:
        if field not in record or _is_blank(record.get(field)):
            add(field, "missing_field", f"Required field '{field}' is missing or blank")

    # If core identity fields are missing there's not much else useful to check.
    if any(i.code == "missing_field" and i.field in ("id", "name") for i in issues):
        return issues

    # 2. id must be an integer (positive)
    if "id" in record and not _is_blank(record.get("id")):
        raw_id = record["id"]
        num = _try_parse_number(raw_id)
        if num is None or num != int(num) or num < 0:
            add("id", "invalid_id", f"id '{raw_id}' is not a non-negative integer")

    # 3. email format
    if "email" in record and not _is_blank(record.get("email")):
        email = str(record["email"]).strip()
        if not EMAIL_RE.match(email):
            add("email", "invalid_email", f"email '{email}' is not a valid email address")

    # 4. age must be an integer within range
    if "age" in record and not _is_blank(record.get("age")):
        raw_age = record["age"]
        num = _try_parse_number(raw_age)
        if num is None or num != int(num):
            add("age", "invalid_age", f"age '{raw_age}' is not an integer")
        elif not (MIN_AGE <= num <= MAX_AGE):
            add("age", "age_out_of_range", f"age {int(num)} is outside allowed range [{MIN_AGE}, {MAX_AGE}]")

    # 5. signup_date must parse against a known format
    if "signup_date" in record and not _is_blank(record.get("signup_date")):
        raw_date = str(record["signup_date"])
        if _try_parse_date(raw_date) is None:
            add("signup_date", "invalid_date", f"signup_date '{raw_date}' does not match a known date format")
        else:
            parsed = _try_parse_date(raw_date)
            if parsed and parsed > datetime.now():
                add("signup_date", "future_date", f"signup_date '{raw_date}' is in the future")

    # 6. amount must be a non-negative number
    if "amount" in record and not _is_blank(record.get("amount")):
        raw_amount = record["amount"]
        num = _try_parse_number(raw_amount)
        if num is None:
            add("amount", "invalid_amount", f"amount '{raw_amount}' is not numeric")
        elif num < 0:
            add("amount", "negative_amount", f"amount {num} is negative")

    return issues


def find_duplicate_ids(records: List[Dict[str, Any]], id_field: str = "id") -> Dict[str, List[int]]:
    """Return a mapping of id-value -> list of source rows that share it.

    Only ids that appear more than once are included. Used by the
    pipeline to flag duplicate records after individual validation.
    """
    seen: Dict[str, List[int]] = {}
    for rec in records:
        key = str(rec.get(id_field, "")).strip()
        if key == "":
            continue
        seen.setdefault(key, []).append(rec.get("_source_row"))
    return {k: v for k, v in seen.items() if len(v) > 1}
