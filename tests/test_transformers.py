import pytest

from data_pipeline.cleaners import clean_record
from data_pipeline.transformers import transform_record


def test_coerces_id_age_to_int(valid_record):
    out = transform_record(clean_record(valid_record))
    assert out["id"] == 1001
    assert isinstance(out["id"], int)
    assert out["age"] == 34
    assert isinstance(out["age"], int)


def test_amount_rounded_to_two_decimals(valid_record):
    valid_record["amount"] = "129.9967"
    out = transform_record(clean_record(valid_record))
    assert out["amount"] == 130.0


def test_date_normalized_to_iso(valid_record):
    valid_record["signup_date"] = "01/22/2023"
    out = transform_record(clean_record(valid_record))
    assert out["signup_date"] == "2023-01-22"


@pytest.mark.parametrize(
    "age,expected_group",
    [(5, "child"), (16, "teen"), (35, "adult"), (70, "senior")],
)
def test_age_group_boundaries(valid_record, age, expected_group):
    valid_record["age"] = str(age)
    out = transform_record(clean_record(valid_record))
    assert out["age_group"] == expected_group


def test_amount_usd_conversion_known_currency(valid_record):
    valid_record["currency"] = "PKR"
    valid_record["amount"] = "1000"
    out = transform_record(clean_record(valid_record))
    assert out["amount_usd"] == pytest.approx(3.6, abs=0.01)


def test_amount_usd_falls_back_for_unknown_currency(valid_record):
    valid_record["currency"] = "XYZ"
    valid_record["amount"] = "100"
    out = transform_record(clean_record(valid_record))
    assert out["amount_usd"] == 100.0


def test_missing_currency_defaults_to_usd(valid_record):
    del valid_record["currency"]
    out = transform_record(clean_record(valid_record))
    assert out["currency"] == "USD"
    assert out["amount_usd"] == out["amount"]
