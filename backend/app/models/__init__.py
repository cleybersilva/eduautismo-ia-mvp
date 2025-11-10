"""
Models Package - EduAutismo IA

Exports all database models for easy importing.
"""

from backend.app.models.user import User
from backend.app.models.student import Student
from backend.app.models.activity import Activity
from backend.app.models.assessment import Assessment

__all__ = [
    "User",
    "Student",
    "Activity",
    "Assessment",
]
