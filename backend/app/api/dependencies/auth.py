"""
FastAPI dependencies for authentication, database, and other shared functionality.

This module provides dependency injection functions for FastAPI routes.
"""

from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_token

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current authenticated user.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User payload dict from JWT token

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # Verify token and get payload
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token has required fields
    if "sub" not in payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_professional_id(x_professional_id: Optional[str] = Header(None, alias="X-Professional-ID")) -> Optional[UUID]:
    """
    Extract Professional ID from X-Professional-ID header.

    Args:
        x_professional_id: Professional ID from custom header

    Returns:
        Professional UUID if header is present, None otherwise

    Raises:
        HTTPException: If header value is not a valid UUID
    """
    if x_professional_id is None:
        return None

    try:
        return UUID(x_professional_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Professional ID format in X-Professional-ID header",
        )
