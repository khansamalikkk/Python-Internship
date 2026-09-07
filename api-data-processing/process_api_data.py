"""
API Data Processing Script
---------------------------
Consumes a public JSON API (JSONPlaceholder - /users endpoint by default),
extracts selected fields, cleans the data, calculates summary statistics,
and exports the results to a CSV file.

Usage:
    python process_api_data.py
"""

import csv
import json
import statistics
import sys
import urllib.request
import urllib.error

API_URL = "https://jsonplaceholder.typicode.com/users"
LOCAL_FALLBACK_FILE = "sample_data.json"
OUTPUT_CSV = "output_data.csv"
SUMMARY_TXT = "summary_stats.txt"


def fetch_data(url, fallback_file=LOCAL_FALLBACK_FILE):
    """Fetch JSON data from the API. Falls back to a bundled local sample
    file if the API is unreachable (e.g. no internet access, blocked, etc.)."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status != 200:
                raise ValueError(f"Unexpected status code: {response.status}")
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except (urllib.error.URLError, ValueError) as e:
        print(f"[WARNING] Could not reach API ({e}). Using local fallback data.")
        try:
            with open(fallback_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as fe:
            print(f"[ERROR] Failed to load fallback data: {fe}")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON response: {e}")
        sys.exit(1)


def extract_and_clean(raw_data):
    """Extract selected fields and clean the data."""
    cleaned = []
    for entry in raw_data:
        try:
            name = str(entry.get("name", "")).strip()
            username = str(entry.get("username", "")).strip()
            email = str(entry.get("email", "")).strip().lower()
            city = str(entry.get("address", {}).get("city", "")).strip()
            company = str(entry.get("company", {}).get("name", "")).strip()

            # Skip records missing critical fields
            if not name or not email:
                continue

            cleaned.append({
                "name": name,
                "username": username,
                "email": email,
                "city": city,
                "company": company,
                "name_length": len(name),
            })
        except (AttributeError, TypeError) as e:
            print(f"[WARNING] Skipping malformed record: {e}")
            continue
    return cleaned


def calculate_statistics(cleaned_data):
    """Calculate simple summary statistics from the cleaned data."""
    if not cleaned_data:
        return {"count": 0}

    name_lengths = [d["name_length"] for d in cleaned_data]
    cities = [d["city"] for d in cleaned_data if d["city"]]
    unique_companies = {d["company"] for d in cleaned_data if d["company"]}

    stats = {
        "count": len(cleaned_data),
        "avg_name_length": round(statistics.mean(name_lengths), 2),
        "max_name_length": max(name_lengths),
        "min_name_length": min(name_lengths),
        "unique_cities": len(set(cities)),
        "unique_companies": len(unique_companies),
    }
    return stats


def export_to_csv(cleaned_data, filepath):
    """Export cleaned data to a CSV file."""
    if not cleaned_data:
        print("[WARNING] No data to export.")
        return
    fieldnames = list(cleaned_data[0].keys())
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_data)
        print(f"[INFO] Data exported to {filepath}")
    except OSError as e:
        print(f"[ERROR] Failed to write CSV file: {e}")
        sys.exit(1)


def export_summary(stats, filepath):
    """Write summary statistics to a text file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Summary Statistics\n")
            f.write("===================\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
        print(f"[INFO] Summary written to {filepath}")
    except OSError as e:
        print(f"[ERROR] Failed to write summary file: {e}")


def main():
    print(f"[INFO] Fetching data from {API_URL} ...")
    raw_data = fetch_data(API_URL)

    print("[INFO] Extracting and cleaning data ...")
    cleaned_data = extract_and_clean(raw_data)

    print("[INFO] Calculating summary statistics ...")
    stats = calculate_statistics(cleaned_data)
    print(json.dumps(stats, indent=2))

    export_to_csv(cleaned_data, OUTPUT_CSV)
    export_summary(stats, SUMMARY_TXT)


if __name__ == "__main__":
    main()
