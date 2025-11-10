"""
Activity model for EduAutismo IA.

This module defines the database model for activity.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base


class Activity(Base):
    """
    Activity database model.

    Attributes:
        id: Primary key
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "activitys"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # TODO: Add model-specific fields here

    def __repr__(self) -> str:
        return f"<Activity(id={self.id})>"
