"""
cleaners.py
-----------
Light normalization applied to records that already passed
validation. Cleaning never changes the *meaning* of a value, only
its representation (whitespace, casing, thousands separators).

Kept separate from transformers.py, which derives new fields or
performs unit/currency conversions - a distinct, "bigger" kind of
change worth reviewing independently.
"""

from __future__ import annotations

from typing import Any, Dict


def clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dict with normalized string formatting.

    - Strips leading/trailing whitespace from every string field.
    - Collapses internal repeated whitespace in the name field.
    - Lower-cases email addresses.
    - Upper-cases country/currency codes.
    """
    cleaned = dict(record)

    for key, value in list(cleaned.items()):
        if isinstance(value, str):
            cleaned[key] = value.strip()

    if "name" in cleaned and isinstance(cleaned["name"], str):
        cleaned["name"] = " ".join(cleaned["name"].split())

    if "email" in cleaned and isinstance(cleaned["email"], str):
        cleaned["email"] = cleaned["email"].lower()

    if "country" in cleaned and isinstance(cleaned["country"], str):
        cleaned["country"] = cleaned["country"].upper()

    if "currency" in cleaned and isinstance(cleaned["currency"], str):
        cleaned["currency"] = cleaned["currency"].upper()

    return cleaned
