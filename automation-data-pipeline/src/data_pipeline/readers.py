"""
readers.py
----------
Load raw records from CSV or JSON files into a uniform in-memory
representation: a list of dictionaries, one per record.

Design notes:
- Readers do NOT validate or clean data. They only parse the file
  format and hand back raw dict rows, so validation/cleaning logic
  stays in one place regardless of the input format.
- Row numbers are 1-indexed and attached under a reserved key
  ``_source_row`` so later error messages can point back at the
  original file line/element.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

SOURCE_ROW_KEY = "_source_row"


class UnsupportedFileTypeError(ValueError):
    """Raised when a file extension isn't one we know how to read."""


def read_csv(path: str | Path, encoding: str = "utf-8") -> List[Dict[str, Any]]:
    """Read a CSV file into a list of dict records.

    Header row is used for field names. Every value is read as a
    string; type coercion happens later during validation/cleaning.
    """
    path = Path(path)
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            row = dict(row)
            row[SOURCE_ROW_KEY] = i
            records.append(row)
    return records


def read_json(path: str | Path, encoding: str = "utf-8") -> List[Dict[str, Any]]:
    """Read a JSON file into a list of dict records.

    Accepts either:
      - a top-level JSON array of objects, or
      - a top-level JSON object with a "records" key holding the array.
    """
    path = Path(path)
    with path.open("r", encoding=encoding) as f:
        data = json.load(f)

    if isinstance(data, dict) and "records" in data:
        data = data["records"]

    if not isinstance(data, list):
        raise ValueError(
            f"{path}: expected a JSON array of records (or an object with "
            f"a 'records' array), got {type(data).__name__}"
        )

    records: List[Dict[str, Any]] = []
    for i, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{path}: record #{i} is not a JSON object")
        row = dict(row)
        row[SOURCE_ROW_KEY] = i
        records.append(row)
    return records


def read_any(path: str | Path) -> List[Dict[str, Any]]:
    """Dispatch to read_csv or read_json based on file extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    if suffix == ".json":
        return read_json(path)
    raise UnsupportedFileTypeError(
        f"Unsupported file extension '{suffix}' for {path}. Expected .csv or .json"
    )
