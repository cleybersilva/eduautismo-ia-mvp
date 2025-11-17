"""
Models Package - EduAutismo IA

Exports all database models for easy importing.
"""

from app.models.activity import Activity
from app.models.assessment import Assessment
from app.models.intervention_plan import InterventionPlan
from app.models.observation import ProfessionalObservation
from app.models.professional import Professional
from app.models.socioemotional_indicator import SocialEmotionalIndicator
from app.models.student import Student
from app.models.user import User

__all__ = [
    "User",
    "Student",
    "Activity",
    "Assessment",
    "Professional",
    "ProfessionalObservation",
    "InterventionPlan",
    "SocialEmotionalIndicator",
]
