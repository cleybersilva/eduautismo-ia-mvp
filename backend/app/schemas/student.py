"""
Student Pydantic schemas for request/response validation.

This module defines the Pydantic schemas for student API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    """Base schema for Student with shared attributes."""

    # TODO: Add base fields here
    pass


class StudentCreate(BaseModel):
    """Schema for creating a new student."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add creation fields here
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add update fields here
    pass


class StudentInDB(StudentBase):
    """Schema for student as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StudentResponse(StudentInDB):
    """Schema for student API response."""

    model_config = ConfigDict(from_attributes=True)
