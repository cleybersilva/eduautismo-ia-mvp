"""
Unit tests for ActivityService.

Tests the business logic for activity management and AI generation.
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest

from app.core.exceptions import ActivityNotFoundError, OpenAIError, PermissionDeniedError, StudentNotFoundError
from app.models.activity import Activity
from app.models.student import Student
from app.schemas.activity import ActivityCreate, ActivityGenerate, ActivityUpdate
from app.services.activity_service import ActivityService
from app.utils.constants import ActivityType, DifficultyLevel


class TestActivityServiceGenerateActivity:
    """Tests for ActivityService.generate_activity method."""

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def student_id(self):
        """Sample student ID."""
        return uuid4()

    @pytest.fixture
    def activity_data(self, student_id):
        """Sample activity generation data."""
        return ActivityGenerate(
            student_id=student_id,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
            duration_minutes=45,
            theme="Matemática básica",
        )

    @pytest.fixture
    def mock_student(self, student_id, teacher_id):
        """Mock student."""
        student = MagicMock()
        student.id = student_id
        student.teacher_id = teacher_id
        student.to_profile_dict = Mock(
            return_value={
                "age": 10,
                "tea_level": "level_1",
                "learning_profile": {"visual": 8},
            }
        )
        return student

    @pytest.fixture
    def mock_generated_activity(self):
        """Mock generated activity content from AI."""
        generated = Mock()
        generated.title = "Atividade de Adição"
        generated.description = "Pratique adição com números até 20"
        generated.duration_minutes = 45
        generated.objectives = ["Praticar adição", "Desenvolver raciocínio"]
        generated.materials = ["Lápis", "Papel"]
        generated.instructions = ["Passo 1", "Passo 2"]
        generated.adaptations = ["Usar apoio visual"]
        generated.visual_supports = ["Imagens de números"]
        generated.success_criteria = ["Completar 80% dos exercícios"]
        return generated

    @pytest.mark.asyncio
    async def test_generate_activity_success(self, activity_data, teacher_id, mock_student, mock_generated_activity):
        """Test successful activity generation with AI."""
        # Arrange
        db_session = AsyncMock()

        # Mock database query for student
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Mock NLP service
        with patch("app.services.activity_service.get_nlp_service") as mock_get_nlp:
            mock_nlp_service = Mock()
            mock_nlp_service.generate_activity = AsyncMock(return_value=mock_generated_activity)
            mock_nlp_service.default_model = "gpt-4"
            mock_get_nlp.return_value = mock_nlp_service

            # Act
            activity = await ActivityService.generate_activity(
                db=db_session, activity_data=activity_data, teacher_id=teacher_id
            )

            # Assert
            assert activity.title == "Atividade de Adição"
            assert activity.generated_by_ai is True
            assert activity.student_id == activity_data.student_id
            assert activity.created_by_id == teacher_id

            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()
            db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_activity_student_not_found(self, activity_data, teacher_id):
        """Test that student not found raises error."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(StudentNotFoundError):
            await ActivityService.generate_activity(db=db_session, activity_data=activity_data, teacher_id=teacher_id)

    @pytest.mark.asyncio
    async def test_generate_activity_permission_denied(self, activity_data, mock_student):
        """Test permission denied for wrong teacher."""
        # Arrange
        db_session = AsyncMock()
        wrong_teacher_id = uuid4()
        mock_student.teacher_id = uuid4()  # Different teacher

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(PermissionDeniedError) as exc_info:
            await ActivityService.generate_activity(
                db=db_session, activity_data=activity_data, teacher_id=wrong_teacher_id
            )

        assert "não tem permissão" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_activity_ai_error(self, activity_data, teacher_id, mock_student):
        """Test that OpenAI error is properly raised."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Mock NLP service to raise error
        with patch("app.services.activity_service.get_nlp_service") as mock_get_nlp:
            mock_nlp_service = Mock()
            mock_nlp_service.generate_activity = AsyncMock(side_effect=OpenAIError("AI service unavailable"))
            mock_get_nlp.return_value = mock_nlp_service

            # Act & Assert
            with pytest.raises(OpenAIError):
                await ActivityService.generate_activity(
                    db=db_session, activity_data=activity_data, teacher_id=teacher_id
                )

    @pytest.mark.asyncio
    async def test_generate_activity_generic_error_rollback(
        self, activity_data, teacher_id, mock_student, mock_generated_activity
    ):
        """Test that generic errors trigger rollback."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Mock commit to raise error
        db_session.commit.side_effect = Exception("Database error")

        # Mock NLP service
        with patch("app.services.activity_service.get_nlp_service") as mock_get_nlp:
            mock_nlp_service = Mock()
            mock_nlp_service.generate_activity = AsyncMock(return_value=mock_generated_activity)
            mock_nlp_service.default_model = "gpt-4"
            mock_get_nlp.return_value = mock_nlp_service

            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                await ActivityService.generate_activity(
                    db=db_session, activity_data=activity_data, teacher_id=teacher_id
                )

            # Verify rollback was called
            db_session.rollback.assert_called_once()


