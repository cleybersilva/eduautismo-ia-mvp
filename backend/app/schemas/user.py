"""
User Schemas - EduAutismo IA

Request and response schemas for user-related endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.schemas.common import BaseResponseSchema, BaseSchema
from app.utils.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH, UserRole
from pydantic import EmailStr, Field, field_validator

# ============================================================================
# Request Schemas
# ============================================================================


class UserRegister(BaseSchema):
    """Schema for user registration."""

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["teacher@escola.com"],
    )

    password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="User password (will be hashed)",
        examples=["SecurePassword123!"],
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full name",
        examples=["Maria Silva Santos"],
    )

    role: UserRole = Field(
        default=UserRole.TEACHER,
        description="User role in the system",
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Phone number",
        examples=["+55 11 98765-4321"],
    )

    institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Institution or organization",
        examples=["Escola Municipal João Paulo"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Validate password strength.

        Args:
            value: Password to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        errors = []

        if not any(c.isupper() for c in value):
            errors.append("deve conter pelo menos uma letra maiúscula")

        if not any(c.islower() for c in value):
            errors.append("deve conter pelo menos uma letra minúscula")

        if not any(c.isdigit() for c in value):
            errors.append("deve conter pelo menos um número")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value):
            errors.append("deve conter pelo menos um caractere especial")

        if errors:
            raise ValueError(f"Senha {', '.join(errors)}")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if value:
            # Remove non-digit characters for validation
            digits = "".join(filter(str.isdigit, value))
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError("Número de telefone inválido")
        return value


class UserLogin(BaseSchema):
    """Schema for user login (OAuth2PasswordRequestForm compatible)."""

    username: EmailStr = Field(
        ...,
        description="User email (username for OAuth2)",
        examples=["teacher@escola.com"],
    )

    password: str = Field(
        ...,
        description="User password",
        examples=["SecurePassword123!"],
    )


class UserUpdate(BaseSchema):
    """Schema for updating user profile."""

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="User's full name",
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Phone number",
    )

    avatar_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Avatar image URL",
    )

    bio: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="User biography",
    )

    institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Institution or organization",
    )


class PasswordReset(BaseSchema):
    """Schema for password reset request."""

    email: EmailStr = Field(
        ...,
        description="Email address to send reset link",
        examples=["teacher@escola.com"],
    )


class PasswordResetConfirm(BaseSchema):
    """Schema for confirming password reset."""

    token: str = Field(
        ...,
        min_length=10,
        description="Password reset token from email",
    )

    new_password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="New password",
        examples=["NewSecurePassword123!"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate new password strength (same as registration)."""
        errors = []

        if not any(c.isupper() for c in value):
            errors.append("deve conter pelo menos uma letra maiúscula")

        if not any(c.islower() for c in value):
            errors.append("deve conter pelo menos uma letra minúscula")

        if not any(c.isdigit() for c in value):
            errors.append("deve conter pelo menos um número")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value):
            errors.append("deve conter pelo menos um caractere especial")

        if errors:
            raise ValueError(f"Senha {', '.join(errors)}")

        return value


class PasswordChange(BaseSchema):
    """Schema for changing password (authenticated user)."""

    current_password: str = Field(
        ...,
        description="Current password for verification",
    )

    new_password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="New password",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate new password strength."""
        errors = []

        if not any(c.isupper() for c in value):
            errors.append("deve conter pelo menos uma letra maiúscula")

        if not any(c.islower() for c in value):
            errors.append("deve conter pelo menos uma letra minúscula")

        if not any(c.isdigit() for c in value):
            errors.append("deve conter pelo menos um número")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value):
            errors.append("deve conter pelo menos um caractere especial")

        if errors:
            raise ValueError(f"Senha {', '.join(errors)}")

        return value


# ============================================================================
# Response Schemas
# ============================================================================


class UserResponse(BaseResponseSchema):
    """Schema for user response (public information)."""

    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verified status")
    phone: Optional[str] = Field(None, description="Phone number")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    bio: Optional[str] = Field(None, description="Biography")
    institution: Optional[str] = Field(None, description="Institution")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class UserDetailResponse(UserResponse):
    """Schema for detailed user response (includes more information)."""

    # Inherits all fields from UserResponse
    # Can add admin-only fields here if needed

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "teacher@escola.com",
                "full_name": "Maria Silva Santos",
                "role": "teacher",
                "is_active": True,
                "is_verified": True,
                "phone": "+55 11 98765-4321",
                "institution": "Escola Municipal João Paulo",
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-01-10T15:30:00Z",
                "last_login": "2025-01-10T15:30:00Z",
            }
        }


class UserListResponse(UserResponse):
    """Schema for user in list (minimal information)."""

    # Only includes essential fields for listings
    model_config = {"exclude": {"bio", "phone", "last_login"}}


# ============================================================================
# Admin Schemas
# ============================================================================


class UserAdminUpdate(UserUpdate):
    """Schema for admin user updates (includes role and status)."""

    role: Optional[UserRole] = Field(
        default=None,
        description="Update user role (admin only)",
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Activate/deactivate account (admin only)",
    )

    is_verified: Optional[bool] = Field(
        default=None,
        description="Verify/unverify email (admin only)",
    )
