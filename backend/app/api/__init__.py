"""
API package initialization.

This module aggregates all API routes into a single router.
"""

from fastapi import APIRouter

from app.api.routes import (
    activities,
    assessments,
    auth,
    health,
    intervention_plans,
    observations,
    professionals,
    socioemotional_indicators,
    students,
)

# Create main API router
api_router = APIRouter()

# Include all route modules
# Core/System routes
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])

# Student & Activity routes
api_router.include_router(students.router, tags=["students"])
api_router.include_router(activities.router, tags=["activities"])
api_router.include_router(assessments.router, tags=["assessments"])

# Multiprofessional System routes
api_router.include_router(professionals.router, tags=["professionals"])
api_router.include_router(observations.router, tags=["observations"])
api_router.include_router(intervention_plans.router, tags=["intervention-plans"])
api_router.include_router(socioemotional_indicators.router, tags=["socioemotional-indicators"])

__all__ = ["api_router"]
