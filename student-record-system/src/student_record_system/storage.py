"""Persistence layer for the Student Record System.

Uses a JSON file as the backing store. The storage layer is intentionally
decoupled from the business logic (see manager.py) so the persistence
mechanism could be swapped (e.g. for SQLite) without touching the rest of
the application.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

from .models import Student

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when records cannot be loaded from or saved to disk."""


class JSONStorage:
    """Reads and writes student records to a JSON file on disk."""

    def __init__(self, file_path: str | Path = "students.json") -> None:
        self.file_path = Path(file_path)

    def load(self) -> Dict[str, Student]:
        """Load all records from disk. Returns an empty dict if the file is absent."""
        if not self.file_path.exists():
            logger.info("No existing data file at %s; starting fresh.", self.file_path)
            return {}
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            return {sid: Student.from_dict(data) for sid, data in raw.items()}
        except (json.JSONDecodeError, OSError) as exc:
            raise StorageError(f"Failed to load data from {self.file_path}: {exc}") from exc

    def save(self, records: Dict[str, Student]) -> None:
        """Persist all records to disk, writing atomically to avoid corruption."""
        try:
            tmp_path = self.file_path.with_suffix(".tmp")
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(
                    {sid: student.to_dict() for sid, student in records.items()},
                    f,
                    indent=2,
                )
            tmp_path.replace(self.file_path)
        except OSError as exc:
            raise StorageError(f"Failed to save data to {self.file_path}: {exc}") from exc
