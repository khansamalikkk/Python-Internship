import pytest

from data_pipeline.validators import find_duplicate_ids, validate_record


def test_valid_record_has_no_issues(valid_record):
    issues = validate_record(valid_record)
    assert issues == []


@pytest.mark.parametrize("field", ["id", "name", "email", "age", "signup_date", "amount"])
def test_missing_required_field_flagged(valid_record, field):
    del valid_record[field]
    issues = validate_record(valid_record)
    codes = [i.code for i in issues]
    assert "missing_field" in codes


@pytest.mark.parametrize("field", ["id", "name", "email", "age", "signup_date", "amount"])
def test_blank_required_field_flagged(valid_record, field):
    valid_record[field] = "   "
    issues = validate_record(valid_record)
    codes = [i.code for i in issues]
    assert "missing_field" in codes


def test_invalid_email_flagged(valid_record):
    valid_record["email"] = "not-an-email"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_email" for i in issues)


def test_invalid_id_non_integer_flagged(valid_record):
    valid_record["id"] = "abc"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_id" for i in issues)


def test_negative_id_flagged(valid_record):
    valid_record["id"] = "-5"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_id" for i in issues)


def test_non_integer_age_flagged(valid_record):
    valid_record["age"] = "twenty"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_age" for i in issues)


def test_age_out_of_range_flagged(valid_record):
    valid_record["age"] = "150"
    issues = validate_record(valid_record)
    assert any(i.code == "age_out_of_range" for i in issues)


def test_unparseable_date_flagged(valid_record):
    valid_record["signup_date"] = "not-a-date"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_date" for i in issues)


def test_future_date_flagged(valid_record):
    valid_record["signup_date"] = "2099-01-01"
    issues = validate_record(valid_record)
    assert any(i.code == "future_date" for i in issues)


@pytest.mark.parametrize("fmt_value", ["01/22/2023", "22-01-2023", "2023/01/22", "2023-01-22"])
def test_accepted_date_formats(valid_record, fmt_value):
    valid_record["signup_date"] = fmt_value
    issues = validate_record(valid_record)
    assert not any(i.code in ("invalid_date", "future_date") for i in issues)


def test_non_numeric_amount_flagged(valid_record):
    valid_record["amount"] = "free"
    issues = validate_record(valid_record)
    assert any(i.code == "invalid_amount" for i in issues)


def test_negative_amount_flagged(valid_record):
    valid_record["amount"] = "-10"
    issues = validate_record(valid_record)
    assert any(i.code == "negative_amount" for i in issues)


def test_validate_record_rejects_non_dict():
    with pytest.raises(TypeError):
        validate_record(["not", "a", "dict"])  # type: ignore[arg-type]


def test_find_duplicate_ids():
    records = [
        {"id": "1", "_source_row": 1},
        {"id": "2", "_source_row": 2},
        {"id": "1", "_source_row": 3},
        {"id": "3", "_source_row": 4},
        {"id": "3", "_source_row": 5},
    ]
    dupes = find_duplicate_ids(records)
    assert set(dupes.keys()) == {"1", "3"}
    assert dupes["1"] == [1, 3]
    assert dupes["3"] == [4, 5]


def test_find_duplicate_ids_ignores_blank_ids():
    records = [{"id": ""}, {"id": ""}, {"id": "5"}]
    dupes = find_duplicate_ids(records)
    assert dupes == {}
