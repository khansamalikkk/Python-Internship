from data_pipeline.stats import compute_summary


def make_record(**overrides):
    base = {
        "id": 1,
        "name": "Test",
        "age": 30,
        "age_group": "adult",
        "amount": 100.0,
        "amount_usd": 100.0,
        "country": "US",
        "currency": "USD",
        "signup_date": "2023-01-01",
    }
    base.update(overrides)
    return base


def test_totals_reflect_counts():
    records = [make_record(), make_record()]
    summary = compute_summary(records, total_read=5, error_count=2, duplicate_count=1)

    assert summary["totals"]["records_read"] == 5
    assert summary["totals"]["records_valid"] == 2
    assert summary["totals"]["records_invalid"] == 2
    assert summary["totals"]["records_duplicate"] == 1
    assert summary["totals"]["success_rate_pct"] == 40.0


def test_numeric_summary_for_amount():
    records = [make_record(amount=100.0), make_record(amount=200.0)]
    summary = compute_summary(records, total_read=2, error_count=0)

    assert summary["amount"]["count"] == 2
    assert summary["amount"]["min"] == 100.0
    assert summary["amount"]["max"] == 200.0
    assert summary["amount"]["mean"] == 150.0


def test_empty_dataset_does_not_crash():
    summary = compute_summary([], total_read=0, error_count=0)
    assert summary["totals"]["records_valid"] == 0
    assert summary["totals"]["success_rate_pct"] == 0.0
    assert summary["amount"]["count"] == 0
    assert summary["amount"]["mean"] is None


def test_grouping_by_country_age_group_currency():
    records = [
        make_record(country="US", age_group="adult", currency="USD"),
        make_record(country="US", age_group="senior", currency="USD"),
        make_record(country="PK", age_group="adult", currency="PKR"),
    ]
    summary = compute_summary(records, total_read=3, error_count=0)

    assert summary["by_country"] == {"US": 2, "PK": 1}
    assert summary["by_age_group"] == {"adult": 2, "senior": 1}
    assert summary["by_currency"] == {"USD": 2, "PKR": 1}


def test_date_range():
    records = [
        make_record(signup_date="2023-05-01"),
        make_record(signup_date="2023-01-01"),
        make_record(signup_date="2023-09-01"),
    ]
    summary = compute_summary(records, total_read=3, error_count=0)

    assert summary["date_range"]["earliest"] == "2023-01-01"
    assert summary["date_range"]["latest"] == "2023-09-01"
