"""
Unit tests for ML Service.

Tests behavioral classification, feature extraction, and predictions.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import numpy as np
import pytest

from app.models.assessment import Assessment
from app.models.student import Student
from app.services.ml_service import MLService, get_ml_service
from app.utils.constants import (
    CompletionStatus,
    DifficultyRating,
    EngagementLevel,
    TEALevel,
)


class TestMLServiceInit:
    """Test ML Service initialization."""

    def test_ml_service_init(self):
        """Test service initialization."""
        service = MLService()

        assert service.behavioral_model is None
        assert service.success_predictor is None
        assert service.confidence_threshold == 0.75
        assert service.RISK_LEVELS == ["baixo", "medio", "alto", "muito_alto"]

    def test_get_ml_service_singleton(self):
        """Test get_ml_service returns singleton instance."""
        service1 = get_ml_service()
        service2 = get_ml_service()

        assert service1 is service2


class TestFeatureExtraction:
    """Test feature extraction from student profiles."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    @pytest.fixture
    def sample_student(self):
        """Create sample student."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 10
        student.tea_level = TEALevel.LEVEL_1
        student.interests = ["matemática", "jogos", "robótica"]
        student.learning_profile = {
            "visual": 8,
            "auditory": 6,
            "kinesthetic": 7,
            "verbal": 6,
            "logical": 8,
            "social": 5,
            "emotional": 6,
            "attention_span": 7,
            "sensory_sensitivity": 6,
            "communication_level": 7,
            "social_skills": 6,
        }
        return student

    def test_extract_student_features_complete_profile(self, ml_service, sample_student):
        """Test feature extraction with complete student profile."""
        features = ml_service.extract_student_features(sample_student, assessments=[])

        # Check basic features
        assert features["age"] == 10.0
        assert features["tea_level"] == 1.0
        assert features["interest_count"] == 3.0

        # Check learning profile features
        assert features["learning_visual"] == 8.0
        assert features["learning_auditory"] == 6.0
        assert features["attention_span"] == 7.0
        assert features["social_skills"] == 6.0

        # Check default assessment features (no history)
        assert features["completion_rate"] == 0.5
        assert features["avg_engagement"] == 2.0

    def test_extract_student_features_no_profile(self, ml_service):
        """Test feature extraction with student without learning profile."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 8
        student.tea_level = None
        student.interests = []
        student.learning_profile = None

        features = ml_service.extract_student_features(student, assessments=[])

        # Check defaults
        assert features["age"] == 8.0
        assert features["tea_level"] == 0.0
        assert features["interest_count"] == 0.0
        assert features["learning_visual"] == 5.0  # Default value
        assert features["attention_span"] == 5.0

    def test_extract_student_features_with_assessments(self, ml_service, sample_student):
        """Test feature extraction with assessment history."""
        # Create mock assessments
        assessments = []
        for i in range(5):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED if i < 4 else CompletionStatus.ABANDONED
            assessment.engagement_level = EngagementLevel.HIGH if i < 3 else EngagementLevel.MEDIUM
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "partial"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        features = ml_service.extract_student_features(sample_student, assessments=assessments)

        # Check computed assessment features
        assert features["completion_rate"] == 0.8  # 4 out of 5 completed
        assert features["avg_engagement"] > 2.0  # High engagement
        assert features["success_rate"] > 0.0

    def test_extract_activity_features(self, ml_service):
        """Test activity feature extraction."""
        activity_data = {
            "difficulty": 5,
            "duration_minutes": 30,
            "activity_type": "cognitive",
            "adaptations": ["Visual supports", "Simplified instructions"],
            "visual_supports": ["Pictures", "Icons"],
        }

        features = ml_service.extract_activity_features(activity_data)

        assert features["activity_difficulty"] == 5.0
        assert features["duration_minutes"] == 30.0
        assert features["type_cognitive"] == 1.0
        assert features["type_social"] == 0.0
        assert features["has_adaptations"] == 1.0
        assert features["has_visual_supports"] == 1.0


