"""
API package initialization.

This module aggregates all API routes into a single router.
"""

from fastapi import APIRouter

from app.api.routes import health, auth, students, activities, assessments

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(students.router, tags=["students"])
api_router.include_router(activities.router, tags=["activities"])
api_router.include_router(assessments.router, tags=["assessments"])

__all__ = ["api_router"]
