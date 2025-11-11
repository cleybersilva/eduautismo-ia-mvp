"""
Activity Schemas - EduAutismo IA

Request and response schemas for activity-related endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseResponseSchema, BaseSchema
from app.utils.constants import MAX_ACTIVITY_DURATION, MIN_ACTIVITY_DURATION, ActivityType, DifficultyLevel


class ActivityGenerate(BaseSchema):
    """Schema for generating activity with AI."""

    student_id: UUID = Field(..., description="Student ID for personalization")
    activity_type: ActivityType = Field(..., description="Type of activity")
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


class ActivityCreate(BaseSchema):
    """Schema for creating activity manually."""

    student_id: UUID = Field(..., description="Student ID")
    title: str = Field(..., min_length=3, max_length=500, description="Activity title")
    description: str = Field(..., min_length=10, description="Activity description")
    activity_type: ActivityType = Field(..., description="Activity type")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    duration_minutes: int = Field(..., ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION)
    objectives: List[str] = Field(..., min_length=1, description="Learning objectives")
    materials: List[str] = Field(..., min_length=1, description="Required materials")
    instructions: List[str] = Field(..., min_length=1, description="Step-by-step instructions")
    adaptations: Optional[List[str]] = Field(default=None, description="Adaptations")
    visual_supports: Optional[List[str]] = Field(default=None, description="Visual supports")
    success_criteria: Optional[List[str]] = Field(default=None, description="Success criteria")
    theme: Optional[str] = Field(default=None, max_length=255, description="Theme")
    tags: Optional[List[str]] = Field(default=None, description="Tags")

    @field_validator("objectives", "materials", "instructions")
    @classmethod
    def validate_not_empty_list(cls, value: List[str]) -> List[str]:
        """Validate lists are not empty."""
        if not value or all(not item.strip() for item in value):
            raise ValueError("Lista não pode estar vazia")
        return [item.strip() for item in value if item.strip()]


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


class ActivityListResponse(BaseResponseSchema):
    """Schema for activity in list."""

    title: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    duration_minutes: int
    theme: Optional[str] = None
    generated_by_ai: bool
    student_id: UUID


class ActivityFilterParams(BaseSchema):
    """Query parameters for filtering activities."""

    activity_type: Optional[ActivityType] = Field(default=None, description="Filter by type")
    difficulty: Optional[DifficultyLevel] = Field(default=None, description="Filter by difficulty")
    theme: Optional[str] = Field(default=None, description="Filter by theme")
    generated_by_ai: Optional[bool] = Field(default=None, description="Filter AI-generated")
    student_id: Optional[UUID] = Field(default=None, description="Filter by student")
