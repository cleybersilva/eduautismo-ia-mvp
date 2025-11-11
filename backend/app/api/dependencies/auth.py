"""
FastAPI dependencies for authentication, database, and other shared functionality.

This module provides dependency injection functions for FastAPI routes.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
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
