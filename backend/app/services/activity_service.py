"""
Activity Service - EduAutismo IA

Business logic for activity management and AI generation.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import (
    ActivityNotFoundError,
    StudentNotFoundError,
    PermissionDeniedError,
    OpenAIError,
)
from backend.app.models.activity import Activity
from backend.app.models.student import Student
from backend.app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityGenerate
from backend.app.services.nlp_service import get_nlp_service
from backend.app.utils.constants import ActivityType, DifficultyLevel
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class ActivityService:
    """Service for activity operations."""

    @staticmethod
    async def generate_activity(
        db: AsyncSession,
        activity_data: ActivityGenerate,
        teacher_id: UUID,
    ) -> Activity:
        """
        Generate activity using AI.

        Args:
            db: Database session
            activity_data: Generation parameters
            teacher_id: Teacher generating the activity

        Returns:
            Generated activity

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
            OpenAIError: If AI generation fails
        """
        # Get student
        result = await db.execute(
            select(Student).where(Student.id == activity_data.student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise StudentNotFoundError(str(activity_data.student_id))

        # Check permission
        if student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para criar atividades para este aluno"
            )

        # Get student profile for AI
        student_profile = student.to_profile_dict()

        # Generate with AI
        try:
            nlp_service = get_nlp_service()
            generated = await nlp_service.generate_activity(
                student_profile=student_profile,
                activity_type=activity_data.activity_type,
                difficulty=activity_data.difficulty,
                duration_minutes=activity_data.duration_minutes,
                theme=activity_data.theme,
            )

            # Create activity from generated content
            activity = Activity(
                title=generated.title,
                description=generated.description,
                activity_type=activity_data.activity_type,
                difficulty=activity_data.difficulty,
                duration_minutes=generated.duration_minutes,
                objectives=generated.objectives,
                materials=generated.materials,
                instructions=generated.instructions,
                adaptations=generated.adaptations,
                visual_supports=generated.visual_supports,
                success_criteria=generated.success_criteria,
                theme=activity_data.theme,
                generated_by_ai=True,
                generation_metadata={
                    "student_profile": student_profile,
                    "model": nlp_service.default_model,
                },
                student_id=activity_data.student_id,
                created_by_id=teacher_id,
            )

            db.add(activity)
            await db.commit()
            await db.refresh(activity)

            logger.info(
                f"Activity generated with AI: {activity.id} for student {student.id}"
            )

            return activity

        except OpenAIError as e:
            logger.error(f"AI generation failed: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error generating activity: {e}")
            raise

    @staticmethod
    async def create_activity(
        db: AsyncSession,
        activity_data: ActivityCreate,
        teacher_id: UUID,
    ) -> Activity:
        """
        Create activity manually.

        Args:
            db: Database session
            activity_data: Activity data
            teacher_id: Teacher creating the activity

        Returns:
            Created activity

        Raises:
            StudentNotFoundError: If student not found
            PermissionDeniedError: If teacher doesn't own student
        """
        # Get student and check permission
        result = await db.execute(
            select(Student).where(Student.id == activity_data.student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise StudentNotFoundError(str(activity_data.student_id))

        if student.teacher_id != teacher_id:
            raise PermissionDeniedError(
                message="Você não tem permissão para criar atividades para este aluno"
            )

        # Create activity
        activity = Activity(
            **activity_data.model_dump(),
            generated_by_ai=False,
            created_by_id=teacher_id,
        )

        db.add(activity)
        await db.commit()
        await db.refresh(activity)

        logger.info(f"Activity created manually: {activity.id}")

        return activity

    @staticmethod
    async def get_activity(
        db: AsyncSession,
        activity_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> Activity:
        """
        Get activity by ID.

        Args:
            db: Database session
            activity_id: Activity ID
            teacher_id: Optional teacher ID for permission check

        Returns:
            Activity

        Raises:
            ActivityNotFoundError: If activity not found
            PermissionDeniedError: If teacher doesn't own activity
        """
        result = await db.execute(select(Activity).where(Activity.id == activity_id))
        activity = result.scalar_one_or_none()

        if not activity:
            raise ActivityNotFoundError(str(activity_id))

        # Check permission if teacher_id provided
        if teacher_id:
            # Get student to check teacher
            student_result = await db.execute(
                select(Student).where(Student.id == activity.student_id)
            )
            student = student_result.scalar_one_or_none()

            if student and student.teacher_id != teacher_id:
                raise PermissionDeniedError(
                    message="Você não tem permissão para acessar esta atividade"
                )

        return activity

    @staticmethod
    async def list_activities(
        db: AsyncSession,
        student_id: Optional[UUID] = None,
        teacher_id: Optional[UUID] = None,
        activity_type: Optional[ActivityType] = None,
        difficulty: Optional[DifficultyLevel] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Activity], int]:
        """
        List activities with filters.

        Args:
            db: Database session
            student_id: Filter by student
            teacher_id: Filter by teacher's students
            activity_type: Filter by type
            difficulty: Filter by difficulty
            skip: Number to skip
            limit: Max results

        Returns:
            Tuple of (activities list, total count)
        """
        query = select(Activity)

        # Filters
        if student_id:
            query = query.where(Activity.student_id == student_id)

        if teacher_id:
            # Join with student to filter by teacher
            query = query.join(Student).where(Student.teacher_id == teacher_id)

        if activity_type:
            query = query.where(Activity.activity_type == activity_type)

        if difficulty:
            query = query.where(Activity.difficulty == difficulty)

        # Only published activities
        query = query.where(Activity.is_published == True)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get results
        query = query.offset(skip).limit(limit).order_by(Activity.created_at.desc())
        result = await db.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    @staticmethod
    async def update_activity(
        db: AsyncSession,
        activity_id: UUID,
        activity_data: ActivityUpdate,
        teacher_id: Optional[UUID] = None,
    ) -> Activity:
        """
        Update activity.

        Args:
            db: Database session
            activity_id: Activity ID
            activity_data: Update data
            teacher_id: Optional teacher ID for permission check

        Returns:
            Updated activity

        Raises:
            ActivityNotFoundError: If activity not found
            PermissionDeniedError: If teacher doesn't own activity
        """
        activity = await ActivityService.get_activity(db, activity_id, teacher_id)

        # Update fields
        update_data = activity_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(activity, field, value)

        await db.commit()
        await db.refresh(activity)

        logger.info(f"Activity updated: {activity_id}")

        return activity

    @staticmethod
    async def delete_activity(
        db: AsyncSession,
        activity_id: UUID,
        teacher_id: Optional[UUID] = None,
    ) -> None:
        """
        Delete activity (soft delete by unpublishing).

        Args:
            db: Database session
            activity_id: Activity ID
            teacher_id: Optional teacher ID for permission check

        Raises:
            ActivityNotFoundError: If activity not found
            PermissionDeniedError: If teacher doesn't own activity
        """
        activity = await ActivityService.get_activity(db, activity_id, teacher_id)

        activity.is_published = False
        await db.commit()

        logger.info(f"Activity unpublished: {activity_id}")

    @staticmethod
    async def get_activities_by_theme(
        db: AsyncSession,
        theme: str,
        teacher_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Activity], int]:
        """
        Get activities by theme.

        Args:
            db: Database session
            theme: Theme to search
            teacher_id: Optional teacher filter
            skip: Number to skip
            limit: Max results

        Returns:
            Tuple of (activities list, total count)
        """
        query = select(Activity).where(Activity.theme.ilike(f"%{theme}%"))

        if teacher_id:
            query = query.join(Student).where(Student.teacher_id == teacher_id)

        query = query.where(Activity.is_published == True)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get results
        query = query.offset(skip).limit(limit).order_by(Activity.created_at.desc())
        result = await db.execute(query)
        activities = result.scalars().all()

        return list(activities), total
