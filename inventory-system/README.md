# Object-Oriented Inventory System

A Python CLI inventory management application built with an object-oriented
architecture: `Product` and `Category` domain models, an `Inventory` service
class for CRUD operations, JSON persistence, and a command-line interface.

## Features
- **Categories**: add, list, remove (with in-use protection — a category
  cannot be removed while products still reference it)
- **Products**: add, update, remove, search
- **Search**: by keyword (name/SKU/description), by category, or low-stock
  only
- **Validation**: non-empty names, non-negative price/quantity, valid
  category references, duplicate SKU/category prevention — all via custom
  exceptions (`ValidationError`, `ProductNotFoundError`,
  `CategoryNotFoundError`, `DuplicateProductError`, `DuplicateCategoryError`)
- **Persistence**: JSON file storage; missing files are treated as an empty
  inventory, corrupt files are backed up (`*.corrupt.<timestamp>.bak`)
  instead of crashing the program
- **Summary reporting**: total products, total items in stock, total
  inventory value, low-stock alerts, and a per-category breakdown
- **Fully unit tested** with `pytest` (29 tests covering models, CRUD,
  search, persistence, and error paths)

## Project Structure
```
inventory-system/
├── src/inventory_system/
│   ├── __init__.py
│   ├── models.py       # Product & Category dataclasses + validation
│   ├── inventory.py    # Inventory service class (CRUD, search, reporting)
│   ├── storage.py      # JSON persistence layer
│   ├── exceptions.py   # Custom exception hierarchy
│   └── cli.py          # Command-line interface
├── tests/
│   ├── test_models.py
│   └── test_inventory.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements
- Python 3.8+
- `pytest` (for running tests only — the application itself has no
  third-party dependencies)

## Installation
```bash
pip install -e .
```

## Usage
```bash
# Categories
python -m inventory_system.cli add-category --name Electronics --description "Gadgets and devices"
python -m inventory_system.cli list-categories
python -m inventory_system.cli remove-category --id 1

# Products
python -m inventory_system.cli add-product --sku LP-001 --name "Laptop" --category-id 1 --price 999.99 --quantity 8 --reorder-level 3
python -m inventory_system.cli update-product --sku LP-001 --quantity 25
python -m inventory_system.cli remove-product --sku LP-001
python -m inventory_system.cli list-products

# Search
python -m inventory_system.cli search --keyword laptop
python -m inventory_system.cli search --category-id 1
python -m inventory_system.cli search --low-stock

# Summary report
python -m inventory_system.cli report
```

By default, data is stored in `inventory_data.json` in the current
directory. Use `--file path/to/data.json` to point at a different file.

## Running Tests
```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Design Notes
- **Encapsulation**: `Inventory` is the only class that touches storage;
  callers never read/write the JSON file directly.
- **Fail-fast validation**: all validation happens in the model
  constructors (`Product.__post_init__`, `Category.__post_init__`), so an
  invalid object can never exist in memory.
- **Referential integrity**: products always reference a valid category id
  (checked on add/update), and categories can't be deleted while in use.
- **Resilience**: corrupt JSON is quarantined (backed up) rather than
  causing data loss or a crash, matching real-world expectations for a
  small business tool.

## Key Lessons / Future Improvements
- Add support for multiple storage backends (e.g. SQLite) behind the same
  `Inventory` interface for larger datasets.
- Add CSV import/export for bulk product updates.
- Add a `--json` output mode for `report`/`list-products` for scripting.
- Add stock movement history (audit log of quantity changes) rather than
  only tracking the current quantity.