class TestRiskPrediction:
    """Test behavioral risk prediction."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    @pytest.fixture
    def low_risk_student(self):
        """Create low-risk student profile."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 10
        student.tea_level = TEALevel.LEVEL_1
        student.interests = ["matemática", "jogos"]
        student.learning_profile = {
            "visual": 8,
            "auditory": 7,
            "kinesthetic": 8,
            "verbal": 7,
            "logical": 8,
            "social": 7,
            "emotional": 7,
            "attention_span": 8,
            "sensory_sensitivity": 5,
            "communication_level": 8,
            "social_skills": 7,
        }
        return student

    @pytest.fixture
    def high_risk_student(self):
        """Create high-risk student profile."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 8
        student.tea_level = TEALevel.LEVEL_3
        student.interests = []
        student.learning_profile = {
            "visual": 3,
            "auditory": 2,
            "kinesthetic": 3,
            "verbal": 2,
            "logical": 3,
            "social": 2,
            "emotional": 2,
            "attention_span": 2,
            "sensory_sensitivity": 9,
            "communication_level": 2,
            "social_skills": 2,
        }
        return student

    def test_predict_risk_level_low_risk(self, ml_service, low_risk_student):
        """Test risk prediction for low-risk student."""
        # Create positive assessment history
        assessments = []
        for i in range(10):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.HIGH
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "full"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        result = ml_service.predict_risk_level(low_risk_student, assessments=assessments)

        assert result["risk_level"] in ml_service.RISK_LEVELS
        assert "confidence" in result
        assert "method" in result
        assert result["method"] in ["ml_model", "rule_based"]

        # Should be low or medium risk
        assert result["risk_level"] in ["baixo", "medio"]

    def test_predict_risk_level_high_risk(self, ml_service, high_risk_student):
        """Test risk prediction for high-risk student."""
        # Create problematic assessment history
        assessments = []
        for i in range(10):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.ABANDONED if i < 7 else CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.LOW
            assessment.difficulty_rating = DifficultyRating.TOO_HARD
            assessment.independence_level = "dependent"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        result = ml_service.predict_risk_level(high_risk_student, assessments=assessments)

        assert result["risk_level"] in ml_service.RISK_LEVELS
        # Should be high or very high risk
        assert result["risk_level"] in ["alto", "muito_alto"]

    def test_predict_risk_level_no_assessments(self, ml_service, low_risk_student):
        """Test risk prediction without assessment history."""
        result = ml_service.predict_risk_level(low_risk_student, assessments=None)

        assert result["risk_level"] in ml_service.RISK_LEVELS
        assert result["confidence"] > 0
        # Should default to medium without history
        assert result["risk_level"] in ["baixo", "medio"]

    def test_predict_with_ml_model(self, ml_service, low_risk_student):
        """Test prediction with loaded ML model."""
        # Mock trained model
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([0]))  # Index 0 = "baixo"
        mock_model.predict_proba = MagicMock(return_value=np.array([[0.7, 0.2, 0.08, 0.02]]))

        ml_service.behavioral_model = mock_model
        ml_service.feature_names = ["age", "tea_level", "completion_rate"]

        result = ml_service.predict_risk_level(low_risk_student, assessments=[])

        assert result["method"] == "ml_model"
        assert result["risk_level"] == "baixo"
        assert result["confidence"] == 0.7
        assert "probabilities" in result


class TestActivitySuccessPrediction:
    """Test activity success prediction."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    @pytest.fixture
    def sample_student(self):
        """Create sample student."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 10
        student.tea_level = TEALevel.LEVEL_1
        student.interests = ["matemática"]
        student.learning_profile = {
            "visual": 8,
            "auditory": 6,
            "attention_span": 7,
            "social_skills": 6,
        }
        return student

    def test_predict_activity_success_appropriate_difficulty(self, ml_service, sample_student):
        """Test success prediction for appropriately difficult activity."""
        # Create positive assessment history
        assessments = []
        for i in range(5):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.HIGH
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "partial"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        activity_data = {"difficulty": 5, "duration_minutes": 30, "activity_type": "cognitive"}

        result = ml_service.predict_activity_success(sample_student, activity_data, assessments=assessments)

        assert "success_probability" in result
        assert 0 <= result["success_probability"] <= 1
        assert "confidence" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_predict_activity_success_too_difficult(self, ml_service, sample_student):
        """Test success prediction for overly difficult activity."""
        # Student with lower independence
        assessments = []
        for i in range(5):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.MEDIUM
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "minimal"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        # Very difficult activity
        activity_data = {
            "difficulty": 9,
            "duration_minutes": 60,
            "activity_type": "cognitive",
            "has_adaptations": False,
            "has_visual_supports": False,
        }

        result = ml_service.predict_activity_success(sample_student, activity_data, assessments=assessments)

        # Should have lower success probability
        assert result["success_probability"] < 0.6
        # Should have recommendations
        assert len(result["recommendations"]) > 0
        # Should suggest simplification
        assert any("dificuldade" in rec.lower() or "simplificar" in rec.lower() for rec in result["recommendations"])

    def test_predict_activity_success_with_supports(self, ml_service, sample_student):
        """Test success prediction for activity with supports."""
        assessments = []

        activity_data = {
            "difficulty": 6,
            "duration_minutes": 30,
            "activity_type": "cognitive",
            "has_adaptations": True,
            "has_visual_supports": True,
        }

        result = ml_service.predict_activity_success(sample_student, activity_data, assessments=assessments)

        # Supports should increase success probability
        assert result["success_probability"] > 0.4


class TestProgressAnalysis:
    """Test student progress analysis."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    @pytest.fixture
    def sample_student(self):
        """Create sample student."""
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 10
        student.tea_level = TEALevel.LEVEL_1
        student.interests = ["matemática"]
        student.learning_profile = {}
        return student

    def test_analyze_student_progress_positive_trend(self, ml_service, sample_student):
        """Test progress analysis with positive trend."""
        # Create improving trend
        assessments = []
        engagement_levels = [
            EngagementLevel.LOW,
            EngagementLevel.LOW,
            EngagementLevel.MEDIUM,
            EngagementLevel.HIGH,
            EngagementLevel.HIGH,
            EngagementLevel.VERY_HIGH,
        ]

        for i, engagement in enumerate(engagement_levels):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = engagement
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "partial" if i < 3 else "full"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        result = ml_service.analyze_student_progress(sample_student, assessments)

        assert result["total_assessments"] == 6
        assert result["completion_rate"] == 1.0
        assert result["engagement_trend"] == "improving"
        assert "insights" in result
        assert len(result["insights"]) > 0

    def test_analyze_student_progress_declining_trend(self, ml_service, sample_student):
        """Test progress analysis with declining trend."""
        # Create declining trend
        assessments = []
        engagement_levels = [
            EngagementLevel.VERY_HIGH,
            EngagementLevel.HIGH,
            EngagementLevel.MEDIUM,
            EngagementLevel.LOW,
            EngagementLevel.LOW,
            EngagementLevel.NONE,
        ]

        for i, engagement in enumerate(engagement_levels):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED if i < 3 else CompletionStatus.ABANDONED
            assessment.engagement_level = engagement
            assessment.difficulty_rating = DifficultyRating.TOO_HARD
            assessment.independence_level = "full" if i < 2 else "dependent"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        result = ml_service.analyze_student_progress(sample_student, assessments)

        assert result["total_assessments"] == 6
        assert result["engagement_trend"] == "declining"
        # Should have warning insights
        assert any("⚠️" in insight for insight in result["insights"])

    def test_analyze_student_progress_insufficient_data(self, ml_service, sample_student):
        """Test progress analysis with no data."""
        result = ml_service.analyze_student_progress(sample_student, [])

        assert result["status"] == "insufficient_data"
        assert "message" in result

    def test_analyze_student_progress_stable_trend(self, ml_service, sample_student):
        """Test progress analysis with stable trend."""
        # Create stable performance
        assessments = []
        for i in range(6):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.MEDIUM
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessment.independence_level = "partial"
            assessment.created_at = datetime.now()
            assessments.append(assessment)

        result = ml_service.analyze_student_progress(sample_student, assessments)

        assert result["total_assessments"] == 6
        assert result["engagement_trend"] == "stable"
        assert result["completion_rate"] == 1.0


