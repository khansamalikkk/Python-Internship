"""
stats.py
--------
Summary statistics computed over the final, transformed dataset.
Pure stdlib (statistics module) - no pandas dependency required just
to answer "how many rows, what's the average amount, etc."
"""

from __future__ import annotations

import statistics
from collections import Counter
from typing import Any, Dict, List


def _numeric_summary(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None, "median": None, "stdev": None}
    return {
        "count": len(values),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "stdev": round(statistics.pstdev(values), 2) if len(values) > 1 else 0.0,
    }


def compute_summary(
    clean_records: List[Dict[str, Any]],
    total_read: int,
    error_count: int,
    duplicate_count: int = 0,
) -> Dict[str, Any]:
    """Build a JSON-serializable summary dict describing a pipeline run.

    Parameters
    ----------
    clean_records : the final, validated + cleaned + transformed records
    total_read    : number of raw records read from the source file(s)
    error_count   : number of records rejected during validation
    duplicate_count : number of records rejected as duplicates
    """
    ages = [r["age"] for r in clean_records if isinstance(r.get("age"), (int, float))]
    amounts = [r["amount"] for r in clean_records if isinstance(r.get("amount"), (int, float))]
    amounts_usd = [r["amount_usd"] for r in clean_records if isinstance(r.get("amount_usd"), (int, float))]

    country_counts = Counter(r.get("country") for r in clean_records if r.get("country"))
    age_group_counts = Counter(r.get("age_group") for r in clean_records if r.get("age_group"))
    currency_counts = Counter(r.get("currency") for r in clean_records if r.get("currency"))

    dates = sorted(r["signup_date"] for r in clean_records if r.get("signup_date"))

    return {
        "totals": {
            "records_read": total_read,
            "records_valid": len(clean_records),
            "records_invalid": error_count,
            "records_duplicate": duplicate_count,
            "success_rate_pct": round(100 * len(clean_records) / total_read, 2) if total_read else 0.0,
        },
        "age": _numeric_summary(ages),
        "amount": _numeric_summary(amounts),
        "amount_usd": _numeric_summary(amounts_usd),
        "by_country": dict(country_counts.most_common()),
        "by_age_group": dict(age_group_counts.most_common()),
        "by_currency": dict(currency_counts.most_common()),
        "date_range": {
            "earliest": dates[0] if dates else None,
            "latest": dates[-1] if dates else None,
        },
    }
