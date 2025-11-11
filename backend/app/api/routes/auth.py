"""
Authentication endpoints.

This module provides authentication and authorization endpoints including:
- Login/Logout
- Token refresh
- Password reset
- User registration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserLogin,
    PasswordReset,
    PasswordResetConfirm
)
from app.schemas.common import Token, TokenRefresh

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============================================================================
# Temporary Schema (TODO: Move to schemas/auth.py)
# ============================================================================

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration data."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="teacher")  # teacher, admin


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    User login with email and password.

    Returns JWT access token and refresh token.

    Args:
        form_data: OAuth2 password form (username=email, password)
        db: Database session

    Returns:
        Token: Access token, refresh token, and expiration

    Raises:
        HTTPException: 401 if credentials are invalid

    Example:
        POST /auth/login
        Body: {
            "username": "teacher@example.com",
            "password": "SecurePass123!"
        }
        Response: {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "expires_in": 1800,
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    """
    # Find user by email (OAuth2 uses 'username' field)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)  # TODO: Get from config
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=refresh_token
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user data (without password)

    Raises:
        HTTPException: 400 if email already registered

    Example:
        POST /auth/register
        Body: {
            "email": "newteacher@example.com",
            "password": "SecurePass123!",
            "full_name": "Maria Silva",
            "role": "teacher"
        }
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Token:
    """
    Refresh access token using refresh token.

    Args:
        token_data: Refresh token
        db: Database session

    Returns:
        Token: New access token

    Raises:
        HTTPException: 401 if refresh token is invalid

    Example:
        POST /auth/refresh
        Body: {
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    """
    try:
        payload = verify_token(token_data.refresh_token)
        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds())
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(oauth2_scheme)
) -> dict:
    """
    User logout.

    Currently a placeholder as JWT tokens are stateless.
    In production, implement token blacklisting or use Redis.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Logout confirmation

    Example:
        POST /auth/logout
        Headers: {"Authorization": "Bearer <token>"}
        Response: {"message": "Successfully logged out"}
    """
    # TODO: Implement token blacklisting
    # - Add token to Redis blacklist
    # - Set expiration to token's remaining lifetime

    return {
        "message": "Successfully logged out",
        "detail": "Token invalidation not yet implemented"
    }


@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def password_reset_request(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
) -> dict:
    """
    Request password reset.

    Sends password reset email to user.

    Args:
        reset_data: Email for password reset
        db: Database session

    Returns:
        dict: Confirmation message

    Example:
        POST /auth/password-reset
        Body: {"email": "user@example.com"}
        Response: {"message": "Password reset email sent"}
    """
    user = db.query(User).filter(User.email == reset_data.email).first()

    # Always return success to prevent email enumeration
    if user:
        # TODO: Implement password reset
        # 1. Generate reset token
        # 2. Save token in database or Redis
        # 3. Send email with reset link
        pass

    return {
        "message": "If the email exists, a password reset link has been sent",
        "detail": "Email sending not yet implemented"
    }


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> dict:
    """
    Confirm password reset with token.

    Args:
        reset_data: Reset token and new password
        db: Database session

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException: 400 if token is invalid

    Example:
        POST /auth/password-reset/confirm
        Body: {
            "token": "reset-token-here",
            "new_password": "NewSecurePass123!"
        }
    """
    try:
        # TODO: Implement password reset confirmation
        # 1. Verify reset token
        # 2. Get user from token
        # 3. Update password
        # 4. Invalidate token

        payload = verify_token(reset_data.token)
        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Password successfully reset"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        UserResponse: Current user data

    Raises:
        HTTPException: 401 if token is invalid

    Example:
        GET /auth/me
        Headers: {"Authorization": "Bearer <token>"}
        Response: {
            "id": 1,
            "email": "user@example.com",
            "full_name": "User Name",
            "role": "teacher",
            "is_active": true,
            "created_at": "2025-01-09T..."
        }
    """
    try:
        payload = verify_token(token)
        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserResponse.model_validate(user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
