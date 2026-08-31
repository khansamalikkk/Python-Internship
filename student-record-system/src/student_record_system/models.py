"""Data models for the Student Record System."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict


@dataclass
class Student:
    """Represents a single student record.

    Attributes:
        student_id: Unique identifier for the student (e.g. roll number).
        name: Full name of the student.
        age: Age of the student in years.
        grade: Current grade/year/class of the student.
        email: Contact email address.
        gpa: Grade point average (0.0 - 4.0 scale).
    """

    student_id: str
    name: str
    age: int
    grade: str
    email: str = ""
    gpa: float = 0.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate field values, raising ValueError on the first problem found."""
        if not self.student_id or not str(self.student_id).strip():
            raise ValueError("student_id cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not isinstance(self.age, int) or self.age <= 0 or self.age > 120:
            raise ValueError("age must be a positive integer (1-120)")
        if not self.grade or not str(self.grade).strip():
            raise ValueError("grade cannot be empty")
        if self.email and "@" not in self.email:
            raise ValueError("email must contain '@'")
        if not (0.0 <= float(self.gpa) <= 4.0):
            raise ValueError("gpa must be between 0.0 and 4.0")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            age=int(data["age"]),
            grade=str(data["grade"]),
            email=str(data.get("email", "")),
            gpa=float(data.get("gpa", 0.0)),
        )

    def __str__(self) -> str:
        return (
            f"ID: {self.student_id} | Name: {self.name} | Age: {self.age} | "
            f"Grade: {self.grade} | Email: {self.email or '-'} | GPA: {self.gpa:.2f}"
        )
