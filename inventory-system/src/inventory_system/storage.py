"""JSON persistence layer for the inventory system.

Handles reading/writing the inventory data file safely: missing files are
treated as an empty inventory, and corrupt files are backed up (with a
timestamp suffix) rather than silently discarded or allowed to crash the
program.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict

from .exceptions import StorageError

DEFAULT_DATA_FILE = "inventory_data.json"

_EMPTY_STORE: Dict[str, Any] = {"categories": [], "products": []}


class JSONStorage:
    """Loads and saves inventory state (categories + products) as JSON."""

    def __init__(self, path: str = DEFAULT_DATA_FILE):
        self.path = path

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return dict(_EMPTY_STORE)

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except OSError as exc:
            raise StorageError(f"Could not read data file '{self.path}': {exc}") from exc

        if not content:
            return dict(_EMPTY_STORE)

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            self._quarantine_corrupt_file(exc)
            return dict(_EMPTY_STORE)

        if not isinstance(data, dict) or "categories" not in data or "products" not in data:
            self._quarantine_corrupt_file(reason="unexpected JSON structure")
            return dict(_EMPTY_STORE)

        data.setdefault("categories", [])
        data.setdefault("products", [])
        return data

    def save(self, data: Dict[str, Any]) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        tmp_path = f"{self.path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.path)
        except OSError as exc:
            raise StorageError(f"Failed to save data to '{self.path}': {exc}") from exc

    def _quarantine_corrupt_file(self, exc: Exception | None = None, reason: str = "") -> None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{self.path}.corrupt.{timestamp}.bak"
        try:
            shutil.copy2(self.path, backup_path)
            print(
                f"[Warning] Data file '{self.path}' is corrupt "
                f"({exc or reason}). Backed up to '{backup_path}'. "
                "Starting with an empty inventory."
            )
        except OSError as copy_exc:
            print(
                f"[Warning] Data file '{self.path}' is corrupt and could not "
                f"be backed up ({copy_exc}). Starting with an empty inventory."
            )
