# Task 2 - Automated Data Pipeline

A practical Python data pipeline that ingests raw CSV and JSON records, validates and cleans the data, applies field transformations, produces summary statistics, and exports clean data together with an error log.

## Project Structure

The project uses a package-oriented `src` layout:

```text
task-2-automated-data-pipeline/
|
|-- src/
|   `-- data_pipeline/
|       |-- __init__.py
|       |-- readers.py
|       |-- validators.py
|       |-- cleaners.py
|       |-- transformers.py
|       |-- stats.py
|       |-- pipeline.py
|       `-- cli.py
|
|-- data/
|   |-- sample.csv
|   `-- sample.json
|
|-- tests/
|   |-- conftest.py
|   |-- test_readers.py
|   |-- test_validators.py
|   |-- test_cleaners.py
|   |-- test_transformers.py
|   |-- test_stats.py
|   `-- <integration test>
|
|-- examples/
|   `-- example_usage.py
|
|-- pyproject.toml
|-- requirements.txt
|-- README.md
|-- .gitignore
`-- LICENSE
```

> Note: The exact filename of the integration test is not documented in the original task notes, so `<integration test>` is shown as a placeholder. Keep the actual test file name already present in the project.

## Main Components

### `readers.py`
Loads records from supported CSV and JSON inputs into a common in-memory representation for downstream processing.

### `validators.py`
Contains field-level and record-level validation rules. Invalid records are separated for error reporting rather than silently discarded.

### `cleaners.py`
Normalizes already-validated values, including whitespace and casing cleanup where appropriate.

### `transformers.py`
Performs data transformations such as type coercion, date normalization, derived-field creation, and currency conversion where configured by the project logic.

### `stats.py`
Calculates summary statistics from the final clean dataset.

### `pipeline.py`
Provides the main `Pipeline` orchestration layer that connects ingestion, validation, cleaning, transformation, statistics, and export steps.

### `cli.py`
Provides a command-line entry point for running the pipeline from a terminal.

## Data Flow

```text
Raw CSV / JSON
      |
      v
   Readers
      |
      v
  Validation ---------> Error Log
      |
      v
    Cleaning
      |
      v
 Transformation
      |
      +-------> Clean Dataset
      |
      +-------> Summary Statistics
```

## Installation

Recommended setup from the project root:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

For editable installation when supported by the project packaging configuration:

```bash
pip install -e .
```

## Running the Pipeline

The project includes a CLI entry point. Display the available options with:

```bash
python -m data_pipeline.cli --help
```

Use the help output to select the supported input, output, and configuration arguments for the version of the project in this repository.

The `examples/example_usage.py` file also demonstrates programmatic use of the pipeline.

## Testing

Run the complete test suite with:

```bash
pytest
```

The original development run reported **64 tests passing** after a duplicate-count regression fix. That figure is included here as project-history information and should be rechecked locally after files are assembled.

To measure coverage, a typical command is:

```bash
coverage run -m pytest
coverage report
```

The original development run reported **88% overall coverage**, with the core logic modules reported at approximately **97-100%** coverage. Re-run coverage locally to confirm the current checkout.

## Quality and Design Goals

This project is designed around practical data-engineering concerns:

- Clear separation of ingestion, validation, cleaning, transformation, statistics, and orchestration.
- Explicit handling of invalid records through an error log.
- Support for more than one raw-data format.
- Unit tests for individual pipeline components.
- End-to-end integration testing.
- A reusable Python API in addition to a CLI entry point.
- Packaging metadata suitable for version-controlled development.
- Sample inputs containing both valid and intentionally invalid records for testing.

## Expected Outputs

The pipeline is intended to produce:

1. A cleaned/normalized dataset containing accepted records.
2. An error log containing records or validation issues that could not be accepted.
3. Summary statistics describing the resulting clean dataset.

The exact output filenames and CLI options depend on the implementation in `pipeline.py` and `cli.py`.

## Task Alignment

This repository addresses the requirements of **Task 2 - Automated Data Pipeline** by implementing a testable Python workflow for reading raw CSV/JSON data, validating and cleaning records, transforming selected fields, generating summary statistics, and exporting the clean dataset plus an error log.

## License

This project is released under the MIT License. See `LICENSE` for details.
