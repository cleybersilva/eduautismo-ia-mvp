"""
Integration tests for Intervention Plan API endpoints.

Tests CRUD operations for multiprofessional intervention plans.
"""

import pytest
from datetime import date, timedelta
from fastapi import status
from uuid import uuid4

from app.models.intervention_plan import PlanStatus, ReviewFrequency
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
def speech_therapist(client, auth_headers):
    """Create a speech therapist for testing."""
    data = {
        "name": "Dra. Ana Fono",
        "email": f"ana.fono.{uuid4().hex[:8]}@example.com",
        "role": ProfessionalRole.SPEECH_THERAPIST.value,
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
def intervention_plan_data(test_student, psychologist):
    """Sample intervention plan data."""
    start = date.today()
    end = start + timedelta(days=90)

    return {
        "student_id": test_student["id"],
        "title": "Plano de Desenvolvimento Socioemocional",
        "objective": "Melhorar habilidades de comunicação social e autorregulação emocional",
        "description": "Plano focado em desenvolvimento de competências socioemocionais",
        "strategies": [
            {
                "name": "Exercícios de respiração",
                "frequency": "3x por semana",
                "duration": "15 minutos",
            },
            {
                "name": "Jogos cooperativos",
                "frequency": "2x por semana",
                "duration": "30 minutos",
            },
        ],
        "target_behaviors": [
            "Iniciar interações sociais adequadas",
            "Identificar e nomear emoções próprias",
            "Utilizar estratégias de autorregulação",
        ],
        "success_criteria": [
            "Iniciar pelo menos 3 interações sociais por dia",
            "Nomear corretamente 5 emoções básicas",
            "Usar técnicas de respiração quando ansioso",
        ],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "review_frequency": ReviewFrequency.WEEKLY.value,
        "professionals_involved_ids": [psychologist["id"]],
    }


class TestInterventionPlanCreate:
    """Tests for POST /api/v1/intervention-plans/"""

    def test_create_plan_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful intervention plan creation."""
        # Set psychologist as creator
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}

        response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == intervention_plan_data["title"]
        assert data["student_id"] == intervention_plan_data["student_id"]
        assert data["status"] == PlanStatus.DRAFT.value
        assert "id" in data
        assert len(data["strategies"]) == 2

    def test_create_plan_invalid_dates_fails(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test that invalid dates are rejected."""
        # Set end_date before start_date
        plan_data = intervention_plan_data.copy()
        plan_data["end_date"] = (date.today() - timedelta(days=1)).isoformat()

        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}

        response = client.post(
            "/api/v1/intervention-plans/",
            json=plan_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "posterior" in response.json()["detail"].lower()

    def test_create_plan_nonexistent_student_fails(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test that plan for nonexistent student is rejected."""
        plan_data = intervention_plan_data.copy()
        plan_data["student_id"] = str(uuid4())

        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}

        response = client.post(
            "/api/v1/intervention-plans/",
            json=plan_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInterventionPlanGet:
    """Tests for GET /api/v1/intervention-plans/{plan_id}"""

    def test_get_plan_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful plan retrieval."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Get plan
        response = client.get(
            f"/api/v1/intervention-plans/{plan_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == plan_id
        assert data["title"] == intervention_plan_data["title"]


class TestInterventionPlanUpdate:
    """Tests for PUT /api/v1/intervention-plans/{plan_id}"""

    def test_update_plan_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful plan update."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Update plan
        update_data = {
            "title": "Plano Atualizado",
            "progress_percentage": 50,
        }
        response = client.put(
            f"/api/v1/intervention-plans/{plan_id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["progress_percentage"] == 50


class TestInterventionPlanDelete:
    """Tests for DELETE /api/v1/intervention-plans/{plan_id}"""

    def test_delete_plan_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful plan deletion."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Delete plan
        response = client.delete(
            f"/api/v1/intervention-plans/{plan_id}",
            headers=headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify plan no longer accessible
        get_response = client.get(
            f"/api/v1/intervention-plans/{plan_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestInterventionPlanList:
    """Tests for GET /api/v1/intervention-plans/"""

    def test_list_plans_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful plan listing."""
        # Create plans
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        for i in range(3):
            plan_data = intervention_plan_data.copy()
            plan_data["title"] = f"Plano {i+1}"
            client.post("/api/v1/intervention-plans/", json=plan_data, headers=headers)

        # List plans
        response = client.get(
            "/api/v1/intervention-plans/",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "plans" in data
        assert "total" in data
        assert data["total"] >= 3

    def test_list_plans_filter_by_student(self, client, auth_headers, intervention_plan_data, test_student, psychologist):
        """Test filtering plans by student."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        client.post("/api/v1/intervention-plans/", json=intervention_plan_data, headers=headers)

        # Filter by student
        response = client.get(
            f"/api/v1/intervention-plans/?student_id={test_student['id']}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for plan in data["plans"]:
            assert plan["student_id"] == test_student["id"]

    def test_list_plans_filter_by_status(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test filtering plans by status."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        client.post("/api/v1/intervention-plans/", json=intervention_plan_data, headers=headers)

        # Filter by draft status
        response = client.get(
            f"/api/v1/intervention-plans/?status={PlanStatus.DRAFT.value}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for plan in data["plans"]:
            assert plan["status"] == PlanStatus.DRAFT.value


class TestInterventionPlanStatus:
    """Tests for POST /api/v1/intervention-plans/{plan_id}/status"""

    def test_change_status_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful status change."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Change status to active
        response = client.post(
            f"/api/v1/intervention-plans/{plan_id}/status",
            json={"status": PlanStatus.ACTIVE.value},
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == PlanStatus.ACTIVE.value


class TestInterventionPlanProgressNote:
    """Tests for POST /api/v1/intervention-plans/{plan_id}/progress-notes"""

    def test_add_progress_note_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test adding progress note to plan."""
        # Create plan
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Add progress note
        note_data = {
            "note": "Estudante demonstrou progresso significativo em autorregulação",
            "progress_percentage": 30,
        }
        response = client.post(
            f"/api/v1/intervention-plans/{plan_id}/progress-notes",
            json=note_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["progress_percentage"] == 30
        assert "progress_notes" in data


class TestInterventionPlanProfessionals:
    """Tests for managing professionals in plans."""

    def test_add_professional_to_plan(self, client, auth_headers, intervention_plan_data, psychologist, speech_therapist):
        """Test adding professional to existing plan."""
        # Create plan with psychologist
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=intervention_plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Add speech therapist
        response = client.post(
            f"/api/v1/intervention-plans/{plan_id}/professionals",
            json={"professional_id": speech_therapist["id"]},
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["professionals_involved"]) == 2

    def test_remove_professional_from_plan(self, client, auth_headers, intervention_plan_data, psychologist, speech_therapist):
        """Test removing professional from plan."""
        # Create plan with both professionals
        plan_data = intervention_plan_data.copy()
        plan_data["professionals_involved_ids"] = [psychologist["id"], speech_therapist["id"]]

        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        create_response = client.post(
            "/api/v1/intervention-plans/",
            json=plan_data,
            headers=headers,
        )
        plan_id = create_response.json()["id"]

        # Remove speech therapist
        response = client.delete(
            f"/api/v1/intervention-plans/{plan_id}/professionals/{speech_therapist['id']}",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["professionals_involved"]) == 1


class TestInterventionPlanStatistics:
    """Tests for GET /api/v1/intervention-plans/statistics/overview"""

    def test_get_statistics_success(self, client, auth_headers, intervention_plan_data, psychologist):
        """Test successful statistics retrieval."""
        # Create some plans
        headers = {**auth_headers, "X-Professional-ID": psychologist["id"]}
        for i in range(3):
            plan_data = intervention_plan_data.copy()
            plan_data["title"] = f"Plano {i+1}"
            client.post("/api/v1/intervention-plans/", json=plan_data, headers=headers)

        # Get statistics
        response = client.get(
            "/api/v1/intervention-plans/statistics/overview",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_plans" in data
        assert "by_status" in data
        assert "average_progress" in data
        assert data["total_plans"] >= 3
