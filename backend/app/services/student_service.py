"""
Student Service - EduAutismo IA

Business logic for student management.
"""

from datetime import date
from uuid import UUID

from app.models.student import Student
from app.schemas.student import StudentCreate
from app.utils.logger import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class StudentService:
    """Service for student operations."""

    @staticmethod
    def create_student(
        db: Session,
        student_data: StudentCreate,
        teacher_id: UUID,
    ) -> Student:
        """
        Create new student.

        Args:
            db: Database session
            student_data: Student data
            teacher_id: Teacher creating the student

        Returns:
            Created student

        Raises:
            AppValidationError: If data is invalid
        """
        try:
            # Calculate age from date of birth
            today = date.today()
            age = (
                today.year
                - student_data.date_of_birth.year
                - ((today.month, today.day) < (student_data.date_of_birth.month, student_data.date_of_birth.day))
            )

            # Create student instance
            student = Student(
                name=student_data.name,
                date_of_birth=student_data.date_of_birth,
                age=age,
                diagnosis=student_data.diagnosis,
                tea_level=student_data.tea_level,
                interests=student_data.interests,
                learning_profile=student_data.learning_profile,
                teacher_id=teacher_id,
            )

            db.add(student)
            db.commit()
            db.refresh(student)

            logger.info(f"Student created: {student.id} by teacher {teacher_id}")

            return student

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating student: {e}")
            raise

    # TODO: Implement other service methods (get, list, update, delete, search)
