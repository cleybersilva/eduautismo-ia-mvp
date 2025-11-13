"""
Unit tests for user schemas.

Tests Pydantic validation and serialization for user-related schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.user import (
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    UserAdminUpdate,
    UserDetailResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.utils.constants import UserRole


class TestUserRegisterSchema:
    """Tests for UserRegister schema."""

    def test_user_register_success(self):
        """Test successful user registration."""
        user = UserRegister(
            email="teacher@escola.com",
            password="SecurePassword123!",
            full_name="Maria Silva Santos",
            role=UserRole.TEACHER,
            phone="+55 11 98765-4321",
            institution="Escola Municipal",
        )

        assert user.email == "teacher@escola.com"
        assert user.password == "SecurePassword123!"
        assert user.full_name == "Maria Silva Santos"
        assert user.role == UserRole.TEACHER

    def test_user_register_default_role(self):
        """Test that role defaults to TEACHER."""
        user = UserRegister(
            email="user@example.com",
            password="ValidPass123!",
            full_name="João Silva",
        )

        assert user.role == UserRole.TEACHER

    def test_user_register_invalid_email(self):
        """Test that invalid email raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="not_an_email",
                password="ValidPass123!",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_register_password_no_uppercase(self):
        """Test that password without uppercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="nouppercasepass123!",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any("maiúscula" in str(error) for error in errors)

    def test_user_register_password_no_lowercase(self):
        """Test that password without lowercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="NOLOWERCASE123!",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any("minúscula" in str(error) for error in errors)

    def test_user_register_password_no_digit(self):
        """Test that password without digit raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="NoDigitPass!",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any("número" in str(error) for error in errors)

    def test_user_register_password_no_special_char(self):
        """Test that password without special character raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="NoSpecialChar123",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any("especial" in str(error) for error in errors)

    def test_user_register_password_too_short(self):
        """Test that password too short raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="Sh0!",
                full_name="Test User",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)

    def test_user_register_full_name_too_short(self):
        """Test that full name too short raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="ValidPass123!",
                full_name="A",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("full_name",) for error in errors)

    def test_user_register_phone_invalid(self):
        """Test that invalid phone number raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="ValidPass123!",
                full_name="Test User",
                phone="123",  # Too short
            )

        errors = exc_info.value.errors()
        assert any("telefone" in str(error).lower() for error in errors)

    def test_user_register_phone_valid_formats(self):
        """Test various valid phone formats."""
        valid_phones = [
            "+55 11 98765-4321",
            "11987654321",
            "+1234567890",
            "(11) 98765-4321",
        ]

        for phone in valid_phones:
            user = UserRegister(
                email="test@example.com",
                password="ValidPass123!",
                full_name="Test User",
                phone=phone,
            )
            assert user.phone == phone


class TestUserLoginSchema:
    """Tests for UserLogin schema."""

    def test_user_login_success(self):
        """Test successful user login schema."""
        login = UserLogin(
            username="teacher@escola.com",
            password="SecurePassword123!",
        )

        assert login.username == "teacher@escola.com"
        assert login.password == "SecurePassword123!"

    def test_user_login_invalid_email(self):
        """Test that invalid username (email) raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                username="not_an_email",
                password="password",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("username",) for error in errors)


class TestUserUpdateSchema:
    """Tests for UserUpdate schema."""

    def test_user_update_success(self):
        """Test successful user update."""
        update = UserUpdate(
            full_name="Novo Nome",
            phone="+55 11 98765-4321",
            bio="Biografia atualizada",
            institution="Nova Instituição",
        )

        assert update.full_name == "Novo Nome"
        assert update.phone == "+55 11 98765-4321"
        assert update.bio == "Biografia atualizada"

    def test_user_update_partial(self):
        """Test partial user update."""
        update = UserUpdate(full_name="Apenas Nome")

        assert update.full_name == "Apenas Nome"
        assert update.phone is None
        assert update.bio is None


class TestPasswordResetSchema:
    """Tests for PasswordReset schema."""

    def test_password_reset_success(self):
        """Test password reset schema."""
        reset = PasswordReset(email="teacher@escola.com")

        assert reset.email == "teacher@escola.com"

    def test_password_reset_invalid_email(self):
        """Test that invalid email raises error."""
        with pytest.raises(ValidationError):
            PasswordReset(email="invalid_email")


