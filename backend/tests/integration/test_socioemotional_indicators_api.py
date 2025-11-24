"""
Integration tests for Socioemotional Indicator API endpoints.

Tests CRUD operations and analysis for socioemotional indicators.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status
from uuid import uuid4

from app.models.socioemotional_indicator import IndicatorType, MeasurementContext
from app.models.professional import ProfessionalRole


@pytest.fixture
def psychologist(client, auth_headers):
    """Create a psychologist for testing."""
    data = {
        "name": "Dr. Maria Psicologia",
        "email": f"maria.psi.{uuid4().hex[:8]}@example.com",
        "role": ProfessionalRole.PSYCHOLOGIST.value,
        "organization": "Clínica Saúde",
    }
    response = client.post("/api/v1/professionals/", json=data, headers=auth_headers)
    return response.json()


@pytest.fixture
def test_student(client, auth_headers):
    """Create a test student."""
    data = {
        "name": "João Silva",
        "date_of_birth": "2015-03-15",
        "age": 9,
        "diagnosis": "TEA Nível 1",
        "interests": ["dinossauros", "lego"],
    }
    response = client.post("/api/v1/students/", json=data, headers=auth_headers)
    return response.json()


@pytest.fixture
def indicator_data(test_student, psychologist):
    """Sample indicator data."""
    return {
        "student_id": test_student["id"],
        "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
        "context": MeasurementContext.CLASSROOM.value,
        "score": 6,
        "observations": "Estudante demonstrou boa capacidade de autorregulação durante atividade em grupo",
        "specific_behaviors": "Utilizou técnicas de respiração quando frustrado",
        "environmental_factors": "Sala com iluminação natural, ambiente tranquilo",
        "triggers": "Nenhum gatilho identificado",
        "supports_used": "Apoio verbal do professor",
        "measured_at": datetime.now().isoformat(),
    }


@pytest.fixture
def indicator_headers(auth_headers, psychologist):
    """Auth headers with Professional ID."""
    headers = auth_headers.copy()
    headers["X-Professional-ID"] = psychologist["id"]
    return headers


class TestIndicatorCreate:
    """Tests for POST /api/v1/socioemotional-indicators/"""

    def test_create_indicator_success(self, client, indicator_headers, indicator_data):
        """Test successful indicator creation."""
        response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=indicator_data,
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["indicator_type"] == indicator_data["indicator_type"]
        assert data["score"] == indicator_data["score"]
        assert "id" in data
        assert "created_at" in data

    def test_create_indicator_invalid_score_fails(self, client, indicator_headers, indicator_data):
        """Test that invalid score is rejected."""
        bad_data = indicator_data.copy()
        bad_data["score"] = 15  # Score should be 0-10

        response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=bad_data,
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_indicator_nonexistent_student_fails(self, client, indicator_headers, indicator_data):
        """Test that indicator for nonexistent student is rejected."""
        bad_data = indicator_data.copy()
        bad_data["student_id"] = str(uuid4())

        response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=bad_data,
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIndicatorBulkCreate:
    """Tests for POST /api/v1/socioemotional-indicators/bulk"""

    def test_bulk_create_success(self, client, indicator_headers, test_student, psychologist):
        """Test successful bulk indicator creation."""
        bulk_data = {
            "student_id": test_student["id"],
            "measured_at": datetime.now().isoformat(),
            "indicators": [
                {
                    "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
                    "context": MeasurementContext.CLASSROOM.value,
                    "score": 6,
                },
                {
                    "indicator_type": IndicatorType.SOCIAL_INTERACTION.value,
                    "context": MeasurementContext.CLASSROOM.value,
                    "score": 7,
                },
                {
                    "indicator_type": IndicatorType.ATTENTION_FOCUS.value,
                    "context": MeasurementContext.CLASSROOM.value,
                    "score": 5,
                },
            ],
        }

        response = client.post(
            "/api/v1/socioemotional-indicators/bulk",
            json=bulk_data,
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["created_count"] == 3
        assert data["failed_count"] == 0
        assert len(data["created_ids"]) == 3


class TestIndicatorGet:
    """Tests for GET /api/v1/socioemotional-indicators/{indicator_id}"""

    def test_get_indicator_success(self, client, indicator_headers, indicator_data):
        """Test successful indicator retrieval."""
        # Create indicator
        create_response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=indicator_data,
            headers=indicator_headers,
        )
        indicator_id = create_response.json()["id"]

        # Get indicator
        response = client.get(
            f"/api/v1/socioemotional-indicators/{indicator_id}",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == indicator_id
        assert data["score"] == indicator_data["score"]


class TestIndicatorUpdate:
    """Tests for PUT /api/v1/socioemotional-indicators/{indicator_id}"""

    def test_update_indicator_success(self, client, indicator_headers, indicator_data, psychologist):
        """Test successful indicator update."""
        # Create indicator
        create_response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=indicator_data,
            headers=indicator_headers,
        )
        indicator_id = create_response.json()["id"]

        # Update indicator
        update_data = {
            "score": 8,
            "observations": "Progresso significativo observado",
        }
        response = client.put(
            f"/api/v1/socioemotional-indicators/{indicator_id}",
            json=update_data,
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == 8
        assert "Progresso" in data["observations"]


class TestIndicatorDelete:
    """Tests for DELETE /api/v1/socioemotional-indicators/{indicator_id}"""

    def test_delete_indicator_success(self, client, indicator_headers, indicator_data, psychologist):
        """Test successful indicator deletion."""
        # Create indicator
        create_response = client.post(
            "/api/v1/socioemotional-indicators/",
            json=indicator_data,
            headers=indicator_headers,
        )
        indicator_id = create_response.json()["id"]

        # Delete indicator
        response = client.delete(
            f"/api/v1/socioemotional-indicators/{indicator_id}",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/api/v1/socioemotional-indicators/{indicator_id}",
            headers=indicator_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestIndicatorList:
    """Tests for GET /api/v1/socioemotional-indicators/"""

    def test_list_indicators_success(self, client, indicator_headers, test_student, psychologist):
        """Test successful indicator listing."""
        # Create multiple indicators
        for i in range(3):
            indicator = {
                "student_id": test_student["id"],
                "professional_id": psychologist["id"],
                "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
                "context": MeasurementContext.CLASSROOM.value,
                "score": 5 + i,
                "measured_at": datetime.now().isoformat(),
            }
            client.post("/api/v1/socioemotional-indicators/", json=indicator, headers=indicator_headers)

        # List indicators
        response = client.get(
            "/api/v1/socioemotional-indicators/",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "indicators" in data
        assert "total" in data
        assert data["total"] >= 3

    def test_list_indicators_filter_by_student(self, client, indicator_headers, test_student, psychologist):
        """Test filtering indicators by student."""
        # Create indicator
        indicator = {
            "student_id": test_student["id"],
            "indicator_type": IndicatorType.SOCIAL_INTERACTION.value,
            "context": MeasurementContext.CLASSROOM.value,
            "score": 7,
            "measured_at": datetime.now().isoformat(),
        }
        client.post("/api/v1/socioemotional-indicators/", json=indicator, headers=indicator_headers)

        # Filter by student
        response = client.get(
            f"/api/v1/socioemotional-indicators/?student_id={test_student['id']}",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for ind in data["indicators"]:
            assert ind["student_id"] == test_student["id"]

    def test_list_indicators_filter_by_type(self, client, indicator_headers, indicator_data):
        """Test filtering indicators by type."""
        # Create indicator
        client.post("/api/v1/socioemotional-indicators/", json=indicator_data, headers=indicator_headers)

        # Filter by type
        response = client.get(
            f"/api/v1/socioemotional-indicators/?indicator_type={IndicatorType.EMOTIONAL_REGULATION.value}",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for ind in data["indicators"]:
            assert ind["indicator_type"] == IndicatorType.EMOTIONAL_REGULATION.value

    def test_list_indicators_filter_concerning_only(self, client, indicator_headers, test_student, psychologist):
        """Test filtering only concerning indicators."""
        # Create indicators with low scores (concerning for positive indicators)
        indicators = [
            {
                "student_id": test_student["id"],
                "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
                "context": MeasurementContext.CLASSROOM.value,
                "score": 3,  # Low score is concerning
                "measured_at": datetime.now().isoformat(),
            },
            {
                "student_id": test_student["id"],
                "indicator_type": IndicatorType.ANXIETY_LEVEL.value,
                "context": MeasurementContext.CLASSROOM.value,
                "score": 8,  # High anxiety is concerning
                "measured_at": datetime.now().isoformat(),
            },
        ]

        for ind in indicators:
            client.post("/api/v1/socioemotional-indicators/", json=ind, headers=indicator_headers)

        # Filter concerning only
        response = client.get(
            f"/api/v1/socioemotional-indicators/?student_id={test_student['id']}&concerning_only=true",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Both should be marked as concerning
        assert data["total"] >= 2


class TestIndicatorTrend:
    """Tests for GET /api/v1/socioemotional-indicators/student/{student_id}/trend"""

    def test_get_trend_success(self, client, indicator_headers, test_student, psychologist):
        """Test successful trend analysis."""
        # Create indicators over time
        base_time = datetime.now()
        for i in range(5):
            indicator = {
                "student_id": test_student["id"],
                "professional_id": psychologist["id"],
                "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
                "context": MeasurementContext.CLASSROOM.value,
                "score": 5 + i,  # Increasing trend
                "measured_at": (base_time - timedelta(days=4-i)).isoformat(),
            }
            client.post("/api/v1/socioemotional-indicators/", json=indicator, headers=indicator_headers)

        # Get trend
        response = client.get(
            f"/api/v1/socioemotional-indicators/student/{test_student['id']}/trend?indicator_type={IndicatorType.EMOTIONAL_REGULATION.value}&days=7",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["indicator_type"] == IndicatorType.EMOTIONAL_REGULATION.value
        assert "trend_direction" in data
        assert "measurements" in data
        assert len(data["measurements"]) >= 5


class TestIndicatorProfile:
    """Tests for GET /api/v1/socioemotional-indicators/student/{student_id}/profile"""

    def test_get_profile_success(self, client, indicator_headers, test_student, psychologist):
        """Test successful profile generation."""
        # Create indicators for multiple types
        indicator_types = [
            IndicatorType.EMOTIONAL_REGULATION,
            IndicatorType.SOCIAL_INTERACTION,
            IndicatorType.ATTENTION_FOCUS,
            IndicatorType.ANXIETY_LEVEL,
        ]

        for ind_type in indicator_types:
            indicator = {
                "student_id": test_student["id"],
                "professional_id": psychologist["id"],
                "indicator_type": ind_type.value,
                "context": MeasurementContext.CLASSROOM.value,
                "score": 6,
                "measured_at": datetime.now().isoformat(),
            }
            client.post("/api/v1/socioemotional-indicators/", json=indicator, headers=indicator_headers)

        # Get profile
        response = client.get(
            f"/api/v1/socioemotional-indicators/student/{test_student['id']}/profile",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "student_id" in data
        assert "indicators_summary" in data
        assert len(data["indicators_summary"]) >= 4
        assert "strengths" in data
        assert "concerning_indicators" in data


class TestIndicatorComparison:
    """Tests for GET /api/v1/socioemotional-indicators/student/{student_id}/compare"""

    def test_compare_periods_success(self, client, indicator_headers, test_student, psychologist):
        """Test successful period comparison."""
        # Create indicators for two periods
        now = datetime.now()

        # Period 1 (30 days ago)
        indicator1 = {
            "student_id": test_student["id"],
            "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
            "context": MeasurementContext.CLASSROOM.value,
            "score": 5,
            "measured_at": (now - timedelta(days=30)).isoformat(),
        }

        # Period 2 (now)
        indicator2 = {
            "student_id": test_student["id"],
            "indicator_type": IndicatorType.EMOTIONAL_REGULATION.value,
            "context": MeasurementContext.CLASSROOM.value,
            "score": 7,
            "measured_at": now.isoformat(),
        }

        client.post("/api/v1/socioemotional-indicators/", json=indicator1, headers=indicator_headers)
        client.post("/api/v1/socioemotional-indicators/", json=indicator2, headers=indicator_headers)

        # Compare periods
        start1 = (now - timedelta(days=35)).isoformat()
        end1 = (now - timedelta(days=25)).isoformat()
        start2 = (now - timedelta(days=5)).isoformat()
        end2 = now.isoformat()

        response = client.get(
            f"/api/v1/socioemotional-indicators/student/{test_student['id']}/compare?"
            f"indicator_type={IndicatorType.EMOTIONAL_REGULATION.value}&"
            f"period1_start={start1}&period1_end={end1}&period2_start={start2}&period2_end={end2}",
            headers=indicator_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "period1_average" in data
        assert "period2_average" in data
        assert "change_direction" in data
        assert "change_percentage" in data
