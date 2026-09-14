import csv
import json

import pytest

from data_pipeline.pipeline import Pipeline


def test_pipeline_rejects_empty_input_list():
    with pytest.raises(ValueError):
        Pipeline(input_paths=[])


def test_pipeline_end_to_end_on_sample_data(sample_data_dir):
    pipeline = Pipeline(input_paths=[sample_data_dir / "customers.csv", sample_data_dir / "customers.json"])
    result = pipeline.run()

    # 12 CSV rows + 4 JSON rows = 16 read
    assert result.total_read == 16

    # Every clean record should have the full derived schema and no
    # leftover internal bookkeeping fields.
    for rec in result.clean_records:
        assert "_source_row" not in rec
        assert "_source_file" not in rec
        assert set(rec.keys()) >= {
            "id", "name", "email", "age", "signup_date", "amount",
            "amount_usd", "age_group", "currency",
        }

    # Known-bad rows must NOT survive into the clean set.
    bad_emails = {"not-an-email", "broken@@example.com"}
    assert not any(r["email"] in bad_emails for r in result.clean_records)

    clean_ids = {r["id"] for r in result.clean_records}
    assert 1004 not in clean_ids  # bad email
    assert 1005 not in clean_ids  # missing age
    assert 1006 not in clean_ids  # future date
    assert 1007 not in clean_ids  # negative amount
    assert 1010 not in clean_ids  # missing name
    assert 1012 not in clean_ids  # age out of range

    # Exactly one of the two id=1002 rows should survive (duplicate handling).
    assert sum(1 for r in result.clean_records if r["id"] == 1002) == 1

    assert result.error_count > 0
    assert result.duplicate_count == 1

    error_codes = {e["code"] for e in result.errors}
    assert "invalid_email" in error_codes
    assert "missing_field" in error_codes
    assert "future_date" in error_codes
    assert "negative_amount" in error_codes
    assert "age_out_of_range" in error_codes
    assert "duplicate_id" in error_codes
    assert "invalid_id" in error_codes  # the "not-an-id" JSON row

    summary = result.summary
    assert summary["totals"]["records_read"] == 16
    assert summary["totals"]["records_valid"] == len(result.clean_records)
    assert summary["totals"]["records_invalid"] == result.error_count
    # Regression check: the summary's duplicate count must match the
    # duplicate count actually recorded in the error log, not default to 0.
    assert summary["totals"]["records_duplicate"] == result.duplicate_count
    assert summary["totals"]["records_duplicate"] == 1


def test_pipeline_export_writes_expected_files(tmp_path, sample_data_dir):
    pipeline = Pipeline(input_paths=[sample_data_dir / "customers.csv"])
    pipeline.run()
    paths = pipeline.export(output_dir=tmp_path / "out")

    for path in paths.values():
        assert path.exists()

    with paths["clean_data"].open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(pipeline.result.clean_records)
    assert "amount_usd" in rows[0]

    errors = json.loads(paths["error_log_json"].read_text())
    assert isinstance(errors, list)
    assert len(errors) == pipeline.result.error_count

    summary = json.loads(paths["summary"].read_text())
    assert "totals" in summary
    assert "by_country" in summary


def test_pipeline_handles_all_valid_records(tmp_path):
    csv_path = tmp_path / "all_good.csv"
    csv_path.write_text(
        "id,name,email,age,country,signup_date,amount,currency\n"
        "1,Alice,alice@example.com,25,us,2023-01-01,10.00,USD\n"
        "2,Bob,bob@example.com,40,gb,2023-02-02,20.00,GBP\n",
        encoding="utf-8",
    )

    pipeline = Pipeline(input_paths=[csv_path])
    result = pipeline.run()

    assert result.error_count == 0
    assert len(result.clean_records) == 2
    assert result.summary["totals"]["success_rate_pct"] == 100.0


def test_pipeline_handles_all_invalid_records(tmp_path):
    csv_path = tmp_path / "all_bad.csv"
    csv_path.write_text(
        "id,name,email,age,country,signup_date,amount,currency\n"
        ",NoId,noid@example.com,25,us,2023-01-01,10.00,USD\n"
        "2,NoName,,25,us,2023-01-01,10.00,USD\n",
        encoding="utf-8",
    )

    pipeline = Pipeline(input_paths=[csv_path])
    result = pipeline.run()

    assert len(result.clean_records) == 0
    assert result.error_count == 2
    assert result.summary["totals"]["success_rate_pct"] == 0.0

    # Export should still succeed and produce a (headers-only) clean file.
    paths = pipeline.export(output_dir=csv_path.parent / "out")
    assert paths["clean_data"].exists()
