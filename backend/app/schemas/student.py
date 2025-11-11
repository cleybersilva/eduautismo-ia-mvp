"""
Student Schemas - EduAutismo IA

Request and response schemas for student-related endpoints.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.schemas.common import BaseResponseSchema, BaseSchema
from app.utils.constants import (MAX_INTERESTS_COUNT, MAX_STUDENT_AGE,
                                 MIN_STUDENT_AGE, TEALevel)
from pydantic import Field, field_validator


class StudentCreate(BaseSchema):
    """Schema for creating a new student."""

    name: str = Field(..., min_length=2, max_length=255, description="Student's full name")
    date_of_birth: date = Field(..., description="Student's date of birth")
    diagnosis: str = Field(..., min_length=3, max_length=500, description="Diagnosis description")
    tea_level: Optional[TEALevel] = Field(default=None, description="TEA support level")
    interests: List[str] = Field(default=[], max_length=MAX_INTERESTS_COUNT, description="Interests")
    learning_profile: Optional[Dict[str, Any]] = Field(default=None, description="Learning profile")

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        """Validate date of birth."""
        from datetime import date as date_type

        today = date_type.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < MIN_STUDENT_AGE:
            raise ValueError(f"Idade deve ser pelo menos {MIN_STUDENT_AGE} anos")
        if age > MAX_STUDENT_AGE:
            raise ValueError(f"Idade deve ser no máximo {MAX_STUDENT_AGE} anos")
        if value > today:
            raise ValueError("Data de nascimento não pode ser no futuro")

        return value


class StudentUpdate(BaseSchema):
    """Schema for updating student information."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    date_of_birth: Optional[date] = Field(default=None)
    diagnosis: Optional[str] = Field(default=None, min_length=3, max_length=500)
    tea_level: Optional[TEALevel] = Field(default=None)
    interests: Optional[List[str]] = Field(default=None)
    learning_profile: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class StudentResponse(BaseResponseSchema):
    """Schema for student response."""

    name: str
    date_of_birth: date
    age: int
    diagnosis: str
    tea_level: Optional[TEALevel] = None
    interests: List[str] = []
    learning_profile: Optional[Dict[str, Any]] = None
    is_active: bool
    teacher_id: UUID


class StudentListResponse(BaseResponseSchema):
    """Schema for student in list."""

    name: str
    age: int
    diagnosis: str
    tea_level: Optional[TEALevel] = None
    is_active: bool
