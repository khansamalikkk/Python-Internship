import json

import pytest

from data_pipeline.readers import UnsupportedFileTypeError, read_any, read_csv, read_json


def test_read_csv_basic(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")

    records = read_csv(p)

    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert records[0]["name"] == "Alice"
    assert records[0]["_source_row"] == 1
    assert records[1]["_source_row"] == 2


def test_read_json_array(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]), encoding="utf-8")

    records = read_json(p)

    assert len(records) == 2
    assert records[0]["name"] == "Alice"
    assert records[0]["_source_row"] == 1


def test_read_json_records_wrapper(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps({"records": [{"id": 1}]}), encoding="utf-8")

    records = read_json(p)

    assert len(records) == 1
    assert records[0]["id"] == 1


def test_read_json_rejects_non_list_non_wrapper(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

    with pytest.raises(ValueError):
        read_json(p)


def test_read_json_rejects_non_object_elements(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(ValueError):
        read_json(p)


def test_read_any_dispatches_by_extension(tmp_path):
    csv_path = tmp_path / "a.csv"
    csv_path.write_text("id\n1\n", encoding="utf-8")
    json_path = tmp_path / "b.json"
    json_path.write_text(json.dumps([{"id": 1}]), encoding="utf-8")

    assert len(read_any(csv_path)) == 1
    assert len(read_any(json_path)) == 1


def test_read_any_rejects_unknown_extension(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("hello", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        read_any(p)


def test_read_csv_sample_data_file(sample_data_dir):
    records = read_csv(sample_data_dir / "customers.csv")
    assert len(records) == 12
    assert records[0]["name"] == "Jane Doe"


def test_read_json_sample_data_file(sample_data_dir):
    records = read_json(sample_data_dir / "customers.json")
    assert len(records) == 4
