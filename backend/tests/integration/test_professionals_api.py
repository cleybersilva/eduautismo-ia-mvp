"""
Integration tests for Professional API endpoints.

Tests CRUD operations and filtering for professionals.
"""

import pytest
from fastapi import status
from uuid import uuid4

from app.models.professional import ProfessionalRole


@pytest.fixture
def professional_data():
    """Sample professional data for testing."""
    return {
        "name": "Dr. Ana Silva",
        "email": f"ana.silva.{uuid4().hex[:8]}@example.com",
        "role": ProfessionalRole.PSYCHOLOGIST.value,
        "specialization": "Psicologia Clínica",
        "license_number": "CRP-01/12345",
        "organization": "Clínica Vida",
        "phone": "(11) 98765-4321",
    }


@pytest.fixture
def teacher_data():
    """Sample teacher data for testing."""
    return {
        "name": "Prof. Carlos Santos",
        "email": f"carlos.santos.{uuid4().hex[:8]}@example.com",
        "role": ProfessionalRole.TEACHER.value,
        "organization": "Escola Municipal ABC",
        "phone": "(11) 91234-5678",
    }


class TestProfessionalCreate:
    """Tests for POST /api/v1/professionals/"""

    def test_create_professional_success(self, client, auth_headers, professional_data):
        """Test successful professional creation."""
        response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == professional_data["name"]
        assert data["email"] == professional_data["email"]
        assert data["role"] == professional_data["role"]
        assert "id" in data
        assert "created_at" in data

    def test_create_professional_duplicate_email_fails(self, client, auth_headers, professional_data):
        """Test that duplicate email is rejected."""
        # Create first professional
        response1 = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create with same email
        response2 = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "já está cadastrado" in response2.json()["detail"]

    def test_create_professional_without_auth_fails(self, client, professional_data):
        """Test that unauthenticated request is rejected."""
        response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
        )
        # FastAPI HTTPBearer returns 403 when no auth is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProfessionalGet:
    """Tests for GET /api/v1/professionals/{professional_id}"""

    def test_get_professional_success(self, client, auth_headers, professional_data):
        """Test successful professional retrieval."""
        # Create professional
        create_response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        professional_id = create_response.json()["id"]

        # Get professional
        response = client.get(
            f"/api/v1/professionals/{professional_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == professional_id
        assert data["name"] == professional_data["name"]

    def test_get_nonexistent_professional_fails(self, client, auth_headers):
        """Test that getting nonexistent professional returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/professionals/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProfessionalUpdate:
    """Tests for PUT /api/v1/professionals/{professional_id}"""

    def test_update_professional_success(self, client, auth_headers, professional_data):
        """Test successful professional update."""
        # Create professional
        create_response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        professional_id = create_response.json()["id"]

        # Update professional
        update_data = {
            "name": "Dr. Ana Maria Silva",
            "phone": "(11) 99999-9999",
        }
        response = client.put(
            f"/api/v1/professionals/{professional_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["phone"] == update_data["phone"]
        assert data["email"] == professional_data["email"]  # Unchanged

    def test_update_professional_email_conflict_fails(self, client, auth_headers, professional_data, teacher_data):
        """Test that updating to existing email is rejected."""
        # Create two professionals
        response1 = client.post("/api/v1/professionals/", json=professional_data, headers=auth_headers)
        professional_id = response1.json()["id"]

        response2 = client.post("/api/v1/professionals/", json=teacher_data, headers=auth_headers)
        existing_email = response2.json()["email"]

        # Try to update first professional with second's email
        response = client.put(
            f"/api/v1/professionals/{professional_id}",
            json={"email": existing_email},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProfessionalDelete:
    """Tests for DELETE /api/v1/professionals/{professional_id}"""

    def test_delete_professional_success(self, client, auth_headers, professional_data):
        """Test successful professional deletion (soft delete)."""
        # Create professional
        create_response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        professional_id = create_response.json()["id"]

        # Delete professional
        response = client.delete(
            f"/api/v1/professionals/{professional_id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify professional is marked as inactive
        get_response = client.get(
            f"/api/v1/professionals/{professional_id}",
            headers=auth_headers,
        )
        assert get_response.json()["is_active"] is False


class TestProfessionalList:
    """Tests for GET /api/v1/professionals/"""

    def test_list_professionals_success(self, client, auth_headers, professional_data, teacher_data):
        """Test successful professional listing."""
        # Create two professionals
        client.post("/api/v1/professionals/", json=professional_data, headers=auth_headers)
        client.post("/api/v1/professionals/", json=teacher_data, headers=auth_headers)

        # List professionals
        response = client.get(
            "/api/v1/professionals/",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "professionals" in data
        assert "total" in data
        assert len(data["professionals"]) >= 2

    def test_list_professionals_filter_by_role(self, client, auth_headers, professional_data, teacher_data):
        """Test filtering professionals by role."""
        # Create professionals
        client.post("/api/v1/professionals/", json=professional_data, headers=auth_headers)
        client.post("/api/v1/professionals/", json=teacher_data, headers=auth_headers)

        # Filter by teacher role
        response = client.get(
            f"/api/v1/professionals/?role={ProfessionalRole.TEACHER.value}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for prof in data["professionals"]:
            assert prof["role"] == ProfessionalRole.TEACHER.value

    def test_list_professionals_search(self, client, auth_headers, professional_data):
        """Test searching professionals by name or email."""
        # Create professional
        create_response = client.post(
            "/api/v1/professionals/",
            json=professional_data,
            headers=auth_headers,
        )
        name = professional_data["name"].split()[0]  # First word of name

        # Search by name
        response = client.get(
            f"/api/v1/professionals/?search={name}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any(name.lower() in prof["name"].lower() for prof in data["professionals"])

    def test_list_professionals_pagination(self, client, auth_headers, professional_data):
        """Test professional list pagination."""
        # Create multiple professionals
        for i in range(5):
            data = professional_data.copy()
            data["email"] = f"professional{i}@example.com"
            data["name"] = f"Professional {i}"
            client.post("/api/v1/professionals/", json=data, headers=auth_headers)

        # Get first page
        response = client.get(
            "/api/v1/professionals/?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["professionals"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] >= 5

    def test_list_education_professionals_only(self, client, auth_headers, professional_data, teacher_data):
        """Test filtering only education professionals."""
        # Create professionals
        client.post("/api/v1/professionals/", json=professional_data, headers=auth_headers)  # Health
        client.post("/api/v1/professionals/", json=teacher_data, headers=auth_headers)  # Education

        # Filter education only
        response = client.get(
            "/api/v1/professionals/?is_education=true",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for prof in data["professionals"]:
            assert prof["role"] in [
                ProfessionalRole.TEACHER.value,
                ProfessionalRole.SPECIAL_EDUCATOR.value,
                ProfessionalRole.SCHOOL_COORDINATOR.value,
                ProfessionalRole.SCHOOL_MANAGER.value,
                ProfessionalRole.PSYCHOPEDAGOGIST.value,
            ]


class TestProfessionalStatistics:
    """Tests for GET /api/v1/professionals/statistics/overview"""

    def test_get_statistics_success(self, client, auth_headers, professional_data, teacher_data):
        """Test successful statistics retrieval."""
        # Create professionals
        client.post("/api/v1/professionals/", json=professional_data, headers=auth_headers)
        client.post("/api/v1/professionals/", json=teacher_data, headers=auth_headers)

        # Get statistics
        response = client.get(
            "/api/v1/professionals/statistics/overview",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_professionals" in data
        assert "total_active" in data
        assert "by_role" in data
        assert "education_professionals" in data
        assert "health_professionals" in data
        assert data["total_professionals"] >= 2
