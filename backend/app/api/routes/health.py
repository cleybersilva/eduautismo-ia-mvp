"""
Health check endpoints.

This module provides health check endpoints for monitoring service status,
database connectivity, and external dependencies.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from datetime import datetime
import asyncio

from backend.app.core.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns a simple status indicating the service is running.
    Used by Docker health checks and load balancers.

    Returns:
        dict: Health status

    Example:
        GET /health
        Response: {"status": "healthy"}
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with dependency checks.

    Checks the status of:
    - API service
    - Database connection
    - External services (optional)

    Args:
        db: Database session dependency

    Returns:
        dict: Detailed health status of all components

    Example:
        GET /health/detailed
        Response: {
            "status": "healthy",
            "timestamp": "2025-01-09T...",
            "components": {
                "api": {"status": "up"},
                "database": {"status": "up", "latency_ms": 5},
                ...
            }
        }
    """
    components = {}
    overall_status = "healthy"

    # Check API
    components["api"] = {
        "status": "up",
        "version": "1.0.0"
    }

    # Check Database
    try:
        start_time = asyncio.get_event_loop().time()
        db.execute(text("SELECT 1"))
        latency = (asyncio.get_event_loop().time() - start_time) * 1000

        components["database"] = {
            "status": "up",
            "type": "postgresql",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        components["database"] = {
            "status": "down",
            "error": str(e)
        }
        overall_status = "degraded"

    # TODO: Check Redis
    components["redis"] = {
        "status": "not_configured",
        "message": "Redis health check not implemented yet"
    }

    # TODO: Check MongoDB
    components["mongodb"] = {
        "status": "not_configured",
        "message": "MongoDB health check not implemented yet"
    }

    # TODO: Check OpenAI API
    components["openai"] = {
        "status": "not_configured",
        "message": "OpenAI health check not implemented yet"
    }

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Readiness check endpoint.

    Checks if the service is ready to accept traffic.
    Used by Kubernetes readiness probes.

    Args:
        db: Database session dependency

    Returns:
        dict: Readiness status

    Raises:
        HTTPException: 503 if service is not ready

    Example:
        GET /health/ready
        Response: {"status": "ready"}
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check endpoint.

    Checks if the service is alive (process is running).
    Used by Kubernetes liveness probes.

    Returns:
        dict: Liveness status

    Example:
        GET /health/live
        Response: {"status": "alive"}
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/startup", status_code=status.HTTP_200_OK)
async def startup_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Startup check endpoint.

    Checks if the service has completed startup.
    Used by Kubernetes startup probes.

    Args:
        db: Database session dependency

    Returns:
        dict: Startup status

    Raises:
        HTTPException: 503 if service has not completed startup

    Example:
        GET /health/startup
        Response: {"status": "started"}
    """
    try:
        # Check critical dependencies are available
        db.execute(text("SELECT 1"))

        # TODO: Add more startup checks
        # - Check migrations are up to date
        # - Check required environment variables
        # - Check external services connectivity

        return {
            "status": "started",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not started: {str(e)}"
        )
