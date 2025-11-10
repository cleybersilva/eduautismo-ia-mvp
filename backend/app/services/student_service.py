"""
Student business logic service.

This module contains the business logic for student operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """
    Service class for Student business logic.

    This class handles all business logic operations for student.
    """

    @staticmethod
    def create(db: Session, student_data: StudentCreate) -> Student:
        """
        Create a new student.

        Args:
            db: Database session
            student_data: Student creation data

        Returns:
            Created student object
        """
        # TODO: Implement creation logic
        db_obj = Student(**student_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, student_id: int) -> Optional[Student]:
        """
        Get a student by ID.

        Args:
            db: Database session
            student_id: Student ID

        Returns:
            Student object or None if not found
        """
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
        """
        Get multiple students.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of student objects
        """
        return db.query(Student).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        """
        Update a student.

        Args:
            db: Database session
            student_id: Student ID
            student_data: Update data

        Returns:
            Updated student object or None if not found
        """
        db_obj = StudentService.get(db, student_id)
        if not db_obj:
            return None

        update_data = student_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, student_id: int) -> bool:
        """
        Delete a student.

        Args:
            db: Database session
            student_id: Student ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = StudentService.get(db, student_id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True
