"""
Example: run the pipeline programmatically (as opposed to the CLI)
against the bundled sample data, and print a few things out of the
result to show what's available on PipelineResult.

Run from the project root with:
    python examples/run_example.py
"""

import json
import sys
from pathlib import Path

# Make src/ importable when running this script directly from a checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_pipeline import Pipeline  # noqa: E402


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    inputs = [
        project_root / "sample_data" / "customers.csv",
        project_root / "sample_data" / "customers.json",
    ]

    pipeline = Pipeline(input_paths=inputs)
    result = pipeline.run()
    paths = pipeline.export(output_dir=project_root / "output")

    print(f"Read:    {result.total_read}")
    print(f"Valid:   {len(result.clean_records)}")
    print(f"Errors:  {result.error_count} (of which {result.duplicate_count} duplicates)")
    print()
    print("Sample of 3 clean records:")
    print(json.dumps(result.clean_records[:3], indent=2))
    print()
    print("Summary statistics:")
    print(json.dumps(result.summary, indent=2))
    print()
    print("Files written:")
    for label, path in paths.items():
        print(f"  {label}: {path}")


if __name__ == "__main__":
    main()
