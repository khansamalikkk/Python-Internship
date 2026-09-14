"""
data_pipeline
=============

A small, dependency-light ETL pipeline for cleaning and validating
tabular customer records supplied as CSV or JSON.

Public API:
    Pipeline        - orchestrates read -> validate -> clean -> transform -> export
    read_csv        - read a CSV file into a list of dict records
    read_json       - read a JSON file (list of objects) into a list of dict records
    validate_record - validate a single raw record
    clean_record    - normalize whitespace/case on a single record
    transform_record- derive/convert fields on a single record
    compute_summary - build summary statistics over a list of clean records
"""

from .pipeline import Pipeline
from .readers import read_csv, read_json, read_any
from .validators import validate_record, ValidationIssue
from .cleaners import clean_record
from .transformers import transform_record
from .stats import compute_summary

__all__ = [
    "Pipeline",
    "read_csv",
    "read_json",
    "read_any",
    "validate_record",
    "ValidationIssue",
    "clean_record",
    "transform_record",
    "compute_summary",
]

__version__ = "1.0.0"
