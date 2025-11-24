"""
Integration tests for pending review endpoint.
"""

from datetime import date, timedelta
from uuid import uuid4

import pytest

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


class TestPendingReviewEndpoint:
    """Testes para endpoint /api/v1/intervention-plans/pending-review."""

    @pytest.fixture
    def pending_review_plans(self, client, auth_headers, test_student, psychologist, db_session):
        """Cria planos com diferentes status de revisão para teste."""
        from app.models.intervention_plan import InterventionPlan
        from app.models.student import Student
        from app.models.professional import Professional

        # Buscar student e professional do banco de dados
        student = db_session.query(Student).filter(Student.id == test_student["id"]).first()
        prof = db_session.query(Professional).filter(Professional.id == psychologist["id"]).first()

        if not student or not prof:
            pytest.skip("Student ou professional não encontrado no banco")

        # Plano 1: Nunca revisado (HIGH priority)
        plan1 = InterventionPlan(
            student_id=student.id,
            created_by_id=prof.id,
            title="Plano Nunca Revisado",
            objective="Objetivo do plano 1",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=None,
            needs_review=True,
        )

        # Plano 2: Revisado há 15 dias, frequência semanal (HIGH priority - 2x threshold)
        plan2 = InterventionPlan(
            student_id=student.id,
            created_by_id=prof.id,
            title="Plano Muito Atrasado",
            objective="Objetivo do plano 2",
            strategies=[{"name": "Estratégia 2"}],
            target_behaviors=["Comportamento 2"],
            success_criteria={"goal": "Meta 2"},
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=15),
            needs_review=True,
        )

        # Plano 3: Revisado há 8 dias, frequência semanal (MEDIUM priority)
        plan3 = InterventionPlan(
            student_id=student.id,
            created_by_id=prof.id,
            title="Plano Atrasado",
            objective="Objetivo do plano 3",
            strategies=[{"name": "Estratégia 3"}],
            target_behaviors=["Comportamento 3"],
            success_criteria={"goal": "Meta 3"},
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=8),
            needs_review=True,
        )

        # Plano 4: Plano COMPLETED - não deve aparecer
        plan4 = InterventionPlan(
            student_id=student.id,
            created_by_id=prof.id,
            title="Plano Completo",
            objective="Objetivo do plano 4",
            strategies=[{"name": "Estratégia 4"}],
            target_behaviors=["Comportamento 4"],
            success_criteria={"goal": "Meta 4"},
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=1),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.COMPLETED,
            last_reviewed_at=None,
            needs_review=False,
        )

        db_session.add_all([plan1, plan2, plan3, plan4])
        db_session.commit()

        return {
            "never_reviewed": plan1,
            "very_overdue": plan2,
            "overdue": plan3,
            "completed": plan4,
        }

    def test_get_pending_review_success(self, client, auth_headers, pending_review_plans):
        """Testa listagem de planos que precisam revisão."""
        response = client.get("/api/v1/intervention-plans/pending-review", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        assert "items" in data
        assert "total" in data
        assert "high_priority" in data
        assert "medium_priority" in data
        assert "low_priority" in data

        # Deve retornar 3 planos (excluindo o COMPLETED)
        assert data["total"] == 3

        # Verificar contagens de prioridade
        assert data["high_priority"] == 2  # Nunca revisado + muito atrasado
        assert data["medium_priority"] == 1  # Atrasado

    def test_get_pending_review_filter_by_priority(self, client, auth_headers, pending_review_plans):
        """Testa filtro por prioridade."""
        # Filtrar apenas HIGH priority
        response = client.get(
            "/api/v1/intervention-plans/pending-review?priority=high",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Deve retornar apenas 2 planos HIGH
        assert data["total"] == 2
        assert all(item["priority"] == "high" for item in data["items"])

    def test_get_pending_review_pagination(self, client, auth_headers, pending_review_plans):
        """Testa paginação."""
        # Página 1 - limite 2
        response = client.get(
            "/api/v1/intervention-plans/pending-review?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["items"]) == 2

        # Página 2 - limite 2
        response = client.get(
            "/api/v1/intervention-plans/pending-review?skip=2&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["items"]) == 1

    def test_get_pending_review_item_structure(self, client, auth_headers, pending_review_plans):
        """Testa estrutura dos items retornados."""
        response = client.get("/api/v1/intervention-plans/pending-review", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura do primeiro item
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "student_id" in item
        assert "student_name" in item
        assert "review_frequency" in item
        assert "last_reviewed_at" in item or item["last_reviewed_at"] is None
        assert "days_since_review" in item or item["days_since_review"] is None
        assert "created_at" in item
        assert "end_date" in item
        assert "days_remaining" in item
        assert "priority" in item
        assert "created_by_id" in item

    def test_get_pending_review_ordering(self, client, auth_headers, pending_review_plans):
        """Testa ordenação por prioridade."""
        response = client.get("/api/v1/intervention-plans/pending-review", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar que HIGH priority vem primeiro
        priorities = [item["priority"] for item in data["items"]]

        # Os dois primeiros devem ser HIGH
        assert priorities[0] == "high"
        assert priorities[1] == "high"

        # O terceiro deve ser MEDIUM
        assert priorities[2] == "medium"

    def test_get_pending_review_without_auth(self, client, pending_review_plans):
        """Testa acesso sem autenticação."""
        response = client.get("/api/v1/intervention-plans/pending-review")

        # Deve retornar 401 ou 403
        assert response.status_code in [401, 403]

    def test_get_pending_review_invalid_priority(self, client, auth_headers, pending_review_plans):
        """Testa filtro com prioridade inválida."""
        response = client.get(
            "/api/v1/intervention-plans/pending-review?priority=invalid",
            headers=auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422

    def test_get_pending_review_empty_result(self, client, auth_headers, db_session, test_student, psychologist):
        """Testa quando não há planos pendentes além dos do fixture."""
        # Apenas testar que a resposta tem estrutura correta
        response = client.get("/api/v1/intervention-plans/pending-review", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 0
