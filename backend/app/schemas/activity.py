"""
Activity Pydantic schemas for request/response validation.

This module defines the Pydantic schemas for activity API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ActivityBase(BaseModel):
    """Base schema for Activity with shared attributes."""

    # TODO: Add base fields here
    pass


class ActivityCreate(BaseModel):
    """Schema for creating a new activity."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add creation fields here
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an existing activity."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add update fields here
    pass


class ActivityInDB(ActivityBase):
    """Schema for activity as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ActivityResponse(ActivityInDB):
    """Schema for activity API response."""

    model_config = ConfigDict(from_attributes=True)
