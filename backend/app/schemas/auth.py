"""
Authentication Schemas - EduAutismo IA

This module defines Pydantic schemas for authentication endpoints.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Access token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token (optional)")


class TokenRefresh(BaseModel):
    """Token refresh request."""

    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


class UserLogin(BaseModel):
    """User login credentials."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class PasswordReset(BaseModel):
    """Password reset request."""

    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