class TestPasswordResetConfirmSchema:
    """Tests for PasswordResetConfirm schema."""

    def test_password_reset_confirm_success(self):
        """Test password reset confirmation."""
        confirm = PasswordResetConfirm(
            token="valid_token_here_123",
            new_password="NewSecurePass123!",
        )

        assert confirm.token == "valid_token_here_123"
        assert confirm.new_password == "NewSecurePass123!"

    def test_password_reset_confirm_token_too_short(self):
        """Test that token too short raises error."""
        with pytest.raises(ValidationError):
            PasswordResetConfirm(
                token="short",
                new_password="ValidPass123!",
            )

    def test_password_reset_confirm_password_no_uppercase(self):
        """Test that new password without uppercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="valid_token_here_123",
                new_password="nouppercasepass123!",
            )

        errors = exc_info.value.errors()
        assert any("maiúscula" in str(error) for error in errors)

    def test_password_reset_confirm_password_no_lowercase(self):
        """Test that new password without lowercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="valid_token_here_123",
                new_password="NOLOWERCASE123!",
            )

        errors = exc_info.value.errors()
        assert any("minúscula" in str(error) for error in errors)

    def test_password_reset_confirm_password_no_digit(self):
        """Test that new password without digit raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="valid_token_here_123",
                new_password="NoDigitPass!",
            )

        errors = exc_info.value.errors()
        assert any("número" in str(error) for error in errors)

    def test_password_reset_confirm_password_no_special(self):
        """Test that new password without special char raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="valid_token_here_123",
                new_password="NoSpecialChar123",
            )

        errors = exc_info.value.errors()
        assert any("especial" in str(error) for error in errors)


class TestPasswordChangeSchema:
    """Tests for PasswordChange schema."""

    def test_password_change_success(self):
        """Test password change schema."""
        change = PasswordChange(
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )

        assert change.current_password == "OldPassword123!"
        assert change.new_password == "NewPassword123!"

    def test_password_change_new_password_no_uppercase(self):
        """Test that new password without uppercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                current_password="OldPassword123!",
                new_password="nouppercasepass123!",
            )

        errors = exc_info.value.errors()
        assert any("maiúscula" in str(error) for error in errors)

    def test_password_change_new_password_no_lowercase(self):
        """Test that new password without lowercase raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                current_password="OldPassword123!",
                new_password="NOLOWERCASE123!",
            )

        errors = exc_info.value.errors()
        assert any("minúscula" in str(error) for error in errors)

    def test_password_change_new_password_no_digit(self):
        """Test that new password without digit raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                current_password="OldPassword123!",
                new_password="NoDigitPass!",
            )

        errors = exc_info.value.errors()
        assert any("número" in str(error) for error in errors)

    def test_password_change_new_password_no_special(self):
        """Test that new password without special char raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                current_password="OldPassword123!",
                new_password="NoSpecialChar123",
            )

        errors = exc_info.value.errors()
        assert any("especial" in str(error) for error in errors)


class TestUserResponseSchemas:
    """Tests for user response schemas."""

    def test_user_response_creation(self):
        """Test UserResponse schema creation."""
        from datetime import datetime
        from uuid import uuid4

        user = UserResponse(
            id=uuid4(),
            email="teacher@escola.com",
            full_name="Maria Silva",
            role=UserRole.TEACHER,
            is_active=True,
            is_verified=True,
            phone="+55 11 98765-4321",
            institution="Escola Municipal",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert user.email == "teacher@escola.com"
        assert user.full_name == "Maria Silva"
        assert user.role == UserRole.TEACHER
        assert user.is_active is True

    def test_user_detail_response_creation(self):
        """Test UserDetailResponse schema creation."""
        from datetime import datetime
        from uuid import uuid4

        user = UserDetailResponse(
            id=uuid4(),
            email="teacher@escola.com",
            full_name="Maria Silva",
            role=UserRole.TEACHER,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert user.email == "teacher@escola.com"
        assert isinstance(user, UserDetailResponse)


class TestUserAdminUpdateSchema:
    """Tests for UserAdminUpdate schema."""

    def test_user_admin_update_success(self):
        """Test admin user update."""
        update = UserAdminUpdate(
            full_name="Novo Nome",
            role=UserRole.ADMIN,
            is_active=False,
            is_verified=True,
        )

        assert update.full_name == "Novo Nome"
        assert update.role == UserRole.ADMIN
        assert update.is_active is False
        assert update.is_verified is True

    def test_user_admin_update_partial(self):
        """Test partial admin update."""
        update = UserAdminUpdate(is_active=False)

        assert update.is_active is False
        assert update.role is None
        assert update.full_name is None
