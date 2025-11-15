"""
Unit tests for AssessmentService.

Tests the business logic for assessment management operations.
"""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ActivityNotFoundError,
    AssessmentNotFoundError,
    PermissionDeniedError,
    StudentNotFoundError,
)
from app.models.activity import Activity
from app.models.assessment import Assessment
from app.models.student import Student
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate
from app.services.assessment_service import AssessmentService
from app.utils.constants import CompletionStatus, DifficultyRating, EngagementLevel


class TestAssessmentServiceCreate:
    """Tests for AssessmentService.create_assessment method."""

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
    def student_id(self):
        """Sample student ID."""
        return uuid4()

    @pytest.fixture
    def activity_id(self):
        """Sample activity ID."""
        return uuid4()

    @pytest.fixture
    def assessment_data(self, activity_id, student_id):
        """Sample assessment data."""
        return AssessmentCreate(
            activity_id=activity_id,
            student_id=student_id,
            completion_status=CompletionStatus.COMPLETED,
            engagement_level=EngagementLevel.HIGH,
            difficulty_rating=DifficultyRating.APPROPRIATE,
            actual_duration_minutes=45,
            notes="Aluno demonstrou boa compreensão",
        )

    @pytest.fixture
    def mock_activity(self, activity_id):
        """Mock activity."""
        activity = Mock(spec=Activity)
        activity.id = activity_id
        return activity

    @pytest.fixture
    def mock_student(self, student_id, teacher_id):
        """Mock student."""
        student = Mock(spec=Student)
        student.id = student_id
        student.teacher_id = teacher_id
        return student

    def test_create_assessment_success(self, db_session, assessment_data, teacher_id, mock_activity, mock_student):
        """Test successful assessment creation."""

        # Arrange
        def query_side_effect(model):
            mock_query = Mock()
            if model == Activity:
                mock_query.filter().first.return_value = mock_activity
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act
        assessment = AssessmentService.create_assessment(
            db=db_session, assessment_data=assessment_data, teacher_id=teacher_id
        )

        # Assert
        assert assessment.activity_id == assessment_data.activity_id
        assert assessment.student_id == assessment_data.student_id
        assert assessment.completion_status == CompletionStatus.COMPLETED
        assert assessment.engagement_level == EngagementLevel.HIGH
        assert assessment.difficulty_rating == DifficultyRating.APPROPRIATE
        assert assessment.assessed_by_id == teacher_id

        # Verify database calls
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    def test_create_assessment_activity_not_found(self, db_session, assessment_data, teacher_id):
        """Test that activity not found raises error."""
        # Arrange
        mock_query = Mock()
        mock_query.filter().first.return_value = None
        db_session.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ActivityNotFoundError):
            AssessmentService.create_assessment(db=db_session, assessment_data=assessment_data, teacher_id=teacher_id)

    def test_create_assessment_student_not_found(self, db_session, assessment_data, teacher_id, mock_activity):
        """Test that student not found raises error."""

        # Arrange
        def query_side_effect(model):
            mock_query = Mock()
            if model == Activity:
                mock_query.filter().first.return_value = mock_activity
            elif model == Student:
                mock_query.filter().first.return_value = None
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act & Assert
        with pytest.raises(StudentNotFoundError):
            AssessmentService.create_assessment(db=db_session, assessment_data=assessment_data, teacher_id=teacher_id)

    def test_create_assessment_permission_denied(self, db_session, assessment_data, mock_activity, mock_student):
        """Test that permission is denied for wrong teacher."""
        # Arrange
        wrong_teacher_id = uuid4()
        mock_student.teacher_id = uuid4()  # Different teacher

        def query_side_effect(model):
            mock_query = Mock()
            if model == Activity:
                mock_query.filter().first.return_value = mock_activity
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act & Assert
        with pytest.raises(PermissionDeniedError) as exc_info:
            AssessmentService.create_assessment(
                db=db_session, assessment_data=assessment_data, teacher_id=wrong_teacher_id
            )

        assert "não tem permissão" in str(exc_info.value)

    def test_create_assessment_logging(self, db_session, assessment_data, teacher_id, mock_activity, mock_student):
        """Test that assessment creation is logged."""
        # Arrange
        mock_assessment = Mock(spec=Assessment)
        mock_assessment.id = uuid4()

        def query_side_effect(model):
            mock_query = Mock()
            if model == Activity:
                mock_query.filter().first.return_value = mock_activity
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        with patch("app.services.assessment_service.Assessment", return_value=mock_assessment):
            with patch("app.services.assessment_service.logger") as mock_logger:
                # Act
                AssessmentService.create_assessment(
                    db=db_session, assessment_data=assessment_data, teacher_id=teacher_id
                )

                # Assert - Verify info log was called
                mock_logger.info.assert_called_once()
                log_message = mock_logger.info.call_args[0][0]
                assert "Assessment created" in log_message
                assert str(mock_assessment.id) in log_message


