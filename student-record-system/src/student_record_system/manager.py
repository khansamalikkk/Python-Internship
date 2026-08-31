"""Core business logic for managing student records (CRUD + search)."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .models import Student
from .storage import JSONStorage

logger = logging.getLogger(__name__)


class StudentAlreadyExistsError(Exception):
    """Raised when attempting to add a student with a duplicate ID."""


class StudentNotFoundError(Exception):
    """Raised when a lookup, update, or delete targets a missing student."""


class StudentManager:
    """Manages the collection of student records and coordinates persistence."""

    def __init__(self, storage: Optional[JSONStorage] = None) -> None:
        self.storage = storage or JSONStorage()
        self._students: Dict[str, Student] = self.storage.load()

    # -- Create -----------------------------------------------------------
    def add_student(self, student: Student) -> Student:
        if student.student_id in self._students:
            raise StudentAlreadyExistsError(
                f"Student with ID '{student.student_id}' already exists."
            )
        self._students[student.student_id] = student
        self._persist()
        logger.info("Added student %s", student.student_id)
        return student

    # -- Read ---------------------------------------------------------------
    def get_student(self, student_id: str) -> Student:
        try:
            return self._students[student_id]
        except KeyError as exc:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.") from exc

    def list_students(self) -> List[Student]:
        return sorted(self._students.values(), key=lambda s: s.student_id)

    def search_students(self, keyword: str) -> List[Student]:
        """Case-insensitive search across student ID, name, and grade."""
        keyword_lower = keyword.strip().lower()
        return [
            s
            for s in self.list_students()
            if keyword_lower in s.student_id.lower()
            or keyword_lower in s.name.lower()
            or keyword_lower in s.grade.lower()
        ]

    # -- Update ---------------------------------------------------------------
    def update_student(self, student_id: str, **fields) -> Student:
        existing = self.get_student(student_id)
        updated_data = existing.to_dict()
        updated_data.update(fields)
        updated = Student.from_dict(updated_data)
        self._students[student_id] = updated
        self._persist()
        logger.info("Updated student %s", student_id)
        return updated

    # -- Delete ---------------------------------------------------------------
    def delete_student(self, student_id: str) -> None:
        if student_id not in self._students:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.")
        del self._students[student_id]
        self._persist()
        logger.info("Deleted student %s", student_id)

    # -- Stats ---------------------------------------------------------------
    def average_gpa(self) -> float:
        if not self._students:
            return 0.0
        return sum(s.gpa for s in self._students.values()) / len(self._students)

    def count(self) -> int:
        return len(self._students)

    # -- Internal ---------------------------------------------------------------
    def _persist(self) -> None:
        self.storage.save(self._students)
