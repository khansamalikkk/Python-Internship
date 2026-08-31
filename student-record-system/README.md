# Student Record System

A command-line Student Record Management System built in Python, following
industry-standard practices: clean separation of concerns (models /
storage / business logic / CLI), input validation, custom exceptions,
logging, JSON persistence, and unit tests.

## Features

- **Add** a student record with validated fields (ID, name, age, grade, email, GPA)
- **View** all student records
- **Search** students by ID, name, or grade (case-insensitive)
- **Update** an existing student's details
- **Delete** a student record (with confirmation prompt)
- **Statistics**: total student count and average GPA
- **Persistent storage** to a local `students.json` file (atomic writes to prevent data corruption)
- **Validation** on every field, with clear error messages
- **Logging** of key operations (add/update/delete) and errors

## Project Structure

```
student-record-system/
├── src/
│   └── student_record_system/
│       ├── __init__.py       # Package exports
│       ├── models.py         # Student dataclass + validation
│       ├── storage.py        # JSON persistence layer
│       ├── manager.py        # CRUD business logic
│       └── cli.py            # Command-line interface (entry point)
├── tests/
│   └── test_student_record_system.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Design Notes

- **Separation of concerns**: `models.py` only knows about a single
  student's shape and validity. `storage.py` only knows how to persist a
  dict of students to disk. `manager.py` orchestrates CRUD operations and
  is the only layer that talks to both. `cli.py` is a thin presentation
  layer on top of `manager.py`. This makes each piece independently
  testable and lets you swap the storage backend (e.g. to SQLite) without
  touching business logic.
- **Custom exceptions** (`StudentAlreadyExistsError`, `StudentNotFoundError`,
  `StorageError`) make error handling explicit and easy to catch
  selectively, rather than relying on generic exceptions.
- **Atomic writes**: the storage layer writes to a temporary file first,
  then renames it, to avoid leaving `students.json` in a corrupted state
  if the program is interrupted mid-write.

## Requirements

- Python 3.9+
- No external runtime dependencies (standard library only)
- `pytest` for running the test suite

## Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd student-record-system

# (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies (only needed for running tests)
pip install -r requirements.txt
```

## Usage

Run the CLI directly:

```bash
python -m student_record_system.cli
```

Or, if installed as a package (`pip install -e .`):

```bash
student-records
```

You'll see a menu:

```
==================================
   STUDENT RECORD SYSTEM
==================================
1. Add student
2. View all students
3. Search students
4. Update student
5. Delete student
6. Show statistics
7. Exit
==================================
```

Data is saved automatically to `students.json` in the working directory
after every add/update/delete operation.

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

The test suite covers model validation, all CRUD operations, search,
statistics, and persistence across manager instances (19 tests).

## Example Session

```
Choose an option: 1

-- Add Student --
Student ID: S001
Name: Ali Khan
Age: 21
Grade/Class: Senior
Email (optional): ali.khan@example.com
GPA (0.0 - 4.0): 3.7
Added: ID: S001 | Name: Ali Khan | Age: 21 | Grade: Senior | Email: ali.khan@example.com | GPA: 3.70
```

## Possible Future Enhancements

- Swap JSON storage for SQLite/PostgreSQL via a repository interface
- Add CSV import/export
- Add a REST API layer (e.g. FastAPI) on top of `StudentManager`
- Add pagination for large record sets

## License

MIT — see repository root for details.