class TestAssessmentServiceGet:
    """Tests for AssessmentService.get_assessment method."""

    @pytest.fixture
    def db_session(self):
        """Mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def assessment_id(self):
        """Sample assessment ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def mock_assessment(self, assessment_id):
        """Mock assessment."""
        assessment = Mock(spec=Assessment)
        assessment.id = assessment_id
        assessment.student_id = uuid4()
        return assessment

    def test_get_assessment_success_without_teacher_id(self, db_session, assessment_id, mock_assessment):
        """Test successful get without teacher_id check."""
        # Arrange
        mock_query = Mock()
        mock_query.filter().first.return_value = mock_assessment
        db_session.query.return_value = mock_query

        # Act
        result = AssessmentService.get_assessment(db=db_session, assessment_id=assessment_id)

        # Assert
        assert result == mock_assessment

    def test_get_assessment_success_with_teacher_id(self, db_session, assessment_id, teacher_id, mock_assessment):
        """Test successful get with teacher_id permission check."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act
        result = AssessmentService.get_assessment(db=db_session, assessment_id=assessment_id, teacher_id=teacher_id)

        # Assert
        assert result == mock_assessment

    def test_get_assessment_not_found(self, db_session, assessment_id):
        """Test that assessment not found raises error."""
        # Arrange
        mock_query = Mock()
        mock_query.filter().first.return_value = None
        db_session.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(AssessmentNotFoundError):
            AssessmentService.get_assessment(db=db_session, assessment_id=assessment_id)

    def test_get_assessment_permission_denied(self, db_session, assessment_id, mock_assessment):
        """Test permission denied for wrong teacher."""
        # Arrange
        wrong_teacher_id = uuid4()
        correct_teacher_id = uuid4()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = correct_teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act & Assert
        with pytest.raises(PermissionDeniedError):
            AssessmentService.get_assessment(db=db_session, assessment_id=assessment_id, teacher_id=wrong_teacher_id)


class TestAssessmentServiceList:
    """Tests for AssessmentService.list_assessments method."""

    @pytest.fixture
    def db_session(self):
        """Mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_assessments(self):
        """Mock list of assessments."""
        assessments = []
        for i in range(5):
            assessment = Mock(spec=Assessment)
            assessment.id = uuid4()
            assessment.student_id = uuid4()
            assessment.activity_id = uuid4()
            assessments.append(assessment)
        return assessments

    def test_list_assessments_no_filters(self, db_session, mock_assessments):
        """Test listing assessments without filters."""
        # Arrange
        mock_query = Mock()
        mock_query.count.return_value = len(mock_assessments)
        mock_query.order_by().offset().limit().all.return_value = mock_assessments
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session)

        # Assert
        assert len(assessments) == 5
        assert total == 5

    def test_list_assessments_filter_by_student(self, db_session, mock_assessments):
        """Test filtering assessments by student_id."""
        # Arrange
        student_id = uuid4()
        mock_query = Mock()
        mock_query.filter().count.return_value = 3
        mock_query.filter().order_by().offset().limit().all.return_value = mock_assessments[:3]
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session, student_id=student_id)

        # Assert
        assert len(assessments) == 3
        assert total == 3

    def test_list_assessments_filter_by_activity(self, db_session, mock_assessments):
        """Test filtering assessments by activity_id."""
        # Arrange
        activity_id = uuid4()
        mock_query = Mock()
        mock_query.filter().count.return_value = 2
        mock_query.filter().order_by().offset().limit().all.return_value = mock_assessments[:2]
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session, activity_id=activity_id)

        # Assert
        assert len(assessments) == 2
        assert total == 2

    def test_list_assessments_filter_by_teacher(self, db_session, mock_assessments):
        """Test filtering assessments by teacher_id."""
        # Arrange
        teacher_id = uuid4()
        mock_query = Mock()
        mock_query.join().filter().count.return_value = 4
        mock_query.join().filter().order_by().offset().limit().all.return_value = mock_assessments[:4]
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session, teacher_id=teacher_id)

        # Assert
        assert len(assessments) == 4
        assert total == 4

    def test_list_assessments_pagination(self, db_session, mock_assessments):
        """Test pagination of assessments."""
        # Arrange
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.order_by().offset().limit().all.return_value = mock_assessments[:2]
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session, skip=2, limit=2)

        # Assert
        assert len(assessments) == 2
        assert total == 10

    def test_list_assessments_empty_results(self, db_session):
        """Test listing with no results."""
        # Arrange
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.order_by().offset().limit().all.return_value = []
        db_session.query.return_value = mock_query

        # Act
        assessments, total = AssessmentService.list_assessments(db=db_session)

        # Assert
        assert len(assessments) == 0
        assert total == 0


