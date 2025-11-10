"""
Assessment Schemas - EduAutismo IA

Request and response schemas for assessment-related endpoints.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import Field, field_validator

from backend.app.schemas.common import BaseResponseSchema, BaseSchema
from backend.app.utils.constants import (
    CompletionStatus,
    EngagementLevel,
    DifficultyRating,
    MAX_NOTES_LENGTH,
)


class AssessmentCreate(BaseSchema):
    """Schema for creating assessment."""

    activity_id: UUID = Field(..., description="Activity ID being assessed")
    student_id: UUID = Field(..., description="Student ID")
    completion_status: CompletionStatus = Field(..., description="Completion status")
    engagement_level: EngagementLevel = Field(..., description="Engagement level")
    difficulty_rating: DifficultyRating = Field(..., description="Difficulty rating")
    actual_duration_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        description="Actual duration in minutes"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
        description="Teacher's notes"
    )
    strengths_observed: Optional[str] = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
        description="Observed strengths"
    )
    challenges_observed: Optional[str] = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
        description="Observed challenges"
    )
    recommendations: Optional[str] = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
        description="Recommendations"
    )
    skills_demonstrated: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Skills demonstrated (JSON)"
    )
    behavioral_notes: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Behavioral observations (JSON)"
    )
    independence_level: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Independence level"
    )
    assistance_needed: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Assistance needed"
    )
    modifications_made: Optional[str] = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
        description="Modifications made"
    )
    objectives_met: Optional[Dict[str, bool]] = Field(
        default=None,
        description="Objectives met (JSON)"
    )

    @field_validator("notes", "strengths_observed", "challenges_observed", "recommendations", "modifications_made")
    @classmethod
    def validate_text_length(cls, value: Optional[str]) -> Optional[str]:
        """Validate text field length."""
        if value and len(value) > MAX_NOTES_LENGTH:
            raise ValueError(f"Texto não pode exceder {MAX_NOTES_LENGTH} caracteres")
        return value


class AssessmentUpdate(BaseSchema):
    """Schema for updating assessment."""

    completion_status: Optional[CompletionStatus] = Field(default=None)
    engagement_level: Optional[EngagementLevel] = Field(default=None)
    difficulty_rating: Optional[DifficultyRating] = Field(default=None)
    actual_duration_minutes: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)
    strengths_observed: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)
    challenges_observed: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)
    recommendations: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)
    skills_demonstrated: Optional[Dict[str, Any]] = Field(default=None)
    behavioral_notes: Optional[Dict[str, Any]] = Field(default=None)
    independence_level: Optional[str] = Field(default=None, max_length=50)
    assistance_needed: Optional[str] = Field(default=None, max_length=255)
    modifications_made: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)
    objectives_met: Optional[Dict[str, bool]] = Field(default=None)


class AssessmentResponse(BaseResponseSchema):
    """Schema for assessment response."""

    activity_id: UUID
    student_id: UUID
    assessed_by_id: Optional[UUID] = None
    completion_status: CompletionStatus
    engagement_level: EngagementLevel
    difficulty_rating: DifficultyRating
    actual_duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    strengths_observed: Optional[str] = None
    challenges_observed: Optional[str] = None
    recommendations: Optional[str] = None
    skills_demonstrated: Optional[Dict[str, Any]] = None
    behavioral_notes: Optional[Dict[str, Any]] = None
    independence_level: Optional[str] = None
    assistance_needed: Optional[str] = None
    modifications_made: Optional[str] = None
    objectives_met: Optional[Dict[str, bool]] = None


class AssessmentListResponse(BaseResponseSchema):
    """Schema for assessment in list."""

    activity_id: UUID
    student_id: UUID
    completion_status: CompletionStatus
    engagement_level: EngagementLevel
    difficulty_rating: DifficultyRating
    actual_duration_minutes: Optional[int] = None


class AssessmentFilterParams(BaseSchema):
    """Query parameters for filtering assessments."""

    student_id: Optional[UUID] = Field(default=None, description="Filter by student")
    activity_id: Optional[UUID] = Field(default=None, description="Filter by activity")
    completion_status: Optional[CompletionStatus] = Field(default=None, description="Filter by status")
    engagement_level: Optional[EngagementLevel] = Field(default=None, description="Filter by engagement")
    difficulty_rating: Optional[DifficultyRating] = Field(default=None, description="Filter by difficulty rating")


class ProgressAnalysisRequest(BaseSchema):
    """Request for progress analysis."""

    student_id: UUID = Field(..., description="Student ID to analyze")
    time_period: Optional[str] = Field(
        default=None,
        description="Time period (e.g., 'last month', 'last 3 months')",
        examples=["last month", "last 3 months", "last year"]
    )


class ProgressAnalysisResponse(BaseSchema):
    """Response for progress analysis."""

    student_id: UUID
    summary: str = Field(..., description="Progress summary")
    strengths: list[str] = Field(default=[], description="Identified strengths")
    areas_for_improvement: list[str] = Field(default=[], description="Areas needing improvement")
    patterns_observed: list[str] = Field(default=[], description="Observed patterns")
    recommendations: list[str] = Field(default=[], description="AI recommendations")
