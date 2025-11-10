"""
User Model - EduAutismo IA

Represents system users (teachers, admins, parents, therapists).
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import BaseModel
from backend.app.utils.constants import UserRole

if TYPE_CHECKING:
    from backend.app.models.student import Student


class User(BaseModel):
    """
    User model for authentication and authorization.

    Represents teachers, admins, parents, and therapists who use the system.
    """

    __tablename__ = "users"

    # Basic Information
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Role and Status
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", create_type=True),
        default=UserRole.TEACHER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Optional Profile Information
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Institution/Organization
    institution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Last Login Tracking
    last_login: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Password Reset Token
    reset_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reset_token_expires: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Email Verification Token
    verification_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="teacher",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_teacher(self) -> bool:
        """Check if user is teacher."""
        return self.role == UserRole.TEACHER

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
