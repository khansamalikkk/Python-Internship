"""Student Record System package."""
from .models import Student
from .manager import StudentManager, StudentAlreadyExistsError, StudentNotFoundError
from .storage import JSONStorage, StorageError

__version__ = "1.0.0"
__all__ = [
    "Student",
    "StudentManager",
    "StudentAlreadyExistsError",
    "StudentNotFoundError",
    "JSONStorage",
    "StorageError",
]