class TestActivityServiceCreateActivity:
    """Tests for ActivityService.create_activity method."""

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def student_id(self):
        """Sample student ID."""
        return uuid4()

    @pytest.fixture
    def activity_data(self, student_id):
        """Sample manual activity data."""
        return ActivityCreate(
            student_id=student_id,
            title="Atividade Manual",
            description="Atividade criada pelo professor",
            activity_type=ActivityType.SOCIAL,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            objectives=["Desenvolver habilidades sociais"],
            materials=["Cartões de emoções", "Espelho"],
            instructions=["Interagir com colegas"],
        )

    @pytest.fixture
    def mock_student(self, student_id, teacher_id):
        """Mock student."""
        student = Mock(spec=Student)
        student.id = student_id
        student.teacher_id = teacher_id
        return student

    @pytest.mark.asyncio
    async def test_create_activity_success(self, activity_data, teacher_id, mock_student):
        """Test successful manual activity creation."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Act
        activity = await ActivityService.create_activity(
            db=db_session, activity_data=activity_data, teacher_id=teacher_id
        )

        # Assert
        assert activity.title == "Atividade Manual"
        assert activity.generated_by_ai is False
        assert activity.created_by_id == teacher_id
        assert activity.student_id == activity_data.student_id

        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_activity_student_not_found(self, activity_data, teacher_id):
        """Test that student not found raises error."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(StudentNotFoundError):
            await ActivityService.create_activity(db=db_session, activity_data=activity_data, teacher_id=teacher_id)

    @pytest.mark.asyncio
    async def test_create_activity_permission_denied(self, activity_data, mock_student):
        """Test permission denied for wrong teacher."""
        # Arrange
        db_session = AsyncMock()
        wrong_teacher_id = uuid4()
        mock_student.teacher_id = uuid4()  # Different teacher

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_student
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(PermissionDeniedError):
            await ActivityService.create_activity(
                db=db_session, activity_data=activity_data, teacher_id=wrong_teacher_id
            )


