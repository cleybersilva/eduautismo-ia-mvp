"""
Assessment Service - EduAutismo IA (Sync Version)

Business logic for assessment management and progress analysis.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.exceptions import (
    AssessmentNotFoundError,
    ActivityNotFoundError,
    StudentNotFoundError,
    PermissionDeniedError,
)
from app.models.assessment import Assessment
from app.models.activity import Activity
from app.models.student import Student
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AssessmentService:
    """Service for assessment operations (synchronous)."""

    @staticmethod
    def create_assessment(
        db: Session,
        assessment_data: AssessmentCreate,
        teacher_id: UUID,
    ) -> Assessment:
        """
        Create assessment.

        Args:
            db: Database session
            assessment_data: Assessment data
            teacher_id: Teacher creating the assessment

        Returns:
            Created assessment

        Raises:
            ActivityNotFoundError: If activity not found
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
        """
        # Get activity
        activity = db.query(Activity).filter(Activity.id == assessment_data.activity_id).first()

        if not activity:
            raise ActivityNotFoundError(str(assessment_data.activity_id))

        # Get student
        student = db.query(Student).filter(Student.id == assessment_data.student_id).first()

        if not student:
            raise StudentNotFoundError(str(assessment_data.student_id))

        # Check permission
        if student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para avaliar este aluno"
            )

        # Create assessment
        assessment = Assessment(
            **assessment_data.model_dump(),
            assessed_by_id=teacher_id,
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        logger.info(f"Assessment created: {assessment.id} for activity {activity.id}")

        return assessment

    @staticmethod
    def get_assessment(
        db: Session,
        assessment_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> Assessment:
        """
        Get assessment by ID.

        Args:
            db: Database session
            assessment_id: Assessment ID
            teacher_id: Optional teacher ID for permission check

        Returns:
            Assessment object

        Raises:
            AssessmentNotFoundError: If assessment not found
            PermissionDeniedError: If teacher doesn't have access
        """
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()

        if not assessment:
            raise AssessmentNotFoundError(str(assessment_id))

        # Check permission if teacher_id provided
        if teacher_id:
            student = db.query(Student).filter(Student.id == assessment.student_id).first()
            if student and student.teacher_id != teacher_id:
                raise PermissionDeniedError(
                    message="Você não tem permissão para ver esta avaliação"
                )

        return assessment

    @staticmethod
    def list_assessments(
        db: Session,
        student_id: Optional[UUID] = None,
        activity_id: Optional[UUID] = None,
        teacher_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Assessment], int]:
        """
        List assessments with filters.

        Args:
            db: Database session
            student_id: Filter by student
            activity_id: Filter by activity
            teacher_id: Filter by teacher's students
            skip: Number to skip
            limit: Max results

        Returns:
            Tuple of (assessments list, total count)
        """
        query = db.query(Assessment)

        # Filters
        if student_id:
            query = query.filter(Assessment.student_id == student_id)

        if activity_id:
            query = query.filter(Assessment.activity_id == activity_id)

        if teacher_id:
            query = query.join(Student).filter(Student.teacher_id == teacher_id)

        # Count
        total = query.count()

        # Get results - order_by MUST come before offset/limit
        assessments = query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()

        return assessments, total

    @staticmethod
    def update_assessment(
        db: Session,
        assessment_id: UUID,
        assessment_data: AssessmentUpdate,
        teacher_id: UUID,
    ) -> Assessment:
        """
        Update assessment.

        Args:
            db: Database session
            assessment_id: Assessment ID
            assessment_data: Update data
            teacher_id: Teacher updating

        Returns:
            Updated assessment

        Raises:
            AssessmentNotFoundError: If assessment not found
            PermissionDeniedError: If teacher doesn't have access
        """
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()

        if not assessment:
            raise AssessmentNotFoundError(str(assessment_id))

        # Check permission
        student = db.query(Student).filter(Student.id == assessment.student_id).first()
        if student and student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para atualizar esta avaliação"
            )

        # Update fields
        update_data = assessment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)

        db.commit()
        db.refresh(assessment)

        logger.info(f"Assessment updated: {assessment.id}")

        return assessment

    @staticmethod
    def delete_assessment(
        db: Session,
        assessment_id: UUID,
        teacher_id: UUID,
    ) -> bool:
        """
        Delete assessment.

        Args:
            db: Database session
            assessment_id: Assessment ID
            teacher_id: Teacher deleting

        Returns:
            True if deleted

        Raises:
            AssessmentNotFoundError: If assessment not found
            PermissionDeniedError: If teacher doesn't have access
        """
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()

        if not assessment:
            raise AssessmentNotFoundError(str(assessment_id))

        # Check permission
        student = db.query(Student).filter(Student.id == assessment.student_id).first()
        if student and student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para deletar esta avaliação"
            )

        db.delete(assessment)
        db.commit()

        logger.info(f"Assessment deleted: {assessment_id}")

        return True
