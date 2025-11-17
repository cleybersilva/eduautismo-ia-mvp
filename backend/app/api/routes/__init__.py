"""
API Routes Package - EduAutismo IA

Exports all route modules for easy importing.
"""

from app.api.routes.activities import router as activities_router
from app.api.routes.assessments import router as assessments_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.intervention_plans import router as intervention_plans_router
from app.api.routes.observations import router as observations_router
from app.api.routes.professionals import router as professionals_router
from app.api.routes.socioemotional_indicators import router as indicators_router
from app.api.routes.students import router as students_router

__all__ = [
    "activities_router",
    "assessments_router",
    "auth_router",
    "health_router",
    "students_router",
    "professionals_router",
    "observations_router",
    "intervention_plans_router",
    "indicators_router",
]
