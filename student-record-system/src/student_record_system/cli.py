"""Command-line interface for the Student Record System."""
from __future__ import annotations

import logging
import sys

from .manager import StudentAlreadyExistsError, StudentManager, StudentNotFoundError
from .models import Student
from .storage import JSONStorage, StorageError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MENU = """
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
"""


def prompt_int(message: str) -> int:
    while True:
        raw = input(message).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid whole number.")


def prompt_float(message: str) -> float:
    while True:
        raw = input(message).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def add_student_flow(manager: StudentManager) -> None:
    print("\n-- Add Student --")
    student_id = input("Student ID: ").strip()
    name = input("Name: ").strip()
    age = prompt_int("Age: ")
    grade = input("Grade/Class: ").strip()
    email = input("Email (optional): ").strip()
    gpa = prompt_float("GPA (0.0 - 4.0): ")
    try:
        student = Student(
            student_id=student_id, name=name, age=age, grade=grade, email=email, gpa=gpa
        )
        manager.add_student(student)
        print(f"Added: {student}")
    except (ValueError, StudentAlreadyExistsError) as exc:
        print(f"Error: {exc}")


def view_all_flow(manager: StudentManager) -> None:
    print("\n-- All Students --")
    students = manager.list_students()
    if not students:
        print("No records found.")
        return
    for s in students:
        print(s)


def search_flow(manager: StudentManager) -> None:
    keyword = input("\nSearch keyword (ID, name, or grade): ").strip()
    results = manager.search_students(keyword)
    if not results:
        print("No matches found.")
        return
    for s in results:
        print(s)


def update_flow(manager: StudentManager) -> None:
    student_id = input("\nStudent ID to update: ").strip()
    try:
        existing = manager.get_student(student_id)
    except StudentNotFoundError as exc:
        print(f"Error: {exc}")
        return

    print(f"Current record: {existing}")
    print("Leave a field blank to keep its current value.")
    fields = {}

    name = input(f"Name [{existing.name}]: ").strip()
    if name:
        fields["name"] = name

    age = input(f"Age [{existing.age}]: ").strip()
    if age:
        try:
            fields["age"] = int(age)
        except ValueError:
            print("Invalid age, skipping.")

    grade = input(f"Grade [{existing.grade}]: ").strip()
    if grade:
        fields["grade"] = grade

    email = input(f"Email [{existing.email}]: ").strip()
    if email:
        fields["email"] = email

    gpa = input(f"GPA [{existing.gpa}]: ").strip()
    if gpa:
        try:
            fields["gpa"] = float(gpa)
        except ValueError:
            print("Invalid GPA, skipping.")

    try:
        updated = manager.update_student(student_id, **fields)
        print(f"Updated: {updated}")
    except ValueError as exc:
        print(f"Error: {exc}")


def delete_flow(manager: StudentManager) -> None:
    student_id = input("\nStudent ID to delete: ").strip()
    confirm = input(f"Are you sure you want to delete '{student_id}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    try:
        manager.delete_student(student_id)
        print("Deleted.")
    except StudentNotFoundError as exc:
        print(f"Error: {exc}")


def stats_flow(manager: StudentManager) -> None:
    print("\n-- Statistics --")
    print(f"Total students: {manager.count()}")
    print(f"Average GPA: {manager.average_gpa():.2f}")


def main() -> None:
    try:
        manager = StudentManager(JSONStorage("students.json"))
    except StorageError as exc:
        logger.error("Could not initialize storage: %s", exc)
        sys.exit(1)

    actions = {
        "1": add_student_flow,
        "2": view_all_flow,
        "3": search_flow,
        "4": update_flow,
        "5": delete_flow,
        "6": stats_flow,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option. Please choose 1-7.")
            continue
        try:
            action(manager)
        except StorageError as exc:
            logger.error("Storage error: %s", exc)
            print(f"A storage error occurred: {exc}")


if __name__ == "__main__":
    main()
