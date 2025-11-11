"""
Student Model - EduAutismo IA

Represents students with autism spectrum disorder (TEA).
"""

from datetime import date
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import Boolean, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.utils.constants import TEALevel

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.assessment import Assessment
    from app.models.user import User


class Student(BaseModel):
    """Student model with comprehensive profile information."""

    __tablename__ = "students"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    diagnosis: Mapped[str] = mapped_column(String(500), nullable=False)
    tea_level: Mapped[TEALevel | None] = mapped_column(SQLEnum(TEALevel, name="tea_level"), nullable=True)
    interests: Mapped[List[str]] = mapped_column(ARRAY(String), default=[], nullable=False)
    learning_profile: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    teacher: Mapped["User"] = relationship("User", back_populates="students", lazy="selectin")
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment", back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )
