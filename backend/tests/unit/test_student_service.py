"""
Unit tests for StudentService.

Tests the business logic for student management operations.
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate
from app.services.student_service import StudentService
from app.utils.constants import TEALevel


class TestStudentServiceCreate:
    """Tests for StudentService.create_student method."""

    @pytest.fixture
    def db_session(self):
        """Mock database session."""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def student_data(self):
        """Sample student data."""
        # Student born 10 years ago
        birth_date = date.today() - timedelta(days=365 * 10)

        return StudentCreate(
            name="João da Silva",
            date_of_birth=birth_date,
            diagnosis="TEA nível 1",
            tea_level=TEALevel.LEVEL_1,
            interests=["matemática", "robótica"],
            learning_profile={
                "visual": 8,
                "auditory": 6,
                "kinesthetic": 7,
            }
        )

    def test_create_student_success(self, db_session, student_data, teacher_id):
        """Test successful student creation."""
        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert
        assert student.name == "João da Silva"
        assert student.date_of_birth == student_data.date_of_birth
        # Age should be either 9 or 10 depending on whether birthday passed this year
        assert student.age in [9, 10]
        assert student.diagnosis == "TEA nível 1"
        assert student.tea_level == TEALevel.LEVEL_1
        assert student.interests == ["matemática", "robótica"]
        assert student.teacher_id == teacher_id

        # Verify database calls
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    def test_create_student_age_calculation_before_birthday(self, db_session, teacher_id):
        """Test age calculation when birthday hasn't occurred this year."""
        # Arrange - Student born 10 years ago, but birthday is next month
        today = date.today()
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        birth_date = date(today.year - 10, next_month, today.day)

        student_data = StudentCreate(
            name="Maria Santos",
            date_of_birth=birth_date,
            diagnosis="TEA",
            tea_level=TEALevel.LEVEL_2,
            interests=[],
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert - Should be 9 years old (birthday not yet this year)
        assert student.age == 9

    def test_create_student_age_calculation_after_birthday(self, db_session, teacher_id):
        """Test age calculation when birthday has occurred this year."""
        # Arrange - Student born 10 years ago, birthday was last month
        today = date.today()
        last_month = today.month - 1 if today.month > 1 else 12
        last_year = today.year if today.month > 1 else today.year - 1
        birth_date = date(today.year - 10, last_month, min(today.day, 28))

        student_data = StudentCreate(
            name="Pedro Costa",
            date_of_birth=birth_date,
            diagnosis="TEA",
            tea_level=TEALevel.LEVEL_1,
            interests=["jogos"],
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert - Should be 10 years old (birthday already happened)
        assert student.age == 10

    def test_create_student_minimal_data(self, db_session, teacher_id):
        """Test creating student with minimal required data."""
        # Arrange
        birth_date = date.today() - timedelta(days=365 * 8)

        student_data = StudentCreate(
            name="Ana Silva",
            date_of_birth=birth_date,
            diagnosis="Diagnóstico em avaliação",
            tea_level=None,
            interests=[],
            learning_profile=None,
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert
        assert student.name == "Ana Silva"
        assert student.tea_level is None
        assert student.interests == []
        assert student.learning_profile is None
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

    def test_create_student_with_learning_profile(self, db_session, teacher_id):
        """Test creating student with detailed learning profile."""
        # Arrange
        birth_date = date.today() - timedelta(days=365 * 12)

        learning_profile = {
            "visual": 9,
            "auditory": 5,
            "kinesthetic": 8,
            "verbal": 7,
            "logical": 8,
            "social": 4,
            "emotional": 6,
            "attention_span": 6,
            "sensory_sensitivity": 7,
            "communication_level": 6,
            "social_skills": 5,
        }

        student_data = StudentCreate(
            name="Lucas Oliveira",
            date_of_birth=birth_date,
            diagnosis="TEA nível 2",
            tea_level=TEALevel.LEVEL_2,
            interests=["música", "animais", "astronomia"],
            learning_profile=learning_profile,
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert
        assert student.learning_profile == learning_profile
        assert len(student.interests) == 3
        assert "astronomia" in student.interests

    def test_create_student_database_error_rollback(self, db_session, teacher_id, student_data):
        """Test that database errors trigger rollback."""
        # Arrange
        db_session.commit.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            StudentService.create_student(
                db=db_session,
                student_data=student_data,
                teacher_id=teacher_id
            )

        # Verify rollback was called
        db_session.rollback.assert_called_once()

    def test_create_student_logging(self, db_session, teacher_id, student_data):
        """Test that student creation is logged."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.id = uuid4()

        # Mock the Student class to return our mock
        with patch('app.services.student_service.Student', return_value=mock_student):
            with patch('app.services.student_service.logger') as mock_logger:
                # Act
                StudentService.create_student(
                    db=db_session,
                    student_data=student_data,
                    teacher_id=teacher_id
                )

                # Assert - Verify info log was called
                mock_logger.info.assert_called_once()
                log_message = mock_logger.info.call_args[0][0]
                assert "Student created" in log_message
                assert str(mock_student.id) in log_message
                assert str(teacher_id) in log_message

    def test_create_student_error_logging(self, db_session, teacher_id, student_data):
        """Test that creation errors are logged."""
        # Arrange
        error_message = "Validation failed"
        db_session.add.side_effect = ValueError(error_message)

        # Act & Assert
        with patch('app.services.student_service.logger') as mock_logger:
            with pytest.raises(ValueError):
                StudentService.create_student(
                    db=db_session,
                    student_data=student_data,
                    teacher_id=teacher_id
                )

            # Verify error log was called
            mock_logger.error.assert_called_once()
            log_message = mock_logger.error.call_args[0][0]
            assert "Error creating student" in log_message

    def test_create_student_exact_age_boundary(self, db_session, teacher_id):
        """Test age calculation on exact birthday."""
        # Arrange - Today is the student's birthday
        today = date.today()
        birth_date = date(today.year - 10, today.month, today.day)

        student_data = StudentCreate(
            name="Birthday Student",
            date_of_birth=birth_date,
            diagnosis="TEA",
            tea_level=TEALevel.LEVEL_1,
            interests=[],
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert - Should be exactly 10 years old
        assert student.age == 10

    def test_create_student_preserves_all_fields(self, db_session, teacher_id):
        """Test that all student fields are correctly preserved."""
        # Arrange
        birth_date = date(2014, 6, 15)

        student_data = StudentCreate(
            name="Complete Test Student",
            date_of_birth=birth_date,
            diagnosis="TEA nível 3 com comorbidades",
            tea_level=TEALevel.LEVEL_3,
            interests=["desenhar", "música", "natureza", "animais"],
            learning_profile={
                "visual": 10,
                "auditory": 3,
                "kinesthetic": 9,
                "verbal": 4,
                "logical": 7,
                "social": 3,
                "emotional": 5,
            }
        )

        # Act
        student = StudentService.create_student(
            db=db_session,
            student_data=student_data,
            teacher_id=teacher_id
        )

        # Assert all fields
        assert student.name == "Complete Test Student"
        assert student.date_of_birth == birth_date
        assert student.diagnosis == "TEA nível 3 com comorbidades"
        assert student.tea_level == TEALevel.LEVEL_3
        assert len(student.interests) == 4
        assert "desenhar" in student.interests
        assert "animais" in student.interests
        assert student.learning_profile["visual"] == 10
        assert student.learning_profile["auditory"] == 3
        assert student.teacher_id == teacher_id
