"""
Assessment Model - EduAutismo IA

Represents assessments/evaluations of completed activities.
"""

from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.utils.constants import CompletionStatus, DifficultyRating, EngagementLevel

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.student import Student
    from app.models.user import User


class Assessment(BaseModel):
    """
    Assessment model for tracking activity completion and student performance.

    Teachers/educators use this to record how well an activity went,
    student engagement, difficulties, and observations.
    """

    __tablename__ = "assessments"

    # Completion Status
    completion_status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name="completion_status"), nullable=False, index=True
    )

    # Engagement and Difficulty
    engagement_level: Mapped[EngagementLevel] = mapped_column(
        SQLEnum(EngagementLevel, name="engagement_level"), nullable=False
    )

    difficulty_rating: Mapped[DifficultyRating] = mapped_column(
        SQLEnum(DifficultyRating, name="difficulty_rating"), nullable=False
    )

    # Duration
    actual_duration_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Actual time taken vs planned duration"
    )

    # Observations
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Teacher's observations and notes")

    strengths_observed: Mapped[str | None] = mapped_column(Text, nullable=True, comment="What the student did well")

    challenges_observed: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Difficulties encountered")

    # Recommendations
    recommendations: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Suggestions for future activities"
    )

    # Structured Data
    skills_demonstrated: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Skills checklist or rubric results"
    )

    behavioral_notes: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Behavioral observations (focus, cooperation, etc.)"
    )

    # Progress Indicators
    independence_level: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Level of independence (full, partial, minimal, dependent)"
    )

    assistance_needed: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Type of assistance provided"
    )

    # Modifications Made
    modifications_made: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Any on-the-fly modifications to the activity"
    )

    # Success Metrics
    objectives_met: Mapped[Dict[str, bool] | None] = mapped_column(
        JSONB, nullable=True, comment="Which objectives were achieved"
    )

    # Foreign Keys
    activity_id: Mapped[UUID] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    student_id: Mapped[UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)

    assessed_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    activity: Mapped["Activity"] = relationship("Activity", back_populates="assessments", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", back_populates="assessments", lazy="selectin")
    assessed_by: Mapped["User"] = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Assessment(id={self.id}, activity={self.activity_id}, status={self.completion_status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AI analysis."""
        return {
            "completion_status": self.completion_status.value,
            "engagement_level": self.engagement_level.value,
            "difficulty_rating": self.difficulty_rating.value,
            "actual_duration_minutes": self.actual_duration_minutes,
            "notes": self.notes,
            "strengths_observed": self.strengths_observed,
            "challenges_observed": self.challenges_observed,
            "independence_level": self.independence_level,
        }

    @property
    def is_successful(self) -> bool:
        """Check if activity was successfully completed."""
        return self.completion_status == CompletionStatus.COMPLETED

    @property
    def needs_adjustment(self) -> bool:
        """Check if difficulty needs adjustment."""
        return self.difficulty_rating in [DifficultyRating.TOO_EASY, DifficultyRating.TOO_HARD]