class TestActivityServiceGetActivity:
    """Tests for ActivityService.get_activity method."""

    @pytest.fixture
    def activity_id(self):
        """Sample activity ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def mock_activity(self, activity_id):
        """Mock activity."""
        activity = Mock(spec=Activity)
        activity.id = activity_id
        activity.student_id = uuid4()
        return activity

    @pytest.mark.asyncio
    async def test_get_activity_success_without_teacher_id(self, activity_id, mock_activity):
        """Test get activity without teacher check."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_activity
        db_session.execute.return_value = mock_result

        # Act
        result = await ActivityService.get_activity(db=db_session, activity_id=activity_id)

        # Assert
        assert result == mock_activity

    @pytest.mark.asyncio
    async def test_get_activity_success_with_teacher_id(self, activity_id, teacher_id, mock_activity):
        """Test get activity with teacher permission check."""
        # Arrange
        db_session = AsyncMock()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        async def execute_side_effect(query):
            mock_result = Mock()
            # First call returns activity, second call returns student
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            if execute_side_effect.call_count == 0:
                mock_result.scalar_one_or_none.return_value = mock_activity
            else:
                mock_result.scalar_one_or_none.return_value = mock_student

            execute_side_effect.call_count += 1
            return mock_result

        db_session.execute.side_effect = execute_side_effect

        # Act
        result = await ActivityService.get_activity(db=db_session, activity_id=activity_id, teacher_id=teacher_id)

        # Assert
        assert result == mock_activity

    @pytest.mark.asyncio
    async def test_get_activity_not_found(self, activity_id):
        """Test that activity not found raises error."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ActivityNotFoundError):
            await ActivityService.get_activity(db=db_session, activity_id=activity_id)

    @pytest.mark.asyncio
    async def test_get_activity_permission_denied(self, activity_id, mock_activity):
        """Test permission denied for wrong teacher."""
        # Arrange
        db_session = AsyncMock()
        wrong_teacher_id = uuid4()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = uuid4()  # Different teacher

        async def execute_side_effect(query):
            mock_result = Mock()
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            if execute_side_effect.call_count == 0:
                mock_result.scalar_one_or_none.return_value = mock_activity
            else:
                mock_result.scalar_one_or_none.return_value = mock_student

            execute_side_effect.call_count += 1
            return mock_result

        db_session.execute.side_effect = execute_side_effect

        # Act & Assert
        with pytest.raises(PermissionDeniedError):
            await ActivityService.get_activity(db=db_session, activity_id=activity_id, teacher_id=wrong_teacher_id)


class TestActivityServiceListActivities:
    """Tests for ActivityService.list_activities method."""

    @pytest.fixture
    def mock_activities(self):
        """Mock list of activities."""
        activities = []
        for i in range(5):
            activity = Mock(spec=Activity)
            activity.id = uuid4()
            activities.append(activity)
        return activities

    @pytest.mark.asyncio
    async def test_list_activities_no_filters(self, mock_activities):
        """Test listing activities without filters."""
        # Arrange
        db_session = AsyncMock()

        # Mock count query
        count_result = Mock()
        count_result.scalar_one.return_value = len(mock_activities)

        # Mock list query
        list_result = Mock()
        list_result.scalars().all.return_value = mock_activities

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.list_activities(db=db_session)

        # Assert
        assert len(activities) == 5
        assert total == 5

    @pytest.mark.asyncio
    async def test_list_activities_filter_by_student(self, mock_activities):
        """Test filtering activities by student_id."""
        # Arrange
        db_session = AsyncMock()
        student_id = uuid4()

        count_result = Mock()
        count_result.scalar_one.return_value = 3

        list_result = Mock()
        list_result.scalars().all.return_value = mock_activities[:3]

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.list_activities(db=db_session, student_id=student_id)

        # Assert
        assert len(activities) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_list_activities_filter_by_type_and_difficulty(self, mock_activities):
        """Test filtering by activity type and difficulty."""
        # Arrange
        db_session = AsyncMock()

        count_result = Mock()
        count_result.scalar_one.return_value = 2

        list_result = Mock()
        list_result.scalars().all.return_value = mock_activities[:2]

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.list_activities(
            db=db_session,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
        )

        # Assert
        assert len(activities) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_activities_pagination(self):
        """Test pagination of activities."""
        # Arrange
        db_session = AsyncMock()

        count_result = Mock()
        count_result.scalar_one.return_value = 10

        list_result = Mock()
        list_result.scalars().all.return_value = [Mock(spec=Activity) for _ in range(2)]

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.list_activities(db=db_session, skip=5, limit=2)

        # Assert
        assert len(activities) == 2
        assert total == 10


class TestActivityServiceUpdateActivity:
    """Tests for ActivityService.update_activity method."""

    @pytest.fixture
    def activity_id(self):
        """Sample activity ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def update_data(self):
        """Sample update data."""
        return ActivityUpdate(
            title="Título Atualizado",
            description="Descrição atualizada",
        )

    @pytest.fixture
    def mock_activity(self, activity_id):
        """Mock activity."""
        activity = Mock(spec=Activity)
        activity.id = activity_id
        activity.title = "Título Original"
        activity.description = "Descrição original"
        activity.student_id = uuid4()
        return activity

    @pytest.mark.asyncio
    async def test_update_activity_success(self, activity_id, teacher_id, update_data, mock_activity):
        """Test successful activity update."""
        # Arrange
        db_session = AsyncMock()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        async def execute_side_effect(query):
            mock_result = Mock()
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            if execute_side_effect.call_count == 0:
                mock_result.scalar_one_or_none.return_value = mock_activity
            else:
                mock_result.scalar_one_or_none.return_value = mock_student

            execute_side_effect.call_count += 1
            return mock_result

        db_session.execute.side_effect = execute_side_effect

        # Act
        _result = await ActivityService.update_activity(  # noqa: F841
            db=db_session,
            activity_id=activity_id,
            activity_data=update_data,
            teacher_id=teacher_id,
        )

        # Assert
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_activity_not_found(self, activity_id, teacher_id, update_data):
        """Test that activity not found raises error."""
        # Arrange
        db_session = AsyncMock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ActivityNotFoundError):
            await ActivityService.update_activity(
                db=db_session,
                activity_id=activity_id,
                activity_data=update_data,
                teacher_id=teacher_id,
            )


