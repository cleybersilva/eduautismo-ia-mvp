"""
Integration tests for MVP 3.0 Multidisciplinary API endpoints.

Tests the new endpoints:
- POST /activities/generate-multidisciplinary
- GET /activities/search/bncc/{code}
- GET /activities/meta/subjects
- GET /activities/meta/grade-levels
- GET /activities/search (with v3.0 filters)
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.utils.constants import GradeLevel, PedagogicalActivityType, Subject


class TestMetaEndpoints:
    """Test metadata endpoints for subjects and grade levels."""

    @pytest.mark.asyncio
    async def test_list_subjects(self, async_client: AsyncClient, auth_headers: dict):
        """Test GET /activities/meta/subjects."""
        response = await async_client.get(
            "/api/v1/activities/meta/subjects",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should return dict of subject_code => display_name
        assert isinstance(data, dict)
        assert len(data) == 25  # All 25 subjects

        # Check some known subjects
        assert "matematica" in data
        assert data["matematica"] == "Matemática"
        assert "portugues" in data
        assert data["portugues"] == "Português"
        assert "educacao_fisica" in data
        assert data["educacao_fisica"] == "Educação Física"

    @pytest.mark.asyncio
    async def test_list_grade_levels(self, async_client: AsyncClient, auth_headers: dict):
        """Test GET /activities/meta/grade-levels."""
        response = await async_client.get(
            "/api/v1/activities/meta/grade-levels",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should return dict of grade_code => display_name
        assert isinstance(data, dict)
        assert len(data) == 18  # All 18 grade levels

        # Check some known grades
        assert "infantil_1" in data
        assert data["infantil_1"] == "Infantil I"
        assert "fundamental_1_3ano" in data
        assert data["fundamental_1_3ano"] == "3º Ano - Fundamental I"
        assert "medio_1ano" in data
        assert data["medio_1ano"] == "1ª Série - Ensino Médio"


class TestAdvancedSearch:
    """Test advanced search endpoint with v3.0 filters."""

    @pytest.mark.asyncio
    async def test_search_by_subject(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test filtering by subject."""
        # Create activity with subject
        activity_data = {
            "student_id": str(test_student.id),
            "title": "Atividade de Matemática",
            "description": "Teste de matemática",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
            "subject": "matematica",
            "grade_level": "fundamental_1_3ano",
        }

        # Create activity
        create_response = await async_client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Search by subject
        response = await async_client.get(
            "/api/v1/activities/search?subject=matematica",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) >= 1
        assert all(act["subject"] == "matematica" for act in activities if act.get("subject"))

    @pytest.mark.asyncio
    async def test_search_by_grade_level(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test filtering by grade level."""
        # Create activity with grade level
        activity_data = {
            "student_id": str(test_student.id),
            "title": "Atividade 3º Ano",
            "description": "Teste para 3º ano",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
            "subject": "portugues",
            "grade_level": "fundamental_1_3ano",
        }

        # Create activity
        create_response = await async_client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Search by grade level
        response = await async_client.get(
            "/api/v1/activities/search?grade_level=fundamental_1_3ano",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) >= 1
        assert all(
            act["grade_level"] == "fundamental_1_3ano" for act in activities if act.get("grade_level")
        )

    @pytest.mark.asyncio
    async def test_search_combined_filters(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test search with multiple v3.0 filters combined."""
        # Create activity with multiple v3.0 fields
        activity_data = {
            "student_id": str(test_student.id),
            "title": "Exercício de Matemática",
            "description": "Exercício para 3º ano",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
            "subject": "matematica",
            "grade_level": "fundamental_1_3ano",
            "pedagogical_type": "exercicio",
            "bncc_competencies": ["EF03MA01", "EF03MA02"],
        }

        # Create activity
        create_response = await async_client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Search with combined filters
        response = await async_client.get(
            "/api/v1/activities/search"
            "?subject=matematica"
            "&grade_level=fundamental_1_3ano"
            "&pedagogical_type=exercicio"
            "&has_bncc=true",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) >= 1

        # Verify filters applied correctly
        for act in activities:
            if act.get("subject"):
                assert act["subject"] == "matematica"
            if act.get("grade_level"):
                assert act["grade_level"] == "fundamental_1_3ano"
            if act.get("pedagogical_type"):
                assert act["pedagogical_type"] == "exercicio"
            if act.get("bncc_competencies"):
                assert len(act["bncc_competencies"]) > 0

    @pytest.mark.asyncio
    async def test_search_has_bncc_filter(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test has_bncc filter (true/false)."""
        # Create activity WITH BNCC
        activity_with_bncc = {
            "student_id": str(test_student.id),
            "title": "Com BNCC",
            "description": "Atividade com códigos BNCC",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
            "bncc_competencies": ["EF03MA01"],
        }

        # Create activity WITHOUT BNCC
        activity_without_bncc = {
            "student_id": str(test_student.id),
            "title": "Sem BNCC",
            "description": "Atividade sem códigos BNCC",
            "activity_type": "cognitive",
            "difficulty": "easy",
            "duration_minutes": 20,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
        }

        await async_client.post("/api/v1/activities/", json=activity_with_bncc, headers=auth_headers)
        await async_client.post("/api/v1/activities/", json=activity_without_bncc, headers=auth_headers)

        # Search for activities WITH BNCC
        response_with = await async_client.get(
            "/api/v1/activities/search?has_bncc=true",
            headers=auth_headers,
        )
        assert response_with.status_code == status.HTTP_200_OK
        activities_with = response_with.json()
        assert all(
            act.get("bncc_competencies") and len(act["bncc_competencies"]) > 0
            for act in activities_with
            if "bncc_competencies" in act
        )

        # Search for activities WITHOUT BNCC
        response_without = await async_client.get(
            "/api/v1/activities/search?has_bncc=false",
            headers=auth_headers,
        )
        assert response_without.status_code == status.HTTP_200_OK


class TestBNCCSearch:
    """Test BNCC code search endpoint."""

    @pytest.mark.asyncio
    async def test_search_by_bncc_code(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test GET /activities/search/bncc/{code}."""
        # Create activities with specific BNCC codes
        activity_data = {
            "student_id": str(test_student.id),
            "title": "Atividade BNCC EF03MA01",
            "description": "Atividade alinhada com EF03MA01",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "objectives": ["Objetivo 1"],
            "materials": ["Material 1"],
            "instructions": ["Passo 1"],
            "subject": "matematica",
            "grade_level": "fundamental_1_3ano",
            "bncc_competencies": ["EF03MA01", "EF03MA02"],
        }

        # Create activity
        create_response = await async_client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Search by BNCC code
        response = await async_client.get(
            "/api/v1/activities/search/bncc/EF03MA01",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) >= 1

        # Verify BNCC code is in results
        for act in activities:
            assert "bncc_competencies" in act
            assert "EF03MA01" in act["bncc_competencies"]

    @pytest.mark.asyncio
    async def test_search_by_bncc_code_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test searching for non-existent BNCC code."""
        response = await async_client.get(
            "/api/v1/activities/search/bncc/EF99ZZ99",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) == 0  # No activities with this code

    @pytest.mark.asyncio
    async def test_search_bncc_pagination(self, async_client: AsyncClient, auth_headers: dict, test_student):
        """Test BNCC search with pagination."""
        # Create multiple activities with same BNCC code
        for i in range(5):
            activity_data = {
                "student_id": str(test_student.id),
                "title": f"Atividade BNCC {i}",
                "description": f"Atividade {i}",
                "activity_type": "cognitive",
                "difficulty": "medium",
                "duration_minutes": 30,
                "objectives": ["Objetivo 1"],
                "materials": ["Material 1"],
                "instructions": ["Passo 1"],
                "bncc_competencies": ["EF03MA06"],
            }
            await async_client.post("/api/v1/activities/", json=activity_data, headers=auth_headers)

        # Test pagination
        response = await async_client.get(
            "/api/v1/activities/search/bncc/EF03MA06?skip=0&limit=3",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) <= 3  # Respects limit


class TestMultidisciplinaryGeneration:
    """Test multidisciplinary activity generation endpoint."""

    @pytest.mark.asyncio
    async def test_generate_multidisciplinary_requires_subject(
        self, async_client: AsyncClient, auth_headers: dict, test_student
    ):
        """Test that subject and grade_level are required."""
        # Request without subject and grade_level
        activity_data = {
            "student_id": str(test_student.id),
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
        }

        response = await async_client.post(
            "/api/v1/activities/generate-multidisciplinary",
            json=activity_data,
            headers=auth_headers,
        )

        # Should fail with 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "subject e grade_level são obrigatórios" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_multidisciplinary_invalid_student(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test generation with non-existent student."""
        activity_data = {
            "student_id": "00000000-0000-0000-0000-000000000000",
            "activity_type": "cognitive",
            "difficulty": "medium",
            "duration_minutes": 30,
            "subject": "matematica",
            "grade_level": "fundamental_1_3ano",
        }

        response = await async_client.post(
            "/api/v1/activities/generate-multidisciplinary",
            json=activity_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Aluno não encontrado" in response.json()["detail"]
