from data_pipeline.cleaners import clean_record


def test_strips_whitespace_from_all_string_fields():
    rec = {"name": "  Jane  ", "email": " jane@example.com ", "note": "  hi  "}
    cleaned = clean_record(rec)
    assert cleaned["name"] == "Jane"  # also collapsed
    assert cleaned["email"] == "jane@example.com"
    assert cleaned["note"] == "hi"


def test_collapses_internal_whitespace_in_name():
    rec = {"name": "John    Smith"}
    cleaned = clean_record(rec)
    assert cleaned["name"] == "John Smith"


def test_lowercases_email():
    rec = {"email": "Jane.DOE@Example.COM"}
    cleaned = clean_record(rec)
    assert cleaned["email"] == "jane.doe@example.com"


def test_uppercases_country_and_currency():
    rec = {"country": "us", "currency": "usd"}
    cleaned = clean_record(rec)
    assert cleaned["country"] == "US"
    assert cleaned["currency"] == "USD"


def test_does_not_mutate_input():
    rec = {"name": " Jane "}
    clean_record(rec)
    assert rec["name"] == " Jane "  # original untouched


def test_non_string_values_left_alone():
    rec = {"age": 30, "amount": 12.5}
    cleaned = clean_record(rec)
    assert cleaned["age"] == 30
    assert cleaned["amount"] == 12.5
