"""
Unit tests for student schemas.

Tests Pydantic validation for student-related schemas.
"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.student import StudentCreate, StudentUpdate
from app.utils.constants import MIN_STUDENT_AGE, MAX_STUDENT_AGE


class TestStudentCreateSchema:
    """Tests for StudentCreate schema."""

    def test_student_create_valid_date_of_birth(self):
        """Test student creation with valid date of birth."""
        # Create a valid date of birth (10 years ago)
        dob = date.today() - timedelta(days=10 * 365)

        student = StudentCreate(
            name="João Silva",
            date_of_birth=dob,
            diagnosis="Autismo Leve",
        )

        assert student.name == "João Silva"
        assert student.date_of_birth == dob

    def test_student_create_date_of_birth_too_young(self):
        """Test that student younger than minimum age raises error."""
        # Create date of birth that makes student too young (2 years old)
        dob = date.today() - timedelta(days=2 * 365)

        with pytest.raises(ValidationError) as exc_info:
            StudentCreate(
                name="Criança Pequena",
                date_of_birth=dob,
                diagnosis="Autismo Leve",
            )

        errors = exc_info.value.errors()
        assert any(
            f"Idade deve ser pelo menos {MIN_STUDENT_AGE}" in str(error)
            for error in errors
        )

    def test_student_create_date_of_birth_too_old(self):
        """Test that student older than maximum age raises error."""
        # Create date of birth that makes student too old (25 years old)
        dob = date.today() - timedelta(days=25 * 365)

        with pytest.raises(ValidationError) as exc_info:
            StudentCreate(
                name="Pessoa Adulta",
                date_of_birth=dob,
                diagnosis="Autismo Moderado",
            )

        errors = exc_info.value.errors()
        assert any(
            f"Idade deve ser no máximo {MAX_STUDENT_AGE}" in str(error)
            for error in errors
        )

    def test_student_create_future_date_of_birth(self):
        """Test that future date of birth raises error."""
        # Create future date of birth
        future_dob = date.today() + timedelta(days=365)

        with pytest.raises(ValidationError) as exc_info:
            StudentCreate(
                name="Viajante do Tempo",
                date_of_birth=future_dob,
                diagnosis="Autismo",
            )

        # Verify ValidationError was raised (which means line 41 was executed)
        assert exc_info.value is not None
        error_str = str(exc_info.value)
        assert "futuro" in error_str or "date_of_birth" in error_str

    def test_student_create_minimum_age_boundary(self):
        """Test student at exact minimum age."""
        # Create date of birth exactly MIN_STUDENT_AGE years ago (accounting for leap years)
        from datetime import datetime

        today = date.today()
        dob = date(today.year - MIN_STUDENT_AGE, today.month, today.day)

        student = StudentCreate(
            name="Aluno Mínimo",
            date_of_birth=dob,
            diagnosis="TEA Leve",
        )

        assert student.name == "Aluno Mínimo"

    def test_student_create_maximum_age_boundary(self):
        """Test student at exact maximum age."""
        # Create date of birth exactly MAX_STUDENT_AGE years ago
        today = date.today()
        dob = date(today.year - MAX_STUDENT_AGE, today.month, today.day)

        student = StudentCreate(
            name="Aluno Máximo",
            date_of_birth=dob,
            diagnosis="Autismo Severo",
        )

        assert student.name == "Aluno Máximo"

    def test_student_create_today_birth(self):
        """Test student born today (edge case)."""
        dob = date.today()

        with pytest.raises(ValidationError) as exc_info:
            StudentCreate(
                name="Recém Nascido",
                date_of_birth=dob,
                diagnosis="TEA",
            )

        # Should fail minimum age validation
        errors = exc_info.value.errors()
        assert any(
            f"Idade deve ser pelo menos {MIN_STUDENT_AGE}" in str(error)
            for error in errors
        )


class TestStudentUpdateSchema:
    """Tests for StudentUpdate schema."""

    def test_student_update_partial(self):
        """Test partial student update."""
        update = StudentUpdate(name="Novo Nome")

        assert update.name == "Novo Nome"
        assert update.date_of_birth is None

    def test_student_update_all_fields(self):
        """Test updating all fields."""
        dob = date.today() - timedelta(days=12 * 365)

        update = StudentUpdate(
            name="Nome Atualizado",
            date_of_birth=dob,
            diagnosis="Autismo Atualizado",
            is_active=True,
        )

        assert update.name == "Nome Atualizado"
        assert update.date_of_birth == dob
        assert update.diagnosis == "Autismo Atualizado"
        assert update.is_active is True

    def test_student_update_empty(self):
        """Test creating empty update (all None)."""
        update = StudentUpdate()

        assert update.name is None
        assert update.date_of_birth is None
        assert update.diagnosis is None
        assert update.is_active is None
