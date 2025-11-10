"""
Services Package - EduAutismo IA

Business logic layer for the application.
"""

from backend.app.services.student_service import StudentService
from backend.app.services.activity_service import ActivityService
from backend.app.services.assessment_service import AssessmentService
from backend.app.services.nlp_service import (
    NLPService,
    get_nlp_service,
    health_check_nlp,
)

__all__ = [
    "StudentService",
    "ActivityService",
    "AssessmentService",
    "NLPService",
    "get_nlp_service",
    "health_check_nlp",
]
