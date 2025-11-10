"""
Assessment Service - EduAutismo IA

Business logic for assessment management and progress analysis.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import (
    AssessmentNotFoundError,
    ActivityNotFoundError,
    StudentNotFoundError,
    PermissionDeniedError,
    OpenAIError,
)
from backend.app.models.assessment import Assessment
from backend.app.models.activity import Activity
from backend.app.models.student import Student
from backend.app.schemas.assessment import AssessmentCreate, AssessmentUpdate
from backend.app.services.nlp_service import get_nlp_service
from backend.app.utils.constants import CompletionStatus, EngagementLevel, DifficultyRating
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class AssessmentService:
    """Service for assessment operations."""

    @staticmethod
    async def create_assessment(
        db: AsyncSession,
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
        activity_result = await db.execute(
            select(Activity).where(Activity.id == assessment_data.activity_id)
        )
        activity = activity_result.scalar_one_or_none()

        if not activity:
            raise ActivityNotFoundError(str(assessment_data.activity_id))

        # Get student
        student_result = await db.execute(
            select(Student).where(Student.id == assessment_data.student_id)
        )
        student = student_result.scalar_one_or_none()

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
        await db.commit()
        await db.refresh(assessment)

        logger.info(f"Assessment created: {assessment.id} for activity {activity.id}")

        return assessment

    @staticmethod
    async def get_assessment(
        db: AsyncSession,
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
            Assessment

        Raises:
            AssessmentNotFoundError: If assessment not found
            PermissionDeniedError: If teacher doesn't own assessment
        """
        result = await db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise AssessmentNotFoundError(str(assessment_id))

        # Check permission
        if teacher_id:
            student_result = await db.execute(
                select(Student).where(Student.id == assessment.student_id)
            )
            student = student_result.scalar_one_or_none()

            if student and student.teacher_id != teacher_id:
                raise PermissionDeniedError(
                    message="Você não tem permissão para acessar esta avaliação"
                )

        return assessment

    @staticmethod
    async def list_assessments(
        db: AsyncSession,
        student_id: Optional[UUID] = None,
        activity_id: Optional[UUID] = None,
        teacher_id: Optional[UUID] = None,
        completion_status: Optional[CompletionStatus] = None,
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
            completion_status: Filter by status
            skip: Number to skip
            limit: Max results

        Returns:
            Tuple of (assessments list, total count)
        """
        query = select(Assessment)

        # Filters
        if student_id:
            query = query.where(Assessment.student_id == student_id)

        if activity_id:
            query = query.where(Assessment.activity_id == activity_id)

        if teacher_id:
            query = query.join(Student).where(Student.teacher_id == teacher_id)

        if completion_status:
            query = query.where(Assessment.completion_status == completion_status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get results
        query = query.offset(skip).limit(limit).order_by(Assessment.created_at.desc())
        result = await db.execute(query)
        assessments = result.scalars().all()

        return list(assessments), total

    @staticmethod
    async def update_assessment(
        db: AsyncSession,
        assessment_id: UUID,
        assessment_data: AssessmentUpdate,
        teacher_id: Optional[UUID] = None,
    ) -> Assessment:
        """
        Update assessment.

        Args:
            db: Database session
            assessment_id: Assessment ID
            assessment_data: Update data
            teacher_id: Optional teacher ID for permission check

        Returns:
            Updated assessment
        """
        assessment = await AssessmentService.get_assessment(
            db, assessment_id, teacher_id
        )

        # Update fields
        update_data = assessment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)

        await db.commit()
        await db.refresh(assessment)

        logger.info(f"Assessment updated: {assessment_id}")

        return assessment

    @staticmethod
    async def delete_assessment(
        db: AsyncSession,
        assessment_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> None:
        """
        Delete assessment.

        Args:
            db: Database session
            assessment_id: Assessment ID
            teacher_id: Optional teacher ID for permission check
        """
        assessment = await AssessmentService.get_assessment(
            db, assessment_id, teacher_id
        )

        await db.delete(assessment)
        await db.commit()

        logger.info(f"Assessment deleted: {assessment_id}")

    @staticmethod
    async def analyze_student_progress(
        db: AsyncSession,
        student_id: UUID,
        teacher_id: Optional[UUID] = None,
        time_period: Optional[str] = None,
    ) -> dict:
        """
        Analyze student progress using AI.

        Args:
            db: Database session
            student_id: Student ID
            teacher_id: Optional teacher ID for permission check
            time_period: Optional time period filter

        Returns:
            Progress analysis dict

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
            OpenAIError: If AI analysis fails
        """
        # Get student
        student_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            raise StudentNotFoundError(str(student_id))

        # Check permission
        if teacher_id and student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para analisar este aluno"
            )

        # Get assessments
        query = select(Assessment).where(Assessment.student_id == student_id)
        
        # TODO: Add time period filtering
        # if time_period:
        #     query = query.where(...)

        query = query.order_by(Assessment.created_at.desc()).limit(50)
        result = await db.execute(query)
        assessments = result.scalars().all()

        if not assessments:
            return {
                "summary": "Nenhuma avaliação encontrada para análise",
                "strengths": [],
                "areas_for_improvement": [],
                "patterns_observed": [],
                "recommendations": [],
            }

        # Prepare data for AI
        student_profile = student.to_profile_dict()
        assessments_data = [assessment.to_dict() for assessment in assessments]

        # Analyze with AI
        try:
            nlp_service = get_nlp_service()
            analysis = await nlp_service.analyze_progress(
                student_profile=student_profile,
                assessments=assessments_data,
                time_period=time_period,
            )

            logger.info(f"Progress analysis completed for student: {student_id}")

            return {
                "student_id": student_id,
                "summary": analysis.summary,
                "strengths": analysis.strengths,
                "areas_for_improvement": analysis.areas_for_improvement,
                "patterns_observed": analysis.patterns_observed,
                "recommendations": analysis.recommendations,
            }

        except OpenAIError as e:
            logger.error(f"AI progress analysis failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing progress: {e}")
            raise

    @staticmethod
    async def get_student_statistics(
        db: AsyncSession,
        student_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> dict:
        """
        Get student statistics.

        Args:
            db: Database session
            student_id: Student ID
            teacher_id: Optional teacher ID for permission check

        Returns:
            Statistics dict
        """
        # Get student
        student_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            raise StudentNotFoundError(str(student_id))

        # Check permission
        if teacher_id and student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para acessar estatísticas deste aluno"
            )

        # Count activities
        activities_count = await db.execute(
            select(func.count())
            .select_from(Activity)
            .where(Activity.student_id == student_id)
        )
        total_activities = activities_count.scalar_one()

        # Count assessments
        assessments_count = await db.execute(
            select(func.count())
            .select_from(Assessment)
            .where(Assessment.student_id == student_id)
        )
        total_assessments = assessments_count.scalar_one()

        # Count completed
        completed_count = await db.execute(
            select(func.count())
            .select_from(Assessment)
            .where(
                Assessment.student_id == student_id,
                Assessment.completion_status == CompletionStatus.COMPLETED,
            )
        )
        completed_activities = completed_count.scalar_one()

        # Average engagement
        # Convert enum to numeric for averaging (none=0, low=1, medium=2, high=3, very_high=4)
        assessments_result = await db.execute(
            select(Assessment.engagement_level)
            .where(Assessment.student_id == student_id)
        )
        engagements = assessments_result.scalars().all()

        engagement_map = {
            EngagementLevel.NONE: 0,
            EngagementLevel.LOW: 1,
            EngagementLevel.MEDIUM: 2,
            EngagementLevel.HIGH: 3,
            EngagementLevel.VERY_HIGH: 4,
        }

        if engagements:
            avg_engagement = sum(engagement_map[e] for e in engagements) / len(
                engagements
            )
        else:
            avg_engagement = None

        return {
            "total_activities": total_activities,
            "total_assessments": total_assessments,
            "completed_activities": completed_activities,
            "completion_rate": (
                (completed_activities / total_assessments * 100)
                if total_assessments > 0
                else 0
            ),
            "average_engagement": avg_engagement,
        }
