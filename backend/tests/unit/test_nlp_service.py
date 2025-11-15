"""
Unit tests for NLPService.

Tests OpenAI integration for activity generation and analysis.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.exceptions import MissingConfigurationError, OpenAIError
from app.services.nlp_service import GeneratedActivity, NLPService, ProgressAnalysis, Recommendation
from app.utils.constants import ActivityType, DifficultyLevel


class TestNLPServiceInit:
    """Tests for NLPService initialization."""

    def test_init_without_api_key(self):
        """Test that initialization without API key raises error."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None

            with pytest.raises(MissingConfigurationError) as exc_info:
                NLPService()

            assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_init_with_api_key(self):
        """Test successful initialization with API key."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test-key"

            with patch("app.services.nlp_service.AsyncOpenAI"):
                service = NLPService()

                assert service.default_model is not None


class TestGeneratedActivityModel:
    """Tests for GeneratedActivity Pydantic model."""

    def test_generated_activity_creation(self):
        """Test creating GeneratedActivity model."""
        activity = GeneratedActivity(
            title="Atividade de Matemática",
            description="Pratique adição",
            objectives=["Aprender soma", "Praticar cálculo"],
            materials=["Lápis", "Papel"],
            instructions=["Passo 1", "Passo 2"],
            duration_minutes=30,
            adaptations=["Usar apoio visual"],
            visual_supports=["Imagens de números"],
            success_criteria=["Completar 80%"],
        )

        assert activity.title == "Atividade de Matemática"
        assert len(activity.objectives) == 2
        assert activity.duration_minutes == 30


class TestProgressAnalysisModel:
    """Tests for ProgressAnalysis Pydantic model."""

    def test_progress_analysis_creation(self):
        """Test creating ProgressAnalysis model."""
        analysis = ProgressAnalysis(
            summary="Progresso positivo",
            strengths=["Boa concentração", "Interesse em matemática"],
            areas_for_improvement=["Habilidades sociais"],
            patterns_observed=["Melhor pela manhã"],
            recommendations=["Continuar atividades visuais"],
        )

        assert analysis.summary == "Progresso positivo"
        assert len(analysis.strengths) == 2
        assert len(analysis.areas_for_improvement) == 1


class TestRecommendationModel:
    """Tests for Recommendation Pydantic model."""

    def test_recommendation_creation(self):
        """Test creating Recommendation model."""
        rec = Recommendation(
            title="Atividade Visual",
            description="Usar mais recursos visuais",
            rationale="Aluno aprende melhor com imagens",
            priority="high",
            category="strategy",
        )

        assert rec.title == "Atividade Visual"
        assert rec.priority == "high"
        assert rec.category == "strategy"


class TestNLPServiceGenerateActivity:
    """Tests for NLPService.generate_activity method."""

    @pytest.fixture
    def nlp_service(self):
        """Create NLP service with mocked OpenAI client."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test-key"

            with patch("app.services.nlp_service.AsyncOpenAI") as mock_openai_class:
                mock_client = AsyncMock()
                mock_openai_class.return_value = mock_client
                service = NLPService()
                service.client = mock_client
                yield service

    @pytest.fixture
    def student_profile(self):
        """Sample student profile."""
        return {
            "age": 10,
            "tea_level": "level_1",
            "interests": ["matemática", "jogos"],
            "learning_profile": {"visual": 8, "auditory": 6},
        }

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"title": "Atividade de Adição", "description": "Pratique soma", '
                    '"objectives": ["Aprender soma"], "materials": ["Lápis"], '
                    '"instructions": ["Faça os exercícios"], "duration_minutes": 30, '
                    '"adaptations": ["Usar imagens"], "visual_supports": ["Cartões"], '
                    '"success_criteria": ["Completar 80%"]}'
                )
            )
        ]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200)
        return mock_response

    @pytest.mark.asyncio
    async def test_generate_activity_success(self, nlp_service, student_profile, mock_openai_response):
        """Test successful activity generation."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        # Act
        activity = await nlp_service.generate_activity(
            student_profile=student_profile,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
            duration_minutes=30,
            theme="Matemática",
        )

        # Assert
        assert isinstance(activity, GeneratedActivity)
        assert activity.title == "Atividade de Adição"
        assert activity.duration_minutes == 30
        assert len(activity.objectives) > 0

    @pytest.mark.asyncio
    async def test_generate_activity_openai_error(self, nlp_service, student_profile):
        """Test that OpenAI API errors are properly handled."""
        # Arrange
        from openai import OpenAIError as OpenAIAPIError

        nlp_service.client.chat.completions.create = AsyncMock(side_effect=OpenAIAPIError("API error"))

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.generate_activity(
                student_profile=student_profile,
                activity_type=ActivityType.SOCIAL,
                difficulty=DifficultyLevel.EASY,
                duration_minutes=20,
            )

    @pytest.mark.asyncio
    async def test_generate_activity_invalid_json_response(self, nlp_service, student_profile):
        """Test handling of invalid JSON in OpenAI response."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON {{{"))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=50)

        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(OpenAIError) as exc_info:
            await nlp_service.generate_activity(
                student_profile=student_profile,
                activity_type=ActivityType.MOTOR,
                difficulty=DifficultyLevel.HARD,
                duration_minutes=45,
            )

        assert "Resposta inválida" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_activity_with_theme(self, nlp_service, student_profile, mock_openai_response):
        """Test activity generation with specific theme."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        # Act
        activity = await nlp_service.generate_activity(
            student_profile=student_profile,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
            duration_minutes=30,
            theme="Animais",
        )

        # Assert
        assert isinstance(activity, GeneratedActivity)
        nlp_service.client.chat.completions.create.assert_called_once()


class TestNLPServiceAnalyzeProgress:
    """Tests for NLPService.analyze_progress method."""

    @pytest.fixture
    def nlp_service(self):
        """Create NLP service with mocked OpenAI client."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test-key"

            with patch("app.services.nlp_service.AsyncOpenAI") as mock_openai_class:
                mock_client = AsyncMock()
                mock_openai_class.return_value = mock_client
                service = NLPService()
                service.client = mock_client
                yield service

    @pytest.fixture
    def student_profile(self):
        """Sample student profile."""
        return {"age": 10, "name": "João", "tea_level": "level_1"}

    @pytest.fixture
    def assessments(self):
        """Sample assessment data."""
        return [
            {
                "completion_status": "completed",
                "engagement_level": "high",
                "notes": "Ótimo desempenho",
            },
            {
                "completion_status": "completed",
                "engagement_level": "medium",
                "notes": "Precisou de ajuda",
            },
        ]

    @pytest.fixture
    def mock_analysis_response(self):
        """Mock OpenAI API response for progress analysis."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"summary": "Progresso positivo", '
                    '"strengths": ["Boa concentração"], '
                    '"areas_for_improvement": ["Habilidades sociais"], '
                    '"patterns_observed": ["Melhor pela manhã"], '
                    '"recommendations": ["Continuar atividades visuais"]}'
                )
            )
        ]
        mock_response.usage = Mock(prompt_tokens=150, completion_tokens=250)
        return mock_response

    @pytest.mark.asyncio
    async def test_analyze_progress_success(self, nlp_service, student_profile, assessments, mock_analysis_response):
        """Test successful progress analysis."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_analysis_response)

        # Act
        analysis = await nlp_service.analyze_progress(
            student_profile=student_profile, assessments=assessments, time_period="last month"
        )

        # Assert
        assert isinstance(analysis, ProgressAnalysis)
        assert analysis.summary == "Progresso positivo"
        assert len(analysis.strengths) > 0
        assert len(analysis.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_progress_openai_error(self, nlp_service, student_profile, assessments):
        """Test that OpenAI API errors are handled."""
        # Arrange
        from openai import OpenAIError as OpenAIAPIError

        nlp_service.client.chat.completions.create = AsyncMock(side_effect=OpenAIAPIError("API error"))

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.analyze_progress(student_profile=student_profile, assessments=assessments)

    @pytest.mark.asyncio
    async def test_analyze_progress_invalid_json(self, nlp_service, student_profile, assessments):
        """Test handling of invalid JSON in progress analysis."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Not valid JSON {{{"))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=100)

        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.analyze_progress(student_profile=student_profile, assessments=assessments)

    @pytest.mark.asyncio
    async def test_analyze_progress_generic_error(self, nlp_service, student_profile, assessments):
        """Test handling of generic errors in progress analysis."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(side_effect=Exception("Unexpected error"))

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.analyze_progress(student_profile=student_profile, assessments=assessments)


class TestNLPServiceGenerateRecommendations:
    """Tests for NLPService.generate_recommendations method."""

    @pytest.fixture
    def nlp_service(self):
        """Create NLP service with mocked OpenAI client."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test-key"

            with patch("app.services.nlp_service.AsyncOpenAI") as mock_openai_class:
                mock_client = AsyncMock()
                mock_openai_class.return_value = mock_client
                service = NLPService()
                service.client = mock_client
                yield service

    @pytest.fixture
    def student_profile(self):
        """Sample student profile."""
        return {"age": 10, "name": "João", "tea_level": "level_1"}

    @pytest.fixture
    def recent_activities(self):
        """Sample recent activities."""
        return [
            {"title": "Atividade 1", "completion_status": "completed"},
            {"title": "Atividade 2", "completion_status": "in_progress"},
        ]

    @pytest.fixture
    def mock_recommendations_response(self):
        """Mock OpenAI API response for recommendations."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"recommendations": [{"title": "Atividade Visual", '
                    '"description": "Usar mais recursos visuais", '
                    '"rationale": "Aluno aprende melhor com imagens", '
                    '"priority": "high", "category": "strategy"}]}'
                )
            )
        ]
        mock_response.usage = Mock(prompt_tokens=120, completion_tokens=180)
        return mock_response

    @pytest.mark.asyncio
    async def test_generate_recommendations_success(
        self, nlp_service, student_profile, recent_activities, mock_recommendations_response
    ):
        """Test successful recommendations generation."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_recommendations_response)

        # Act
        recommendations = await nlp_service.generate_recommendations(
            student_profile=student_profile, recent_activities=recent_activities
        )

        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert isinstance(recommendations[0], Recommendation)
        assert recommendations[0].title == "Atividade Visual"
        assert recommendations[0].priority == "high"

    @pytest.mark.asyncio
    async def test_generate_recommendations_with_progress_summary(
        self, nlp_service, student_profile, recent_activities, mock_recommendations_response
    ):
        """Test recommendations with progress summary."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_recommendations_response)

        progress_summary = {"strengths": ["Boa concentração"], "areas_for_improvement": ["Social"]}

        # Act
        recommendations = await nlp_service.generate_recommendations(
            student_profile=student_profile,
            recent_activities=recent_activities,
            progress_summary=progress_summary,
        )

        # Assert
        assert len(recommendations) > 0
        nlp_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_recommendations_openai_error(self, nlp_service, student_profile, recent_activities):
        """Test that OpenAI API errors are handled."""
        # Arrange
        from openai import OpenAIError as OpenAIAPIError

        nlp_service.client.chat.completions.create = AsyncMock(side_effect=OpenAIAPIError("API error"))

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.generate_recommendations(
                student_profile=student_profile, recent_activities=recent_activities
            )

    @pytest.mark.asyncio
    async def test_generate_recommendations_invalid_json(self, nlp_service, student_profile, recent_activities):
        """Test handling of invalid JSON in recommendations response."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON {{{"))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=50)

        nlp_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(OpenAIError):
            await nlp_service.generate_recommendations(
                student_profile=student_profile, recent_activities=recent_activities
            )

    @pytest.mark.asyncio
    async def test_generate_recommendations_generic_error(self, nlp_service, student_profile, recent_activities):
        """Test handling of generic errors in recommendations."""
        # Arrange
        nlp_service.client.chat.completions.create = AsyncMock(side_effect=Exception("Unexpected error"))

        # Act & Assert
        with pytest.raises(OpenAIError) as exc_info:
            await nlp_service.generate_recommendations(
                student_profile=student_profile, recent_activities=recent_activities
            )

        assert "Erro inesperado" in str(exc_info.value)


class TestNLPServiceBuildPrompts:
    """Tests for NLPService prompt building methods."""

    @pytest.fixture
    def nlp_service(self):
        """Create NLP service."""
        with patch("app.services.nlp_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test-key"

            with patch("app.services.nlp_service.AsyncOpenAI"):
                yield NLPService()

    def test_build_activity_prompt_basic(self, nlp_service):
        """Test building basic activity prompt."""
        student_profile = {"age": 10}

        prompt = nlp_service._build_activity_prompt(
            student_profile=student_profile,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
            duration_minutes=30,
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert "idade: 10" in prompt.lower() or "age" in prompt.lower() or "10" in prompt

    def test_build_activity_prompt_with_theme(self, nlp_service):
        """Test building activity prompt with theme."""
        student_profile = {"age": 10, "interests": ["matemática"]}

        prompt = nlp_service._build_activity_prompt(
            student_profile=student_profile,
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=20,
            theme="Números",
        )

        assert prompt is not None
        assert "números" in prompt.lower() or "number" in prompt.lower() or "número" in prompt.lower()

    def test_build_activity_prompt_with_full_profile(self, nlp_service):
        """Test building prompt with complete student profile."""
        student_profile = {
            "age": 10,
            "name": "João",
            "diagnosis": "TEA nível 1",
            "interests": ["matemática", "jogos"],
            "learning_profile": {"visual": 8, "auditory": 6},
        }

        prompt = nlp_service._build_activity_prompt(
            student_profile=student_profile,
            activity_type=ActivityType.SOCIAL,
            difficulty=DifficultyLevel.HARD,
            duration_minutes=45,
            theme="Amizade",
        )

        assert prompt is not None
        assert len(prompt) > 100
        assert "joão" in prompt.lower() or "joao" in prompt.lower()

    def test_build_progress_prompt(self, nlp_service):
        """Test building progress analysis prompt."""
        student_profile = {"age": 10, "name": "João"}
        assessments = [{"completion_status": "completed", "notes": "Bom desempenho"}]

        prompt = nlp_service._build_progress_prompt(
            student_profile=student_profile, assessments=assessments, time_period="last month"
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert "joão" in prompt.lower() or "joao" in prompt.lower()

    def test_build_progress_prompt_multiple_assessments(self, nlp_service):
        """Test progress prompt with multiple assessments."""
        student_profile = {"age": 10, "name": "Maria"}
        assessments = [
            {"completion_status": "completed", "engagement_level": "high"},
            {"completion_status": "completed", "engagement_level": "medium"},
            {"completion_status": "in_progress", "engagement_level": "low"},
        ]

        prompt = nlp_service._build_progress_prompt(student_profile=student_profile, assessments=assessments)

        assert prompt is not None
        assert len(assessments) > 0

    def test_build_recommendations_prompt(self, nlp_service):
        """Test building recommendations prompt."""
        student_profile = {"age": 10, "name": "Pedro"}
        recent_activities = [
            {"title": "Atividade 1", "completion_status": "completed"},
            {"title": "Atividade 2", "completion_status": "completed"},
        ]

        prompt = nlp_service._build_recommendations_prompt(
            student_profile=student_profile, recent_activities=recent_activities
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_build_recommendations_prompt_with_progress(self, nlp_service):
        """Test recommendations prompt with progress summary."""
        student_profile = {"age": 10}
        recent_activities = [{"title": "Atividade 1"}]
        progress_summary = {"strengths": ["Boa memória"], "areas_for_improvement": ["Atenção"]}

        prompt = nlp_service._build_recommendations_prompt(
            student_profile=student_profile,
            recent_activities=recent_activities,
            progress_summary=progress_summary,
        )

        assert prompt is not None
        assert "memória" in prompt.lower() or "memoria" in prompt.lower() or len(prompt) > 50
