"""
cli.py
------
Command-line entrypoint:

    python -m data_pipeline.cli input1.csv input2.json --output-dir output

or, once installed:

    data-pipeline input1.csv input2.json --output-dir output
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .pipeline import Pipeline


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-pipeline",
        description="Read raw CSV/JSON records, validate, clean, transform, and export results.",
    )
    parser.add_argument("inputs", nargs="+", help="One or more input .csv/.json files")
    parser.add_argument(
        "--output-dir", "-o", default="output", help="Directory to write clean_data.csv, error_log.*, summary.json (default: output)"
    )
    parser.add_argument(
        "--id-field", default="id", help="Field name used for duplicate detection (default: id)"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Only log warnings and errors")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    missing = [p for p in args.inputs if not Path(p).exists()]
    if missing:
        logging.error("Input file(s) not found: %s", ", ".join(missing))
        return 1

    pipeline = Pipeline(input_paths=args.inputs, id_field=args.id_field)
    result = pipeline.run()
    paths = pipeline.export(output_dir=args.output_dir)

    totals = result.summary["totals"]
    print("\n--- Pipeline Summary ---")
    print(f"  Records read:    {totals['records_read']}")
    print(f"  Valid records:   {totals['records_valid']}")
    print(f"  Invalid records: {totals['records_invalid']}")
    print(f"  Duplicates:      {totals['records_duplicate']}")
    print(f"  Success rate:    {totals['success_rate_pct']}%")
    print("\n--- Files written ---")
    for label, path in paths.items():
        print(f"  {label}: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
