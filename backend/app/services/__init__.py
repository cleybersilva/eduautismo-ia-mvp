"""
Services Package - EduAutismo IA

Business logic layer for the application.
"""

from app.services.activity_service import ActivityService
from app.services.assessment_service import AssessmentService
from app.services.nlp_service import NLPService, get_nlp_service, health_check_nlp
from app.services.student_service import StudentService

__all__ = [
    "StudentService",
    "ActivityService",
    "AssessmentService",
    "NLPService",
    "get_nlp_service",
    "health_check_nlp",
]
