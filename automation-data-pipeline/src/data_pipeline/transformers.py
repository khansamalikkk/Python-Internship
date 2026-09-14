"""
transformers.py
----------------
Field-level transformations applied to cleaned, validated records:
type coercion (str -> int/float), date normalization to ISO-8601,
derived fields (age_group), and a simple fixed-rate currency
conversion to illustrate cross-field derivation.

Assumes the record has already passed ``validators.validate_record``
so the raw values are known to be parseable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

KNOWN_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d")

# Illustrative fixed conversion rates to USD. In a real system this
# would come from a rates service/config, not be hard-coded.
FX_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "PKR": 0.0036,
    "TRY": 0.029,
}


def _parse_date(value: str) -> datetime:
    for fmt in KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value!r}")


def _age_group(age: int) -> str:
    if age < 13:
        return "child"
    if age < 20:
        return "teen"
    if age < 60:
        return "adult"
    return "senior"


def transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dict with coerced types and derived fields.

    Adds:
      - id, age as int
      - amount as float, rounded to 2 decimals
      - signup_date normalized to 'YYYY-MM-DD'
      - age_group derived from age
      - amount_usd derived from amount + currency (best-effort; falls
        back to the raw amount if the currency is unrecognized)
    """
    out = dict(record)

    out["id"] = int(float(str(out["id"]).replace(",", "")))
    out["age"] = int(float(str(out["age"])))
    out["amount"] = round(float(str(out["amount"]).replace(",", "")), 2)

    parsed_date = _parse_date(str(out["signup_date"]))
    out["signup_date"] = parsed_date.strftime("%Y-%m-%d")

    out["age_group"] = _age_group(out["age"])

    currency = str(out.get("currency", "USD") or "USD").upper()
    rate = FX_TO_USD.get(currency)
    out["amount_usd"] = round(out["amount"] * rate, 2) if rate is not None else out["amount"]
    out["currency"] = currency

    return out