class TestInsightsGeneration:
    """Test insight generation from assessments."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    def test_generate_insights_high_completion(self, ml_service):
        """Test insights for high completion rate."""
        assessments = []
        for i in range(10):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.HIGH
            assessment.difficulty_rating = DifficultyRating.APPROPRIATE
            assessments.append(assessment)

        insights = ml_service._generate_progress_insights(assessments)

        assert len(insights) > 0
        assert any("excelente" in insight.lower() or "✅" in insight for insight in insights)

    def test_generate_insights_low_completion(self, ml_service):
        """Test insights for low completion rate."""
        assessments = []
        for i in range(10):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.ABANDONED if i < 7 else CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.LOW
            assessment.difficulty_rating = DifficultyRating.TOO_HARD
            assessments.append(assessment)

        insights = ml_service._generate_progress_insights(assessments)

        assert len(insights) > 0
        assert any("⚠️" in insight or "baixa" in insight.lower() for insight in insights)

    def test_generate_insights_difficulty_issues(self, ml_service):
        """Test insights for inappropriate difficulty."""
        assessments = []
        for i in range(10):
            assessment = Mock(spec=Assessment)
            assessment.completion_status = CompletionStatus.COMPLETED
            assessment.engagement_level = EngagementLevel.MEDIUM
            # Half too easy, half too hard
            assessment.difficulty_rating = DifficultyRating.TOO_EASY if i < 5 else DifficultyRating.TOO_HARD
            assessments.append(assessment)

        insights = ml_service._generate_progress_insights(assessments)

        assert len(insights) > 0
        assert any("dificuldade inadequada" in insight.lower() for insight in insights)


class TestRecommendations:
    """Test recommendation generation."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    def test_recommendations_low_success_probability(self, ml_service):
        """Test recommendations for low success probability."""
        features = {
            "activity_difficulty": 8.0,
            "avg_engagement": 1.5,
            "has_visual_supports": 0.0,
            "has_adaptations": 0.0,
            "attention_span": 3.0,
            "duration_minutes": 60.0,
        }

        recommendations = ml_service._generate_success_recommendations(features, success_prob=0.3)

        assert len(recommendations) > 0
        # Should suggest reducing difficulty
        assert any("dificuldade" in rec.lower() for rec in recommendations)
        # Should suggest adding supports
        assert any("visual" in rec.lower() or "adaptações" in rec.lower() for rec in recommendations)

    def test_recommendations_high_success_probability(self, ml_service):
        """Test recommendations for high success probability."""
        features = {
            "activity_difficulty": 4.0,
            "avg_engagement": 3.5,
            "avg_independence": 3.5,
            "has_visual_supports": 1.0,
            "has_adaptations": 1.0,
        }

        recommendations = ml_service._generate_success_recommendations(features, success_prob=0.8)

        assert len(recommendations) > 0
        # Should have positive feedback
        assert any("✅" in rec or "bem alinhada" in rec.lower() for rec in recommendations)

    def test_recommendations_duration_issues(self, ml_service):
        """Test recommendations for duration issues."""
        features = {"duration_minutes": 60.0, "attention_span": 2.0}

        recommendations = ml_service._generate_success_recommendations(features, success_prob=0.5)

        assert len(recommendations) > 0
        # Should suggest breaking into smaller sessions
        assert any("dividir" in rec.lower() or "sessões menores" in rec.lower() for rec in recommendations)


class TestModelLoading:
    """Test ML model loading."""

    @pytest.fixture
    def ml_service(self):
        """Create ML service instance."""
        return MLService()

    def test_load_behavioral_model_not_found(self, ml_service):
        """Test model loading when files don't exist."""
        result = ml_service.load_behavioral_model(version="nonexistent")

        # Should return False but not crash
        assert result is False
        assert ml_service.behavioral_model is None

    def test_load_behavioral_model_fallback(self, ml_service):
        """Test that service works without model (fallback to rules)."""
        # Don't load model
        student = Mock(spec=Student)
        student.id = uuid4()
        student.age = 10
        student.tea_level = TEALevel.LEVEL_1
        student.interests = []
        student.learning_profile = {}

        # Should still work with rule-based approach
        result = ml_service.predict_risk_level(student, assessments=[])

        assert result["method"] == "rule_based"
        assert result["risk_level"] in ml_service.RISK_LEVELS
