"""
Student Service - EduAutismo IA

Business logic for student management.
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import (
    StudentNotFoundError,
    PermissionDeniedError,
    ValidationError as AppValidationError,
)
from backend.app.models.student import Student
from backend.app.schemas.student import StudentCreate, StudentUpdate
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class StudentService:
    """Service for student operations."""

    @staticmethod
    async def create_student(
        db: AsyncSession,
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
                - (
                    (today.month, today.day)
                    < (student_data.date_of_birth.month, student_data.date_of_birth.day)
                )
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
            await db.commit()
            await db.refresh(student)

            logger.info(f"Student created: {student.id} by teacher {teacher_id}")

            return student

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating student: {e}")
            raise

    @staticmethod
    async def get_student(
        db: AsyncSession,
        student_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> Student:
        """
        Get student by ID.

        Args:
            db: Database session
            student_id: Student ID
            teacher_id: Optional teacher ID for permission check

        Returns:
            Student

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
        """
        result = await db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()

        if not student:
            raise StudentNotFoundError(str(student_id))

        # Check permission if teacher_id provided
        if teacher_id and student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para acessar este aluno",
                resource=f"student:{student_id}",
            )

        return student

    @staticmethod
    async def list_students(
        db: AsyncSession,
        teacher_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Student], int]:
        """
        List students with pagination.

        Args:
            db: Database session
            teacher_id: Filter by teacher (None = all)
            skip: Number to skip
            limit: Max results
            is_active: Filter by active status

        Returns:
            Tuple of (students list, total count)
        """
        # Build query
        query = select(Student)

        if teacher_id:
            query = query.where(Student.teacher_id == teacher_id)

        if is_active is not None:
            query = query.where(Student.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Student.created_at.desc())
        result = await db.execute(query)
        students = result.scalars().all()

        return list(students), total

    @staticmethod
    async def update_student(
        db: AsyncSession,
        student_id: UUID,
        student_data: StudentUpdate,
        teacher_id: Optional[UUID] = None,
    ) -> Student:
        """
        Update student.

        Args:
            db: Database session
            student_id: Student ID
            student_data: Update data
            teacher_id: Optional teacher ID for permission check

        Returns:
            Updated student

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
        """
        # Get student (with permission check)
        student = await StudentService.get_student(db, student_id, teacher_id)

        # Update fields
        update_data = student_data.model_dump(exclude_unset=True)

        # Recalculate age if date_of_birth changed
        if "date_of_birth" in update_data:
            today = date.today()
            dob = update_data["date_of_birth"]
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            update_data["age"] = age

        for field, value in update_data.items():
            setattr(student, field, value)

        await db.commit()
        await db.refresh(student)

        logger.info(f"Student updated: {student_id}")

        return student

    @staticmethod
    async def delete_student(
        db: AsyncSession,
        student_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> None:
        """
        Delete student (soft delete by setting is_active=False).

        Args:
            db: Database session
            student_id: Student ID
            teacher_id: Optional teacher ID for permission check

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
        """
        student = await StudentService.get_student(db, student_id, teacher_id)

        student.is_active = False
        await db.commit()

        logger.info(f"Student deactivated: {student_id}")

    @staticmethod
    async def get_student_profile(
        db: AsyncSession,
        student_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> dict:
        """
        Get student profile formatted for AI services.

        Args:
            db: Database session
            student_id: Student ID
            teacher_id: Optional teacher ID for permission check

        Returns:
            Student profile dict
        """
        student = await StudentService.get_student(db, student_id, teacher_id)
        return student.to_profile_dict()

    @staticmethod
    async def update_learning_profile(
        db: AsyncSession,
        student_id: UUID,
        learning_profile: dict,
        teacher_id: Optional[UUID] = None,
    ) -> Student:
        """
        Update student's learning profile.

        Args:
            db: Database session
            student_id: Student ID
            learning_profile: New learning profile
            teacher_id: Optional teacher ID for permission check

        Returns:
            Updated student
        """
        student = await StudentService.get_student(db, student_id, teacher_id)

        student.learning_profile = learning_profile
        await db.commit()
        await db.refresh(student)

        logger.info(f"Learning profile updated for student: {student_id}")

        return student

    @staticmethod
    async def search_students(
        db: AsyncSession,
        query: str,
        teacher_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Student], int]:
        """
        Search students by name.

        Args:
            db: Database session
            query: Search query
            teacher_id: Filter by teacher
            skip: Number to skip
            limit: Max results

        Returns:
            Tuple of (students list, total count)
        """
        search_query = select(Student).where(Student.name.ilike(f"%{query}%"))

        if teacher_id:
            search_query = search_query.where(Student.teacher_id == teacher_id)

        # Count
        count_query = select(func.count()).select_from(search_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get results
        search_query = search_query.offset(skip).limit(limit).order_by(Student.name)
        result = await db.execute(search_query)
        students = result.scalars().all()

        return list(students), total
