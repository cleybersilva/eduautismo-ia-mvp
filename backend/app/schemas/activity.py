"""
Activity Schemas - EduAutismo IA

Request and response schemas for activity-related endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseResponseSchema, BaseSchema
from app.utils.constants import (
    MAX_ACTIVITY_DURATION,
    MIN_ACTIVITY_DURATION,
    ActivityType,
    DifficultyLevel,
    GradeLevel,
    PedagogicalActivityType,
    Subject,
)


class ActivityGenerate(BaseSchema):
    """Schema for generating activity with AI."""

    student_id: UUID = Field(..., description="Student ID for personalization")
    activity_type: ActivityType = Field(..., description="Type of activity (skill domain)")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    duration_minutes: int = Field(
        ..., ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION, description="Duration in minutes"
    )
    theme: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional theme/topic",
        examples=["dinossauros", "sistema solar", "cores"],
    )

    # ===================================================================
    # MVP 3.0 - Multidisciplinary Fields (Optional)
    # ===================================================================
    subject: Optional[Subject] = Field(
        default=None,
        description="Educational subject/discipline (v3.0)",
        examples=[Subject.MATEMATICA, Subject.PORTUGUES],
    )
    grade_level: Optional[GradeLevel] = Field(
        default=None,
        description="Brazilian education grade level (v3.0)",
        examples=[GradeLevel.FUNDAMENTAL_1_3ANO, GradeLevel.MEDIO_1ANO],
    )
    pedagogical_type: Optional[PedagogicalActivityType] = Field(
        default=None,
        description="Type of pedagogical activity format (v3.0)",
        examples=[PedagogicalActivityType.EXERCICIO, PedagogicalActivityType.JOGO_EDUCATIVO],
    )
    bncc_competencies: Optional[List[str]] = Field(
        default=None,
        description="BNCC competency codes (v3.0)",
        examples=[["EF03MA01", "EF03MA02"]],
    )


class ActivityCreate(BaseSchema):
    """Schema for creating activity manually."""

    student_id: UUID = Field(..., description="Student ID")
    title: str = Field(..., min_length=3, max_length=500, description="Activity title")
    description: str = Field(..., min_length=10, description="Activity description")
    activity_type: ActivityType = Field(default=ActivityType.COGNITIVE, description="Activity type (skill domain)")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY, description="Difficulty level")
    duration_minutes: int = Field(
        default=30, ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION, description="Duration in minutes"
    )
    objectives: List[str] = Field(..., description="Learning objectives")
    materials: List[str] = Field(..., description="Required materials")
    instructions: List[str] = Field(..., description="Step-by-step instructions")
    adaptations: Optional[List[str]] = Field(default=None, description="Adaptations")
    visual_supports: Optional[List[str]] = Field(default=None, description="Visual supports")
    success_criteria: Optional[List[str]] = Field(default=None, description="Success criteria")
    theme: Optional[str] = Field(default=None, max_length=255, description="Theme")
    tags: Optional[List[str]] = Field(default=None, description="Tags")

    # MVP 3.0 - Multidisciplinary Fields
    subject: Optional[Subject] = Field(default=None, description="Subject/discipline (v3.0)")
    grade_level: Optional[GradeLevel] = Field(default=None, description="Grade level (v3.0)")
    pedagogical_type: Optional[PedagogicalActivityType] = Field(default=None, description="Pedagogical format (v3.0)")
    bncc_competencies: Optional[List[str]] = Field(default=None, description="BNCC codes (v3.0)")

    @field_validator("objectives", "materials", "instructions", mode="before")
    @classmethod
    def validate_not_empty_list(cls, value: List[str]) -> List[str]:
        """Validate lists are not empty and contain non-whitespace items."""
        if not value:
            raise ValueError("Lista não pode estar vazia")

        # Strip whitespace and filter empty strings
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]

        if not cleaned:
            raise ValueError("Lista não pode estar vazia")

        return cleaned


class ActivityUpdate(BaseSchema):
    """Schema for updating activity."""

    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, min_length=10)
    activity_type: Optional[ActivityType] = Field(default=None)
    difficulty: Optional[DifficultyLevel] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION)
    objectives: Optional[List[str]] = Field(default=None)
    materials: Optional[List[str]] = Field(default=None)
    instructions: Optional[List[str]] = Field(default=None)
    adaptations: Optional[List[str]] = Field(default=None)
    visual_supports: Optional[List[str]] = Field(default=None)
    success_criteria: Optional[List[str]] = Field(default=None)
    theme: Optional[str] = Field(default=None, max_length=255)
    tags: Optional[List[str]] = Field(default=None)
    is_published: Optional[bool] = Field(default=None)

    # MVP 3.0 - Multidisciplinary Fields
    subject: Optional[Subject] = Field(default=None, description="Subject/discipline (v3.0)")
    grade_level: Optional[GradeLevel] = Field(default=None, description="Grade level (v3.0)")
    pedagogical_type: Optional[PedagogicalActivityType] = Field(default=None, description="Pedagogical format (v3.0)")
    bncc_competencies: Optional[List[str]] = Field(default=None, description="BNCC codes (v3.0)")


class ActivityResponse(BaseResponseSchema):
    """Schema for activity response."""

    title: str
    description: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    duration_minutes: int
    objectives: List[str]
    materials: List[str]
    instructions: List[str]
    adaptations: Optional[List[str]] = None
    visual_supports: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    theme: Optional[str] = None
    tags: Optional[List[str]] = None
    generated_by_ai: bool
    generation_metadata: Optional[Dict[str, Any]] = None
    is_published: bool
    is_template: bool
    student_id: UUID
    created_by_id: Optional[UUID] = None

    # MVP 3.0 - Multidisciplinary Fields
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
    pedagogical_type: Optional[PedagogicalActivityType] = None
    bncc_competencies: Optional[List[str]] = None


class ActivityListResponse(BaseResponseSchema):
    """Schema for activity in list."""

    title: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    duration_minutes: int
    theme: Optional[str] = None
    generated_by_ai: bool
    student_id: UUID

    # MVP 3.0 - Multidisciplinary Fields (for quick filtering)
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
    pedagogical_type: Optional[PedagogicalActivityType] = None
    bncc_competencies: Optional[List[str]] = None


class ActivityFilterParams(BaseSchema):
    """Query parameters for filtering activities."""

    # V1.0 Filters
    activity_type: Optional[ActivityType] = Field(default=None, description="Filter by type (skill domain)")
    difficulty: Optional[DifficultyLevel] = Field(default=None, description="Filter by difficulty")
    theme: Optional[str] = Field(default=None, description="Filter by theme")
    generated_by_ai: Optional[bool] = Field(default=None, description="Filter AI-generated")
    student_id: Optional[UUID] = Field(default=None, description="Filter by student")

    # MVP 3.0 - Multidisciplinary Filters
    subject: Optional[Subject] = Field(default=None, description="Filter by subject/discipline (v3.0)")
    grade_level: Optional[GradeLevel] = Field(default=None, description="Filter by grade level (v3.0)")
    pedagogical_type: Optional[PedagogicalActivityType] = Field(
        default=None, description="Filter by pedagogical format (v3.0)"
    )
    has_bncc: Optional[bool] = Field(default=None, description="Filter activities with BNCC codes (v3.0)")
    bncc_code: Optional[str] = Field(
        default=None, description="Filter by specific BNCC code (e.g., 'EF03MA01') (v3.0)"
    )
