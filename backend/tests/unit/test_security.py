"""
Unit tests for security utilities.

Tests password hashing, JWT token creation and verification.
"""

from datetime import timedelta

from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_creates_hash(self):
        """Test that get_password_hash creates a hash."""
        password = "MySecurePassword123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long

    def test_get_password_hash_different_for_same_password(self):
        """Test that same password generates different hashes (salt)."""
        password = "SamePassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Different salts

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "CorrectPassword123"
        hashed = get_password_hash(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        correct_password = "CorrectPassword123"
        incorrect_password = "WrongPassword456"
        hashed = get_password_hash(correct_password)

        result = verify_password(incorrect_password, hashed)

        assert result is False

    def test_verify_password_empty_password(self):
        """Test verify_password with empty password."""
        hashed = get_password_hash("SomePassword")

        result = verify_password("", hashed)

        assert result is False

    def test_password_hash_workflow(self):
        """Test complete password hash and verify workflow."""
        # User registers with password
        original_password = "UserPassword123!"
        stored_hash = get_password_hash(original_password)

        # User logs in with correct password
        assert verify_password(original_password, stored_hash) is True

        # Attacker tries wrong password
        assert verify_password("WrongPassword", stored_hash) is False


class TestAccessToken:
    """Tests for access token creation and verification."""

    def test_create_access_token_with_default_expiry(self):
        """Test creating access token with default expiration."""
        data = {"sub": "user@example.com", "role": "teacher"}

        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_access_token_with_custom_expiry(self):
        """Test creating access token with custom expiration."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=15)

        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        # Verify token contains expiry
        from app.core.config import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_create_access_token_includes_data(self):
        """Test that access token includes the provided data."""
        data = {"sub": "teacher@escola.com", "user_id": "123", "role": "teacher"}

        token = create_access_token(data)

        # Decode and verify
        from app.core.config import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == "teacher@escola.com"
        assert payload["user_id"] == "123"
        assert payload["role"] == "teacher"

    def test_create_access_token_adds_exp_claim(self):
        """Test that access token includes exp claim."""
        data = {"sub": "user@example.com"}

        token = create_access_token(data)

        from app.core.config import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))


class TestRefreshToken:
    """Tests for refresh token creation."""

    def test_create_refresh_token_with_default_expiry(self):
        """Test creating refresh token with default expiration."""
        data = {"sub": "user@example.com"}

        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_refresh_token_with_custom_expiry(self):
        """Test creating refresh token with custom expiration."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(days=7)

        token = create_refresh_token(data, expires_delta=expires_delta)

        assert token is not None

    def test_create_refresh_token_includes_type(self):
        """Test that refresh token includes type field."""
        data = {"sub": "user@example.com"}

        token = create_refresh_token(data)

        from app.core.config import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload.get("type") == "refresh"

    def test_create_refresh_token_includes_data(self):
        """Test that refresh token includes the provided data."""
        data = {"sub": "user@example.com", "user_id": "456"}

        token = create_refresh_token(data)

        from app.core.config import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == "user@example.com"
        assert payload["user_id"] == "456"


class TestTokenVerification:
    """Tests for token verification functions."""

    def test_verify_token_valid_token(self):
        """Test verify_token with a valid token."""
        data = {"sub": "user@example.com", "role": "teacher"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "user@example.com"
        assert payload["role"] == "teacher"

    def test_verify_token_invalid_token(self):
        """Test verify_token with an invalid token."""
        invalid_token = "invalid.jwt.token"

        payload = verify_token(invalid_token)

        assert payload is None

    def test_verify_token_tampered_token(self):
        """Test verify_token with a tampered token."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"

        payload = verify_token(tampered_token)

        assert payload is None

    def test_verify_token_expired_token(self):
        """Test verify_token with an expired token."""
        data = {"sub": "user@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = verify_token(token)

        assert payload is None

    def test_decode_access_token_valid_token(self):
        """Test decode_access_token with valid token."""
        email = "teacher@escola.com"
        data = {"sub": email}
        token = create_access_token(data)

        subject = decode_access_token(token)

        assert subject == email

    def test_decode_access_token_invalid_token(self):
        """Test decode_access_token with invalid token."""
        invalid_token = "invalid.token.here"

        subject = decode_access_token(invalid_token)

        assert subject is None

    def test_decode_access_token_token_without_sub(self):
        """Test decode_access_token with token missing sub claim."""
        data = {"user_id": "123", "role": "teacher"}  # No 'sub'
        token = create_access_token(data)

        subject = decode_access_token(token)

        assert subject is None


class TestSecurityIntegration:
    """Integration tests for security utilities."""

    def test_complete_auth_flow(self):
        """Test complete authentication flow."""
        # 1. User registers - password is hashed
        password = "MyPassword123!"
        password_hash = get_password_hash(password)

        # 2. User logs in - verify password
        assert verify_password(password, password_hash) is True

        # 3. System creates access token
        access_token = create_access_token({"sub": "user@example.com", "role": "teacher"})

        # 4. System creates refresh token
        refresh_token = create_refresh_token({"sub": "user@example.com"})

        # 5. Verify access token
        access_payload = verify_token(access_token)
        assert access_payload is not None
        assert access_payload["sub"] == "user@example.com"

        # 6. Verify refresh token
        refresh_payload = verify_token(refresh_token)
        assert refresh_payload is not None
        assert refresh_payload.get("type") == "refresh"

        # 7. Decode access token to get user
        user_email = decode_access_token(access_token)
        assert user_email == "user@example.com"

    def test_token_refresh_flow(self):
        """Test token refresh flow."""
        user_email = "teacher@escola.com"

        # 1. User has valid refresh token
        refresh_data = {"sub": user_email}
        refresh_token = create_refresh_token(refresh_data)

        # 2. Verify refresh token
        payload = verify_token(refresh_token)
        assert payload is not None
        assert payload.get("type") == "refresh"

        # 3. Issue new access token
        new_access_token = create_access_token({"sub": payload["sub"], "role": "teacher"})

        # 4. Verify new access token works
        new_payload = verify_token(new_access_token)
        assert new_payload is not None
        assert new_payload["sub"] == user_email