class TestAssessmentServiceUpdate:
    """Tests for AssessmentService.update_assessment method."""

    @pytest.fixture
    def db_session(self):
        """Mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def assessment_id(self):
        """Sample assessment ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def update_data(self):
        """Sample update data."""
        return AssessmentUpdate(
            completion_status=CompletionStatus.COMPLETED,
            engagement_level=EngagementLevel.VERY_HIGH,
            notes="Atualização: Aluno superou expectativas",
        )

    @pytest.fixture
    def mock_assessment(self, assessment_id):
        """Mock assessment."""
        assessment = Mock(spec=Assessment)
        assessment.id = assessment_id
        assessment.student_id = uuid4()
        assessment.completion_status = CompletionStatus.IN_PROGRESS
        assessment.engagement_level = EngagementLevel.MEDIUM
        assessment.notes = "Nota inicial"
        return assessment

    def test_update_assessment_success(self, db_session, assessment_id, teacher_id, update_data, mock_assessment):
        """Test successful assessment update."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act
        result = AssessmentService.update_assessment(
            db=db_session, assessment_id=assessment_id, assessment_data=update_data, teacher_id=teacher_id
        )

        # Assert
        assert result == mock_assessment
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    def test_update_assessment_not_found(self, db_session, assessment_id, teacher_id, update_data):
        """Test that assessment not found raises error."""
        # Arrange
        mock_query = Mock()
        mock_query.filter().first.return_value = None
        db_session.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(AssessmentNotFoundError):
            AssessmentService.update_assessment(
                db=db_session, assessment_id=assessment_id, assessment_data=update_data, teacher_id=teacher_id
            )

    def test_update_assessment_permission_denied(self, db_session, assessment_id, update_data, mock_assessment):
        """Test permission denied for wrong teacher."""
        # Arrange
        wrong_teacher_id = uuid4()
        correct_teacher_id = uuid4()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = correct_teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act & Assert
        with pytest.raises(PermissionDeniedError):
            AssessmentService.update_assessment(
                db=db_session,
                assessment_id=assessment_id,
                assessment_data=update_data,
                teacher_id=wrong_teacher_id,
            )

    def test_update_assessment_partial_update(self, db_session, assessment_id, teacher_id, mock_assessment):
        """Test partial update of assessment."""
        # Arrange
        partial_update = AssessmentUpdate(notes="Apenas atualizando a nota")

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act
        result = AssessmentService.update_assessment(
            db=db_session,
            assessment_id=assessment_id,
            assessment_data=partial_update,
            teacher_id=teacher_id,
        )

        # Assert
        assert result == mock_assessment

    def test_update_assessment_logging(self, db_session, assessment_id, teacher_id, update_data, mock_assessment):
        """Test that assessment update is logged."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        with patch("app.services.assessment_service.logger") as mock_logger:
            # Act
            AssessmentService.update_assessment(
                db=db_session,
                assessment_id=assessment_id,
                assessment_data=update_data,
                teacher_id=teacher_id,
            )

            # Assert
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "Assessment updated" in log_message


class TestAssessmentServiceDelete:
    """Tests for AssessmentService.delete_assessment method."""

    @pytest.fixture
    def db_session(self):
        """Mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def assessment_id(self):
        """Sample assessment ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def mock_assessment(self, assessment_id):
        """Mock assessment."""
        assessment = Mock(spec=Assessment)
        assessment.id = assessment_id
        assessment.student_id = uuid4()
        return assessment

    def test_delete_assessment_success(self, db_session, assessment_id, teacher_id, mock_assessment):
        """Test successful assessment deletion."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act
        result = AssessmentService.delete_assessment(db=db_session, assessment_id=assessment_id, teacher_id=teacher_id)

        # Assert
        assert result is True
        db_session.delete.assert_called_once_with(mock_assessment)
        db_session.commit.assert_called_once()

    def test_delete_assessment_not_found(self, db_session, assessment_id, teacher_id):
        """Test that assessment not found raises error."""
        # Arrange
        mock_query = Mock()
        mock_query.filter().first.return_value = None
        db_session.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(AssessmentNotFoundError):
            AssessmentService.delete_assessment(db=db_session, assessment_id=assessment_id, teacher_id=teacher_id)

    def test_delete_assessment_permission_denied(self, db_session, assessment_id, mock_assessment):
        """Test permission denied for wrong teacher."""
        # Arrange
        wrong_teacher_id = uuid4()
        correct_teacher_id = uuid4()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = correct_teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        # Act & Assert
        with pytest.raises(PermissionDeniedError):
            AssessmentService.delete_assessment(db=db_session, assessment_id=assessment_id, teacher_id=wrong_teacher_id)

    def test_delete_assessment_logging(self, db_session, assessment_id, teacher_id, mock_assessment):
        """Test that assessment deletion is logged."""
        # Arrange
        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assessment:
                mock_query.filter().first.return_value = mock_assessment
            elif model == Student:
                mock_query.filter().first.return_value = mock_student
            return mock_query

        db_session.query.side_effect = query_side_effect

        with patch("app.services.assessment_service.logger") as mock_logger:
            # Act
            AssessmentService.delete_assessment(db=db_session, assessment_id=assessment_id, teacher_id=teacher_id)

            # Assert
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "Assessment deleted" in log_message
            assert str(assessment_id) in log_message