class TestActivityServiceDeleteActivity:
    """Tests for ActivityService.delete_activity method."""

    @pytest.fixture
    def activity_id(self):
        """Sample activity ID."""
        return uuid4()

    @pytest.fixture
    def teacher_id(self):
        """Sample teacher ID."""
        return uuid4()

    @pytest.fixture
    def mock_activity(self, activity_id):
        """Mock activity."""
        activity = Mock(spec=Activity)
        activity.id = activity_id
        activity.is_published = True
        activity.student_id = uuid4()
        return activity

    @pytest.mark.asyncio
    async def test_delete_activity_success(self, activity_id, teacher_id, mock_activity):
        """Test successful activity deletion (unpublish)."""
        # Arrange
        db_session = AsyncMock()

        mock_student = Mock(spec=Student)
        mock_student.teacher_id = teacher_id

        async def execute_side_effect(query):
            mock_result = Mock()
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            if execute_side_effect.call_count == 0:
                mock_result.scalar_one_or_none.return_value = mock_activity
            else:
                mock_result.scalar_one_or_none.return_value = mock_student

            execute_side_effect.call_count += 1
            return mock_result

        db_session.execute.side_effect = execute_side_effect

        # Act
        await ActivityService.delete_activity(db=db_session, activity_id=activity_id, teacher_id=teacher_id)

        # Assert
        assert mock_activity.is_published is False
        db_session.commit.assert_called_once()


class TestActivityServiceGetActivitiesByTheme:
    """Tests for ActivityService.get_activities_by_theme method."""

    @pytest.fixture
    def mock_activities(self):
        """Mock list of activities."""
        activities = []
        for i in range(3):
            activity = Mock(spec=Activity)
            activity.id = uuid4()
            activity.theme = "Matemática"
            activities.append(activity)
        return activities

    @pytest.mark.asyncio
    async def test_get_activities_by_theme_success(self, mock_activities):
        """Test getting activities by theme."""
        # Arrange
        db_session = AsyncMock()

        count_result = Mock()
        count_result.scalar_one.return_value = len(mock_activities)

        list_result = Mock()
        list_result.scalars().all.return_value = mock_activities

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.get_activities_by_theme(db=db_session, theme="Matemática")

        # Assert
        assert len(activities) == 3
        assert total == 3
        assert all(act.theme == "Matemática" for act in activities)

    @pytest.mark.asyncio
    async def test_get_activities_by_theme_with_teacher_filter(self, mock_activities):
        """Test getting activities by theme with teacher filter."""
        # Arrange
        db_session = AsyncMock()
        teacher_id = uuid4()

        count_result = Mock()
        count_result.scalar_one.return_value = 2

        list_result = Mock()
        list_result.scalars().all.return_value = mock_activities[:2]

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.get_activities_by_theme(
            db=db_session, theme="Ciências", teacher_id=teacher_id
        )

        # Assert
        assert len(activities) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_activities_by_theme_empty_results(self):
        """Test getting activities with no results."""
        # Arrange
        db_session = AsyncMock()

        count_result = Mock()
        count_result.scalar_one.return_value = 0

        list_result = Mock()
        list_result.scalars().all.return_value = []

        async def execute_side_effect(query):
            if not hasattr(execute_side_effect, "call_count"):
                execute_side_effect.call_count = 0

            result = count_result if execute_side_effect.call_count == 0 else list_result
            execute_side_effect.call_count += 1
            return result

        db_session.execute.side_effect = execute_side_effect

        # Act
        activities, total = await ActivityService.get_activities_by_theme(db=db_session, theme="História")

        # Assert
        assert len(activities) == 0
        assert total == 0
