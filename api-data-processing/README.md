# API Data Processing Script

A Python script that fetches user data from a public JSON API
([JSONPlaceholder](https://jsonplaceholder.typicode.com/users)), extracts
selected fields, cleans the data, computes summary statistics, and exports
the results to CSV.

## Features
- Fetches data from `https://jsonplaceholder.typicode.com/users`
- Falls back to a bundled `sample_data.json` file if the API is unreachable
  (network error, timeout, non-200 response, etc.)
- Extracts fields: `name`, `username`, `email`, `city`, `company`
- Cleans data: strips whitespace, lowercases emails, skips records missing
  a name or email
- Computes summary statistics: record count, average/min/max name length,
  unique city count, unique company count
- Exports cleaned data to `output_data.csv`
- Exports summary statistics to `summary_stats.txt`
- Error handling for network failures, malformed JSON, malformed records,
  and file write errors

## Requirements
- Python 3.7+ (standard library only — no external dependencies)

## Usage
```bash
python process_api_data.py
```

## Output Files
- `output_data.csv` — cleaned, extracted records
- `summary_stats.txt` — summary statistics of the dataset

## Project Structure
```
api-data-processing/
├── process_api_data.py   # Main script
├── sample_data.json      # Local fallback dataset (same schema as the API)
├── README.md
└── LESSONS.md            # Key lessons / future improvements
```
