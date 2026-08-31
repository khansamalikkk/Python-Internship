"""Unit tests for the Student Record System."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from student_record_system.models import Student
from student_record_system.manager import (
    StudentManager,
    StudentAlreadyExistsError,
    StudentNotFoundError,
)
from student_record_system.storage import JSONStorage


@pytest.fixture
def temp_storage(tmp_path):
    return JSONStorage(tmp_path / "students.json")


@pytest.fixture
def manager(temp_storage):
    return StudentManager(temp_storage)


@pytest.fixture
def sample_student():
    return Student(student_id="S001", name="Ali Khan", age=20, grade="Senior", email="ali@example.com", gpa=3.5)


class TestStudentModel:
    def test_valid_student_creation(self, sample_student):
        assert sample_student.student_id == "S001"
        assert sample_student.name == "Ali Khan"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Student(student_id="S002", name="", age=20, grade="Senior")

    def test_invalid_age_raises(self):
        with pytest.raises(ValueError):
            Student(student_id="S003", name="Sara", age=-5, grade="Senior")

    def test_invalid_gpa_raises(self):
        with pytest.raises(ValueError):
            Student(student_id="S004", name="Sara", age=20, grade="Senior", gpa=5.0)

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Student(student_id="S005", name="Sara", age=20, grade="Senior", email="not-an-email")

    def test_to_dict_and_from_dict_roundtrip(self, sample_student):
        data = sample_student.to_dict()
        rebuilt = Student.from_dict(data)
        assert rebuilt == sample_student


class TestStudentManagerCRUD:
    def test_add_student(self, manager, sample_student):
        manager.add_student(sample_student)
        assert manager.count() == 1
        assert manager.get_student("S001") == sample_student

    def test_add_duplicate_raises(self, manager, sample_student):
        manager.add_student(sample_student)
        with pytest.raises(StudentAlreadyExistsError):
            manager.add_student(sample_student)

    def test_get_missing_raises(self, manager):
        with pytest.raises(StudentNotFoundError):
            manager.get_student("NOPE")

    def test_update_student(self, manager, sample_student):
        manager.add_student(sample_student)
        updated = manager.update_student("S001", gpa=3.9)
        assert updated.gpa == 3.9
        assert manager.get_student("S001").gpa == 3.9

    def test_update_missing_raises(self, manager):
        with pytest.raises(StudentNotFoundError):
            manager.update_student("NOPE", gpa=3.0)

    def test_delete_student(self, manager, sample_student):
        manager.add_student(sample_student)
        manager.delete_student("S001")
        assert manager.count() == 0

    def test_delete_missing_raises(self, manager):
        with pytest.raises(StudentNotFoundError):
            manager.delete_student("NOPE")

    def test_list_students_sorted(self, manager):
        manager.add_student(Student(student_id="S002", name="B", age=20, grade="Sr"))
        manager.add_student(Student(student_id="S001", name="A", age=20, grade="Sr"))
        ids = [s.student_id for s in manager.list_students()]
        assert ids == ["S001", "S002"]

    def test_search_by_name(self, manager, sample_student):
        manager.add_student(sample_student)
        results = manager.search_students("ali")
        assert len(results) == 1

    def test_search_no_match(self, manager, sample_student):
        manager.add_student(sample_student)
        assert manager.search_students("zzz") == []

    def test_average_gpa(self, manager):
        manager.add_student(Student(student_id="S001", name="A", age=20, grade="Sr", gpa=3.0))
        manager.add_student(Student(student_id="S002", name="B", age=20, grade="Sr", gpa=4.0))
        assert manager.average_gpa() == 3.5

    def test_average_gpa_empty(self, manager):
        assert manager.average_gpa() == 0.0


class TestPersistence:
    def test_data_persists_across_manager_instances(self, temp_storage, sample_student):
        manager1 = StudentManager(temp_storage)
        manager1.add_student(sample_student)

        manager2 = StudentManager(temp_storage)
        assert manager2.count() == 1
        assert manager2.get_student("S001").name == "Ali Khan"
