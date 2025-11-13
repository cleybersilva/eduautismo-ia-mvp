"""
Unit tests for authentication schemas.

Tests Pydantic validation and serialization for auth-related schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    PasswordReset,
    PasswordResetConfirm,
    Token,
    TokenRefresh,
    UserLogin,
)


class TestTokenSchema:
    """Tests for Token schema."""

    def test_token_creation_success(self):
        """Test successful token creation with all fields."""
        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer",
            expires_in=3600,
            refresh_token="refresh_token_here"
        )

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh_token_here"

    def test_token_default_token_type(self):
        """Test that token_type defaults to 'bearer'."""
        token = Token(
            access_token="test_token",
            expires_in=3600
        )

        assert token.token_type == "bearer"

    def test_token_without_refresh_token(self):
        """Test token creation without refresh_token."""
        token = Token(
            access_token="test_token",
            expires_in=3600
        )

        assert token.refresh_token is None

    def test_token_serialization(self):
        """Test token serialization to dict."""
        token = Token(
            access_token="test_token",
            token_type="bearer",
            expires_in=7200,
            refresh_token="refresh_here"
        )

        token_dict = token.model_dump()

        assert token_dict["access_token"] == "test_token"
        assert token_dict["token_type"] == "bearer"
        assert token_dict["expires_in"] == 7200
        assert token_dict["refresh_token"] == "refresh_here"


class TestUserLoginSchema:
    """Tests for UserLogin schema."""

    def test_user_login_success(self):
        """Test successful login schema creation."""
        login = UserLogin(
            email="teacher@escola.com",
            password="SecurePass123"
        )

        assert login.email == "teacher@escola.com"
        assert login.password == "SecurePass123"

    def test_user_login_invalid_email(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                email="not_an_email",
                password="SecurePass123"
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_login_password_too_short(self):
        """Test that password less than 8 characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                email="teacher@escola.com",
                password="short"
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("password",) 
            for error in errors
        )


class TestPasswordResetSchema:
    """Tests for PasswordReset schema."""

    def test_password_reset_success(self):
        """Test PasswordReset creation."""
        reset = PasswordReset(email="user@example.com")

        assert reset.email == "user@example.com"

    def test_password_reset_invalid_email(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordReset(email="invalid_email")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)


class TestPasswordResetConfirmSchema:
    """Tests for PasswordResetConfirm schema."""

    def test_password_reset_confirm_success(self):
        """Test PasswordResetConfirm creation."""
        confirm = PasswordResetConfirm(
            token="reset_token_here",
            new_password="NewSecurePass123"
        )

        assert confirm.token == "reset_token_here"
        assert confirm.new_password == "NewSecurePass123"

    def test_password_reset_confirm_password_too_short(self):
        """Test that new_password less than 8 characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="valid_token",
                new_password="short"
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("new_password",)
            for error in errors
        )
