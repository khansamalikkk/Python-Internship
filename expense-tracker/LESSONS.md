# Key Lessons & Improvements for the Next Iteration

## What went well

- Keeping everything in the standard library (no `pip install` step) made
  the tool trivially easy to run anywhere with Python 3.8+.
- Separating a dedicated `ExpenseStorage` class from the CLI command
  functions made it straightforward to test load/save behavior (including
  corruption handling) independently of the argparse wiring.
- Writing to a temporary file and using `os.replace()` for saves avoids
  leaving a half-written, corrupt JSON file behind if the process is
  interrupted mid-save.
- Validating on both write (`add`) and read (`load`) means the tracker is
  resilient even if the JSON file is hand-edited between runs.

## Known limitations

- **Concurrency**: the tool assumes single-user, single-process access.
  Two instances running `add` at the same time could race and one write
  could be lost, since there's no file locking.
- **Scalability**: the entire file is loaded into memory and rewritten on
  every change. This is fine for a personal tracker with thousands of
  entries but would not scale to a very large or multi-year, high-volume
  dataset.
- **No editing command**: currently you can `add` or `delete` but not
  `edit` an existing record in place (you'd delete and re-add).
- **No recurring expenses / budgets**: no support for recurring monthly
  bills or budget limits/alerts per category.
- **No currency handling**: amounts are treated as plain floats with no
  currency code, which would matter for anyone tracking expenses in more
  than one currency.
- **CSV import**: the tool can *export* to CSV but cannot *import* from
  CSV/bank statements, which would be a natural next feature.

## Improvements planned for the next iteration

1. **`edit` command** — allow updating amount/category/description/date of
   an existing expense by id, instead of delete + re-add.
2. **File locking** — use a simple lock file (or `fcntl`/`msvcrt` locking)
   to make concurrent access safe.
3. **Budgets** — allow setting a monthly budget per category and warn when
   `summary` shows a category over budget.
4. **Recurring expenses** — a `--recurring monthly` flag on `add` that
   auto-generates future entries.
5. **Richer reporting** — optional bar-chart style ASCII summary, or an
   `--export-summary` flag to dump the monthly/category summary to CSV as
   well as the raw records.
6. **Automated test suite** — the current validation was manual, exercised
   command-by-command from the shell; a `pytest` suite with fixtures for
   valid/corrupt/missing files would make regressions much easier to catch
   as features are added.
7. **Multi-currency support** — store a currency code per record and
   convert for summary totals using a fixed or fetched exchange rate.
8. **SQLite backend option** — for users with very large histories, offer
   `--backend sqlite` as an alternative to the JSON file, keeping the CLI
   interface unchanged.
