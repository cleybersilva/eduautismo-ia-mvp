"""
Models Package - EduAutismo IA

Exports all database models for easy importing.
"""

from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity
from app.models.assessment import Assessment

__all__ = [
    "User",
    "Student",
    "Activity",
    "Assessment",
]
