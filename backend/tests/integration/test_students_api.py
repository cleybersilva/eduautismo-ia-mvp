"""
Integration tests for students API.
"""

import pytest
from fastapi.testclient import TestClient


class TestStudentsAPI:
    """Test class for students API endpoints."""

    def test_create_student_success(self, client, auth_headers):
        """Test successful student creation."""
        response = client.post(
            "/api/v1/students/",
            headers=auth_headers,
            json={
                "name": "Maria Silva",
                "date_of_birth": "2014-03-20",
                "diagnosis": "Transtorno do Espectro Autista - Nível 2",
                "tea_level": "level_2",
                "interests": ["música", "arte"],
                "learning_profile": {"visual_learner": True, "auditory_sensitivity": "high"},
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Maria Silva"
        assert data["tea_level"] == "level_2"
        assert data["age"] == 11
        assert "id" in data
        assert "teacher_id" in data

    def test_create_student_without_auth(self, client):
        """Test creating student without authentication fails."""
        response = client.post(
            "/api/v1/students/",
            json={
                "name": "Test Student",
                "date_of_birth": "2015-01-01",
                "diagnosis": "TEA Nível 1",
                "tea_level": "level_1",
            },
        )

        assert response.status_code == 403

    def test_create_student_invalid_date(self, client, auth_headers):
        """Test creating student with invalid birth date."""
        response = client.post(
            "/api/v1/students/",
            headers=auth_headers,
            json={
                "name": "Invalid Student",
                "date_of_birth": "2025-01-01",  # Future date
                "diagnosis": "TEA",
                "tea_level": "level_1",
            },
        )

        assert response.status_code == 422

    def test_create_student_too_young(self, client, auth_headers):
        """Test creating student below minimum age."""
        response = client.post(
            "/api/v1/students/",
            headers=auth_headers,
            json={
                "name": "Too Young",
                "date_of_birth": "2024-06-01",  # Less than 2 years old (1.5 years)
                "diagnosis": "TEA",
                "tea_level": "level_1",
            },
        )

        # Should return 422 (Validation Error) because age < MIN_STUDENT_AGE (2 years)
        assert response.status_code == 422
