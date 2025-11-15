"""
Unit tests for activity and assessment schemas.

Tests Pydantic validation for activity and assessment schemas.
"""

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.activity import ActivityCreate
from app.schemas.assessment import AssessmentCreate
from app.utils.constants import MAX_NOTES_LENGTH


class TestActivitySchemas:
    """Tests for Activity schemas."""

    def test_activity_create_empty_objectives_raises_error(self):
        """Test that empty objectives list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ActivityCreate(
                student_id=uuid4(),
                title="Atividade Teste",
                description="Descrição da atividade",
                objectives=[],  # Empty list
                materials=["Material 1"],
                instructions=["Instrução 1"],
                estimated_duration=30,
            )

        errors = exc_info.value.errors()
        assert any("Lista não pode estar vazia" in str(error) for error in errors)

    def test_activity_create_empty_materials_raises_error(self):
        """Test that empty materials list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ActivityCreate(
                student_id=uuid4(),
                title="Atividade Teste",
                description="Descrição da atividade",
                objectives=["Objetivo 1"],
                materials=[],  # Empty list
                instructions=["Instrução 1"],
                estimated_duration=30,
            )

        errors = exc_info.value.errors()
        assert any("Lista não pode estar vazia" in str(error) for error in errors)

    def test_activity_create_empty_instructions_raises_error(self):
        """Test that empty instructions list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ActivityCreate(
                student_id=uuid4(),
                title="Atividade Teste",
                description="Descrição da atividade",
                objectives=["Objetivo 1"],
                materials=["Material 1"],
                instructions=[],  # Empty list
                estimated_duration=30,
            )

        errors = exc_info.value.errors()
        assert any("Lista não pode estar vazia" in str(error) for error in errors)

    def test_activity_create_whitespace_only_items_raises_error(self):
        """Test that lists with only whitespace items raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ActivityCreate(
                student_id=uuid4(),
                title="Atividade Teste",
                description="Descrição da atividade",
                objectives=["  ", "   "],  # Only whitespace
                materials=["Material 1"],
                instructions=["Instrução 1"],
                estimated_duration=30,
            )

        errors = exc_info.value.errors()
        assert any("Lista não pode estar vazia" in str(error) for error in errors)

    def test_activity_create_valid(self):
        """Test valid activity creation."""
        activity = ActivityCreate(
            student_id=uuid4(),
            title="Atividade Teste",
            description="Descrição da atividade",
            objectives=["Objetivo 1", "Objetivo 2"],
            materials=["Material 1", "Material 2"],
            instructions=["Instrução 1", "Instrução 2"],
            estimated_duration=45,
        )

        assert activity.title == "Atividade Teste"
        assert len(activity.objectives) == 2
        assert len(activity.materials) == 2
        assert len(activity.instructions) == 2


class TestAssessmentSchemas:
    """Tests for Assessment schemas."""

    def test_assessment_create_notes_too_long_raises_error(self):
        """Test that notes exceeding MAX_NOTES_LENGTH raise validation error."""
        long_text = "A" * (MAX_NOTES_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            AssessmentCreate(
                student_id=uuid4(),
                activity_id=uuid4(),
                date=date.today(),
                performance_level=3,
                engagement_level=4,
                notes=long_text,  # Exceeds MAX_NOTES_LENGTH
            )

        errors = exc_info.value.errors()
        assert any(f"Texto não pode exceder {MAX_NOTES_LENGTH}" in str(error) for error in errors)

    def test_assessment_create_strengths_too_long_raises_error(self):
        """Test that strengths exceeding MAX_NOTES_LENGTH raise validation error."""
        long_text = "B" * (MAX_NOTES_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            AssessmentCreate(
                student_id=uuid4(),
                activity_id=uuid4(),
                date=date.today(),
                performance_level=3,
                engagement_level=4,
                strengths_observed=long_text,  # Exceeds MAX_NOTES_LENGTH
            )

        errors = exc_info.value.errors()
        assert any(f"Texto não pode exceder {MAX_NOTES_LENGTH}" in str(error) for error in errors)

    def test_assessment_create_recommendations_too_long_raises_error(self):
        """Test that recommendations exceeding MAX_NOTES_LENGTH raise validation error."""
        long_text = "C" * (MAX_NOTES_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            AssessmentCreate(
                student_id=uuid4(),
                activity_id=uuid4(),
                date=date.today(),
                performance_level=3,
                engagement_level=4,
                recommendations=long_text,  # Exceeds MAX_NOTES_LENGTH
            )

        errors = exc_info.value.errors()
        assert any(f"Texto não pode exceder {MAX_NOTES_LENGTH}" in str(error) for error in errors)

    def test_assessment_create_valid(self):
        """Test valid assessment creation."""
        assessment = AssessmentCreate(
            student_id=uuid4(),
            activity_id=uuid4(),
            date=date.today(),
            performance_level=4,
            engagement_level=5,
            notes="Notas da avaliação",
            strengths_observed="Pontos fortes observados",
            challenges_observed="Desafios observados",
            recommendations="Recomendações para próximas atividades",
        )

        assert assessment.performance_level == 4
        assert assessment.engagement_level == 5
        assert len(assessment.notes) < MAX_NOTES_LENGTH
        assert len(assessment.strengths_observed) < MAX_NOTES_LENGTH

    def test_assessment_create_text_at_max_length(self):
        """Test assessment with text exactly at MAX_NOTES_LENGTH."""
        max_text = "D" * MAX_NOTES_LENGTH

        assessment = AssessmentCreate(
            student_id=uuid4(),
            activity_id=uuid4(),
            date=date.today(),
            performance_level=3,
            engagement_level=3,
            notes=max_text,  # Exactly at max length
        )

        assert len(assessment.notes) == MAX_NOTES_LENGTH
