import sys
from pathlib import Path

# Ensure src/ is importable without installing the package.
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest


@pytest.fixture
def valid_record():
    return {
        "id": "1001",
        "name": " Jane   Doe ",
        "email": "Jane@Example.com",
        "age": "34",
        "country": "us",
        "signup_date": "2023-01-15",
        "amount": "129.99",
        "currency": "usd",
    }


@pytest.fixture
def sample_data_dir():
    return Path(__file__).resolve().parents[1] / "sample_data"
