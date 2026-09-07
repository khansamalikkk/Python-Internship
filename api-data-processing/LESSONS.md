# Key Lessons & Future Improvements

## Lessons Learned
- Public APIs can be unreliable or blocked in restricted environments
  (firewalls, sandboxes, rate limits), so a local fallback dataset is
  valuable for reproducibility and testing.
- Real-world API data often has missing or inconsistent fields (e.g. blank
  names/emails), so cleaning logic must validate and skip bad records
  rather than crash.
- Separating fetch, clean, calculate, and export into distinct functions
  makes the script easier to test and extend.

## Improvements for Next Iteration
- Add retry logic with exponential backoff for transient network failures.
- Support command-line arguments for API URL, output filename, and field
  selection instead of hardcoded constants.
- Add unit tests (e.g. with `pytest`) covering cleaning and statistics
  logic.
- Validate email format more strictly (e.g. with a regex) rather than
  just checking non-empty.
- Support pagination for APIs that return large datasets across multiple
  pages.
- Add logging (via the `logging` module) instead of `print` for better
  traceability in production use.
