"""
pipeline.py
-----------
Orchestrates the full ETL flow:

    read -> validate -> (drop invalid / drop duplicates) -> clean
    -> transform -> export clean dataset + error log + summary

Usage
-----
    from data_pipeline import Pipeline

    pipeline = Pipeline(input_paths=["sample_data/customers.csv"])
    result = pipeline.run()
    pipeline.export(output_dir="output")

``result`` is a ``PipelineResult`` with ``.clean_records``,
``.errors`` and ``.summary`` already populated; ``export`` just
writes those to disk.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .cleaners import clean_record
from .readers import read_any
from .stats import compute_summary
from .transformers import transform_record
from .validators import ValidationIssue, find_duplicate_ids, validate_record

logger = logging.getLogger("data_pipeline")


@dataclass
class PipelineResult:
    clean_records: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    total_read: int = 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def duplicate_count(self) -> int:
        return sum(1 for e in self.errors if e.get("code") == "duplicate_id")


class Pipeline:
    """Reads one or more input files and produces a cleaned dataset,
    an error log, and summary statistics.
    """

    def __init__(self, input_paths: Sequence[str | Path], id_field: str = "id"):
        if not input_paths:
            raise ValueError("Pipeline requires at least one input path")
        self.input_paths = [Path(p) for p in input_paths]
        self.id_field = id_field
        self.result = PipelineResult()

    # ------------------------------------------------------------------
    # Core run
    # ------------------------------------------------------------------
    def run(self) -> PipelineResult:
        raw_records: List[Dict[str, Any]] = []
        for path in self.input_paths:
            logger.info("Reading %s", path)
            file_records = read_any(path)
            for rec in file_records:
                rec["_source_file"] = str(path)
            raw_records.extend(file_records)

        self.result.total_read = len(raw_records)
        logger.info("Read %d raw records from %d file(s)", len(raw_records), len(self.input_paths))

        valid_records: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        # Pass 1: per-record validation
        for rec in raw_records:
            row = rec.get("_source_row")
            issues = validate_record(rec, row=row)
            if issues:
                errors.extend(self._issue_to_error_row(rec, i) for i in issues)
            else:
                valid_records.append(rec)

        # Pass 2: duplicate detection across records that individually passed
        dupes = find_duplicate_ids(valid_records, id_field=self.id_field)
        if dupes:
            deduped: List[Dict[str, Any]] = []
            seen_ids: set = set()
            for rec in valid_records:
                key = str(rec.get(self.id_field, "")).strip()
                if key in dupes:
                    if key in seen_ids:
                        errors.append(
                            {
                                "row": rec.get("_source_row"),
                                "source_file": rec.get("_source_file"),
                                "field": self.id_field,
                                "code": "duplicate_id",
                                "message": f"Duplicate {self.id_field} '{key}' - keeping first occurrence, dropping this one",
                                "raw_record": self._strip_meta(rec),
                            }
                        )
                        continue
                    seen_ids.add(key)
                deduped.append(rec)
            valid_records = deduped

        # Pass 3: clean + transform survivors
        clean_records: List[Dict[str, Any]] = []
        for rec in valid_records:
            try:
                cleaned = clean_record(rec)
                transformed = transform_record(cleaned)
                clean_records.append(self._strip_meta(transformed))
            except Exception as exc:  # defensive: a record that passed validation
                # should not fail transformation, but we never want one bad
                # record to crash the whole pipeline run.
                errors.append(
                    {
                        "row": rec.get("_source_row"),
                        "source_file": rec.get("_source_file"),
                        "field": "",
                        "code": "transform_error",
                        "message": f"Unexpected error during clean/transform: {exc}",
                        "raw_record": self._strip_meta(rec),
                    }
                )

        duplicate_count = sum(1 for e in errors if e.get("code") == "duplicate_id")
        summary = compute_summary(
            clean_records,
            total_read=self.result.total_read,
            error_count=len(errors),
            duplicate_count=duplicate_count,
        )

        self.result.clean_records = clean_records
        self.result.errors = errors
        self.result.summary = summary
        logger.info(
            "Pipeline complete: %d valid, %d errors, success rate %.2f%%",
            len(clean_records),
            len(errors),
            summary["totals"]["success_rate_pct"],
        )
        return self.result

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def export(self, output_dir: str | Path = "output") -> Dict[str, Path]:
        """Write clean_data.csv, error_log.csv/json, and summary.json.

        Returns a dict of the paths written, for convenience.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        clean_path = output_dir / "clean_data.csv"
        error_json_path = output_dir / "error_log.json"
        error_csv_path = output_dir / "error_log.csv"
        summary_path = output_dir / "summary.json"

        self._write_clean_csv(clean_path)
        self._write_error_log(error_json_path, error_csv_path)
        summary_path.write_text(json.dumps(self.result.summary, indent=2), encoding="utf-8")

        logger.info("Exported clean dataset -> %s", clean_path)
        logger.info("Exported error log -> %s / %s", error_csv_path, error_json_path)
        logger.info("Exported summary -> %s", summary_path)

        return {
            "clean_data": clean_path,
            "error_log_json": error_json_path,
            "error_log_csv": error_csv_path,
            "summary": summary_path,
        }

    def _write_clean_csv(self, path: Path) -> None:
        records = self.result.clean_records
        if not records:
            path.write_text("", encoding="utf-8")
            return
        fieldnames = list(records[0].keys())
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    def _write_error_log(self, json_path: Path, csv_path: Path) -> None:
        errors = self.result.errors
        json_path.write_text(json.dumps(errors, indent=2, default=str), encoding="utf-8")

        if not errors:
            csv_path.write_text("row,source_file,field,code,message,raw_record\n", encoding="utf-8")
            return

        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["row", "source_file", "field", "code", "message", "raw_record"])
            writer.writeheader()
            for e in errors:
                row = dict(e)
                row["raw_record"] = json.dumps(row.get("raw_record", {}), default=str)
                writer.writerow(row)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_meta(record: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in record.items() if not k.startswith("_")}

    def _issue_to_error_row(self, rec: Dict[str, Any], issue: ValidationIssue) -> Dict[str, Any]:
        return {
            "row": issue.row,
            "source_file": rec.get("_source_file"),
            "field": issue.field,
            "code": issue.code,
            "message": issue.message,
            "raw_record": self._strip_meta(rec),
        }
