"""
ML Service - EduAutismo IA

Machine Learning service for behavioral classification and predictive analytics.
Provides risk assessment, activity success prediction, and progress analysis.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.assessment import Assessment
from app.models.student import Student
from app.utils.constants import CompletionStatus, DifficultyRating, EngagementLevel, TEALevel
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MLService:
    """
    Machine Learning service for behavioral predictions.

    Provides:
    - Risk level classification (baixo, medio, alto, muito_alto)
    - Activity success prediction
    - Student progress analysis
    - Feature importance analysis
    """

    # Risk levels based on behavioral analysis
    RISK_LEVELS = ["baixo", "medio", "alto", "muito_alto"]

    # Independence levels
    INDEPENDENCE_LEVELS = {
        "full": 4,
        "partial": 3,
        "minimal": 2,
        "dependent": 1,
        None: 0,
    }

    def __init__(self):
        """Initialize ML Service."""
        self.behavioral_model: Optional[RandomForestClassifier] = None
        self.success_predictor: Optional[RandomForestClassifier] = None
        self.scaler: Optional[Any] = None
        self.feature_names: List[str] = []
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.model_path = Path(settings.ML_MODEL_PATH)

        logger.info(
            "ML Service initialized",
            extra={"model_path": str(self.model_path), "confidence_threshold": self.confidence_threshold},
        )

    # ========== Model Loading ==========

    def load_behavioral_model(self, version: str = "production") -> bool:
        """
        Load trained behavioral classification model.

        Args:
            version: Model version to load (default: production)

        Returns:
            True if loaded successfully

        Raises:
            FileNotFoundError: If model files not found
            ValidationError: If model validation fails
        """
        try:
            model_dir = self.model_path / "behavioral_classifier" / version

            # Load model
            model_file = model_dir / "model.pkl"
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")

            self.behavioral_model = joblib.load(model_file)
            logger.info(f"Loaded behavioral model from {model_file}")

            # Load scaler
            scaler_file = model_dir / "scaler.pkl"
            if scaler_file.exists():
                self.scaler = joblib.load(scaler_file)
                logger.info(f"Loaded scaler from {scaler_file}")

            # Load metadata
            metadata_file = model_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get("feature_names", [])
                    logger.info(f"Loaded {len(self.feature_names)} feature names")

            # Validate model
            if not hasattr(self.behavioral_model, "predict"):
                raise ValidationError("Loaded model is not a valid classifier")

            logger.info(f"Behavioral model loaded successfully: version={version}")
            return True

        except FileNotFoundError as e:
            logger.warning(f"Model files not found: {e}")
            logger.info("Model will use fallback rule-based classification")
            return False

        except Exception as e:
            logger.error(f"Error loading behavioral model: {e}")
            raise ValidationError(f"Failed to load model: {str(e)}")

    def load_success_predictor(self, version: str = "production") -> bool:
        """
        Load trained activity success prediction model.

        Args:
            version: Model version to load

        Returns:
            True if loaded successfully
        """
        try:
            model_dir = self.model_path / "success_predictor" / version
            model_file = model_dir / "model.pkl"

            if not model_file.exists():
                logger.warning(f"Success predictor not found: {model_file}")
                return False

            self.success_predictor = joblib.load(model_file)
            logger.info(f"Loaded success predictor from {model_file}")

            return True

        except Exception as e:
            logger.error(f"Error loading success predictor: {e}")
            return False

    # ========== Feature Extraction ==========

    def extract_student_features(self, student: Student, assessments: Optional[List[Assessment]] = None) -> Dict[str, float]:
        """
        Extract features from student profile and assessment history.

        Args:
            student: Student object
            assessments: Optional list of assessment history

        Returns:
            Dictionary of features for ML prediction
        """
        features = {}

        # Basic demographics
        features["age"] = float(student.age)

        # TEA level encoding
        tea_level_map = {
            TEALevel.LEVEL_1: 1.0,
            TEALevel.LEVEL_2: 2.0,
            TEALevel.LEVEL_3: 3.0,
            None: 0.0,
        }
        features["tea_level"] = tea_level_map.get(student.tea_level, 0.0)

        # Learning profile features
        if student.learning_profile:
            profile = student.learning_profile

            # Extract numeric features from learning profile
            for domain in ["visual", "auditory", "kinesthetic", "verbal", "logical", "social", "emotional"]:
                features[f"learning_{domain}"] = float(profile.get(domain, 0))

            # Additional profile features
            features["attention_span"] = float(profile.get("attention_span", 5))
            features["sensory_sensitivity"] = float(profile.get("sensory_sensitivity", 5))
            features["communication_level"] = float(profile.get("communication_level", 5))
            features["social_skills"] = float(profile.get("social_skills", 5))

        else:
            # Default values if no learning profile
            for domain in ["visual", "auditory", "kinesthetic", "verbal", "logical", "social", "emotional"]:
                features[f"learning_{domain}"] = 5.0

            features["attention_span"] = 5.0
            features["sensory_sensitivity"] = 5.0
            features["communication_level"] = 5.0
            features["social_skills"] = 5.0

        # Interest diversity
        features["interest_count"] = float(len(student.interests))

        # Assessment history features
        if assessments and len(assessments) > 0:
            # Completion rate
            completed = sum(1 for a in assessments if a.completion_status == CompletionStatus.COMPLETED)
            features["completion_rate"] = completed / len(assessments)

            # Average engagement
            engagement_map = {
                EngagementLevel.NONE: 0,
                EngagementLevel.LOW: 1,
                EngagementLevel.MEDIUM: 2,
                EngagementLevel.HIGH: 3,
                EngagementLevel.VERY_HIGH: 4,
            }
            engagement_scores = [engagement_map.get(a.engagement_level, 0) for a in assessments]
            features["avg_engagement"] = np.mean(engagement_scores)

            # Difficulty appropriateness
            difficulty_map = {
                DifficultyRating.TOO_EASY: -2,
                DifficultyRating.SLIGHTLY_EASY: -1,
                DifficultyRating.APPROPRIATE: 0,
                DifficultyRating.SLIGHTLY_HARD: 1,
                DifficultyRating.TOO_HARD: 2,
            }
            difficulty_scores = [difficulty_map.get(a.difficulty_rating, 0) for a in assessments]
            features["avg_difficulty_rating"] = np.mean(difficulty_scores)

            # Independence level
            independence_scores = [self.INDEPENDENCE_LEVELS.get(a.independence_level, 0) for a in assessments]
            features["avg_independence"] = np.mean(independence_scores) if independence_scores else 0.0

            # Success rate (completed with high engagement)
            success_count = sum(
                1
                for a in assessments
                if a.completion_status == CompletionStatus.COMPLETED
                and a.engagement_level in [EngagementLevel.HIGH, EngagementLevel.VERY_HIGH]
            )
            features["success_rate"] = success_count / len(assessments)

            # Recent trend (last 5 assessments)
            recent_assessments = sorted(assessments, key=lambda a: a.created_at, reverse=True)[:5]
            if len(recent_assessments) > 0:
                recent_completed = sum(1 for a in recent_assessments if a.completion_status == CompletionStatus.COMPLETED)
                features["recent_completion_rate"] = recent_completed / len(recent_assessments)
            else:
                features["recent_completion_rate"] = 0.0

        else:
            # Default values for students without assessment history
            features["completion_rate"] = 0.5
            features["avg_engagement"] = 2.0
            features["avg_difficulty_rating"] = 0.0
            features["avg_independence"] = 2.0
            features["success_rate"] = 0.5
            features["recent_completion_rate"] = 0.5

        logger.debug(f"Extracted {len(features)} features for student {student.id}")

        return features

    def extract_activity_features(self, activity_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from activity for success prediction.

        Args:
            activity_data: Dictionary with activity details

        Returns:
            Feature dictionary
        """
        features = {}

        # Activity difficulty
        features["activity_difficulty"] = float(activity_data.get("difficulty", 5))

        # Duration
        features["duration_minutes"] = float(activity_data.get("duration_minutes", 30))

        # Activity type encoding (one-hot style)
        activity_type = activity_data.get("activity_type", "")
        for activity_type_option in [
            "cognitive",
            "social",
            "motor",
            "sensory",
            "communication",
            "daily_living",
            "academic",
        ]:
            features[f"type_{activity_type_option}"] = 1.0 if activity_type == activity_type_option else 0.0

        # Has adaptations
        features["has_adaptations"] = 1.0 if activity_data.get("adaptations") else 0.0

        # Has visual supports
        features["has_visual_supports"] = 1.0 if activity_data.get("visual_supports") else 0.0

        return features

    # ========== Predictions ==========

    def predict_risk_level(self, student: Student, assessments: Optional[List[Assessment]] = None) -> Dict[str, Any]:
        """
        Predict behavioral risk level for student.

        Args:
            student: Student object
            assessments: Optional assessment history

        Returns:
            Dictionary with risk_level, confidence, and probabilities
        """
        try:
            # Extract features
            features = self.extract_student_features(student, assessments)

            # Use ML model if loaded
            if self.behavioral_model:
                return self._predict_with_model(features)
            else:
                # Fallback to rule-based classification
                return self._predict_rule_based(features)

        except Exception as e:
            logger.error(f"Error predicting risk level: {e}")
            # Return safe default
            return {"risk_level": "medio", "confidence": 0.5, "probabilities": {}, "method": "default"}

    def _predict_with_model(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict using trained ML model."""
        # Convert to DataFrame
        df = pd.DataFrame([features])

        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0.0

        # Select and order features
        X = df[self.feature_names]

        # Scale if scaler available
        if self.scaler:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X.values

        # Predict
        prediction_idx = self.behavioral_model.predict(X_scaled)[0]
        probabilities = self.behavioral_model.predict_proba(X_scaled)[0]

        # Get confidence (max probability)
        confidence = float(np.max(probabilities))

        # Build probability distribution
        prob_dist = {level: float(prob) for level, prob in zip(self.RISK_LEVELS, probabilities)}

        result = {
            "risk_level": self.RISK_LEVELS[prediction_idx],
            "confidence": confidence,
            "probabilities": prob_dist,
            "method": "ml_model",
        }

        logger.info(
            f"ML prediction: {result['risk_level']} (confidence: {confidence:.2f})",
            extra={"prediction": result},
        )

        return result

    def _predict_rule_based(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Fallback rule-based classification.

        Uses heuristics based on assessment performance and student profile.
        """
        # Calculate risk score (0-100)
        risk_score = 50.0  # Start at medium

        # Adjust based on completion rate
        completion_rate = features.get("completion_rate", 0.5)
        if completion_rate < 0.3:
            risk_score += 20
        elif completion_rate < 0.5:
            risk_score += 10
        elif completion_rate > 0.8:
            risk_score -= 10

        # Adjust based on engagement
        avg_engagement = features.get("avg_engagement", 2.0)
        if avg_engagement < 1.5:
            risk_score += 15
        elif avg_engagement > 3.0:
            risk_score -= 10

        # Adjust based on independence
        avg_independence = features.get("avg_independence", 2.0)
        if avg_independence < 1.5:
            risk_score += 10
        elif avg_independence > 3.0:
            risk_score -= 10

        # Adjust based on success rate
        success_rate = features.get("success_rate", 0.5)
        if success_rate < 0.2:
            risk_score += 15
        elif success_rate > 0.7:
            risk_score -= 15

        # Adjust based on TEA level
        tea_level = features.get("tea_level", 0.0)
        if tea_level == 3.0:  # Level 3 - highest support needs
            risk_score += 10
        elif tea_level == 1.0:  # Level 1 - lower support needs
            risk_score -= 5

        # Cap between 0 and 100
        risk_score = max(0, min(100, risk_score))

        # Map to risk level
        if risk_score < 25:
            risk_level = "baixo"
        elif risk_score < 50:
            risk_level = "medio"
        elif risk_score < 75:
            risk_level = "alto"
        else:
            risk_level = "muito_alto"

        # Calculate confidence based on data availability
        data_points = len([v for v in features.values() if v != 0])
        confidence = min(0.7, 0.4 + (data_points / 40))  # Max 0.7 for rule-based

        result = {
            "risk_level": risk_level,
            "confidence": float(confidence),
            "risk_score": float(risk_score),
            "method": "rule_based",
        }

        logger.info(
            f"Rule-based prediction: {risk_level} (score: {risk_score:.1f})",
            extra={"prediction": result},
        )

        return result

    def predict_activity_success(
        self, student: Student, activity_data: Dict[str, Any], assessments: Optional[List[Assessment]] = None
    ) -> Dict[str, Any]:
        """
        Predict likelihood of activity success.

        Args:
            student: Student object
            activity_data: Activity details
            assessments: Assessment history

        Returns:
            Dictionary with success_probability and recommendations
        """
        try:
            # Extract features
            student_features = self.extract_student_features(student, assessments)
            activity_features = self.extract_activity_features(activity_data)

            # Combine features
            combined_features = {**student_features, **activity_features}

            # Use ML model if available
            if self.success_predictor:
                # Convert to DataFrame
                df = pd.DataFrame([combined_features])
                X = df.values

                # Predict probability
                success_prob = float(self.success_predictor.predict_proba(X)[0][1])

            else:
                # Rule-based estimation
                success_prob = self._estimate_success_probability(student_features, activity_features)

            # Generate recommendations
            recommendations = self._generate_success_recommendations(combined_features, success_prob)

            result = {
                "success_probability": success_prob,
                "confidence": "high" if success_prob > 0.7 or success_prob < 0.3 else "medium",
                "recommendations": recommendations,
            }

            logger.info(f"Activity success prediction: {success_prob:.2f}", extra={"prediction": result})

            return result

        except Exception as e:
            logger.error(f"Error predicting activity success: {e}")
            return {
                "success_probability": 0.5,
                "confidence": "low",
                "recommendations": ["Monitorar engajamento durante a atividade"],
            }

    def _estimate_success_probability(self, student_features: Dict[str, float], activity_features: Dict[str, float]) -> float:
        """Estimate success probability using rules."""
        base_prob = 0.5

        # Adjust based on completion rate
        completion_rate = student_features.get("completion_rate", 0.5)
        base_prob += (completion_rate - 0.5) * 0.3

        # Adjust based on engagement
        avg_engagement = student_features.get("avg_engagement", 2.0)
        base_prob += (avg_engagement - 2.0) / 4.0 * 0.2

        # Adjust based on activity difficulty vs student performance
        activity_difficulty = activity_features.get("activity_difficulty", 5)
        avg_independence = student_features.get("avg_independence", 2.0)

        # Difficulty alignment
        if activity_difficulty > 7 and avg_independence < 2:
            base_prob -= 0.15  # Too hard
        elif activity_difficulty < 3 and avg_independence > 3:
            base_prob += 0.05  # May be too easy but likely to complete

        # Has supports
        if activity_features.get("has_visual_supports", 0) > 0:
            base_prob += 0.05
        if activity_features.get("has_adaptations", 0) > 0:
            base_prob += 0.05

        # Cap between 0 and 1
        return max(0.0, min(1.0, base_prob))

    def _generate_success_recommendations(self, features: Dict[str, float], success_prob: float) -> List[str]:
        """Generate recommendations to improve success probability."""
        recommendations = []

        if success_prob < 0.4:
            recommendations.append("  Atividade pode ser desafiadora - considere simplificar")

            # Check difficulty
            if features.get("activity_difficulty", 5) > 6:
                recommendations.append("Reduza o nível de dificuldade da atividade")

            # Check supports
            if not features.get("has_visual_supports"):
                recommendations.append("Adicione suportes visuais para facilitar compreensão")

            if not features.get("has_adaptations"):
                recommendations.append("Inclua adaptações baseadas no perfil do aluno")

            # Check student performance
            if features.get("avg_engagement", 2) < 2:
                recommendations.append("Incorpore interesses especiais do aluno para aumentar engajamento")

        elif success_prob > 0.7:
            recommendations.append(" Atividade bem alinhada com perfil do aluno")

            # Check if may be too easy
            if features.get("avg_independence", 2) > 3 and features.get("activity_difficulty", 5) < 4:
                recommendations.append("Considere aumentar complexidade para desafio apropriado")

        else:
            recommendations.append("Atividade adequada - monitore progresso")

        # Duration recommendations
        duration = features.get("duration_minutes", 30)
        attention_span = features.get("attention_span", 5)

        if duration > 45 and attention_span < 3:
            recommendations.append("Considere dividir atividade em sessões menores")

        return recommendations

    # ========== Analysis Methods ==========

    def analyze_student_progress(
        self, student: Student, assessments: List[Assessment], time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze student progress over time.

        Args:
            student: Student object
            assessments: Assessment history
            time_window_days: Analysis window in days

        Returns:
            Progress analysis with trends and insights
        """
        if not assessments:
            return {
                "status": "insufficient_data",
                "message": "Não há avaliações suficientes para análise",
            }

        # Sort by date
        sorted_assessments = sorted(assessments, key=lambda a: a.created_at)

        # Calculate metrics
        total = len(sorted_assessments)
        completed = sum(1 for a in sorted_assessments if a.completion_status == CompletionStatus.COMPLETED)

        # Engagement trend
        engagement_map = {
            EngagementLevel.NONE: 0,
            EngagementLevel.LOW: 1,
            EngagementLevel.MEDIUM: 2,
            EngagementLevel.HIGH: 3,
            EngagementLevel.VERY_HIGH: 4,
        }
        engagement_scores = [engagement_map.get(a.engagement_level, 0) for a in sorted_assessments]

        # Calculate trend (simple linear regression)
        if len(engagement_scores) > 1:
            x = np.arange(len(engagement_scores))
            trend_slope = np.polyfit(x, engagement_scores, 1)[0]
            engagement_trend = "improving" if trend_slope > 0.1 else "declining" if trend_slope < -0.1 else "stable"
        else:
            engagement_trend = "insufficient_data"
            trend_slope = 0

        # Independence progression
        recent_assessments = sorted_assessments[-5:] if len(sorted_assessments) >= 5 else sorted_assessments
        independence_scores = [self.INDEPENDENCE_LEVELS.get(a.independence_level, 0) for a in recent_assessments]
        avg_recent_independence = np.mean(independence_scores) if independence_scores else 0

        # Success rate
        success_count = sum(
            1
            for a in sorted_assessments
            if a.completion_status == CompletionStatus.COMPLETED
            and a.engagement_level in [EngagementLevel.HIGH, EngagementLevel.VERY_HIGH]
        )

        analysis = {
            "total_assessments": total,
            "completion_rate": completed / total if total > 0 else 0,
            "success_rate": success_count / total if total > 0 else 0,
            "avg_engagement": float(np.mean(engagement_scores)),
            "engagement_trend": engagement_trend,
            "trend_slope": float(trend_slope),
            "avg_recent_independence": float(avg_recent_independence),
            "insights": self._generate_progress_insights(sorted_assessments),
        }

        logger.info(f"Progress analysis completed for student {student.id}", extra={"analysis": analysis})

        return analysis

    def _generate_progress_insights(self, assessments: List[Assessment]) -> List[str]:
        """Generate insights from assessment history."""
        insights = []

        if not assessments:
            return ["Não há dados suficientes para gerar insights"]

        # Check completion rate
        completed = sum(1 for a in assessments if a.completion_status == CompletionStatus.COMPLETED)
        completion_rate = completed / len(assessments)

        if completion_rate > 0.8:
            insights.append(" Excelente taxa de conclusão de atividades")
        elif completion_rate < 0.4:
            insights.append("  Baixa taxa de conclusão - considere ajustar dificuldade")

        # Check difficulty appropriateness
        difficulty_issues = sum(
            1
            for a in assessments
            if a.difficulty_rating in [DifficultyRating.TOO_EASY, DifficultyRating.TOO_HARD]
        )
        if difficulty_issues > len(assessments) * 0.4:
            insights.append("  Muitas atividades com dificuldade inadequada - revisar seleção")

        # Recent performance
        recent = assessments[-5:] if len(assessments) >= 5 else assessments
        recent_completed = sum(1 for a in recent if a.completion_status == CompletionStatus.COMPLETED)

        if recent_completed == len(recent):
            insights.append("<¯ Todas as atividades recentes foram concluídas")
        elif recent_completed == 0:
            insights.append("  Nenhuma atividade recente foi concluída - necessário suporte adicional")

        return insights if insights else ["Progresso dentro do esperado"]

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from trained model.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.behavioral_model or not hasattr(self.behavioral_model, "feature_importances_"):
            logger.warning("Model not loaded or doesn't support feature importance")
            return {}

        importance = dict(zip(self.feature_names, self.behavioral_model.feature_importances_))

        # Sort by importance
        sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return sorted_importance


# ========== Singleton Instance ==========

_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """
    Get singleton instance of ML Service.

    Returns:
        MLService instance
    """
    global _ml_service

    if _ml_service is None:
        _ml_service = MLService()

        # Try to load models
        try:
            _ml_service.load_behavioral_model()
        except Exception as e:
            logger.warning(f"Could not load behavioral model: {e}")
            logger.info("ML Service will use rule-based classification")

        try:
            _ml_service.load_success_predictor()
        except Exception as e:
            logger.warning(f"Could not load success predictor: {e}")

    return _ml_service
