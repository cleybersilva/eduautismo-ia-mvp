"""
Testes unitários para a lógica de cálculo do campo needs_review.

Testa o método calculate_needs_review() do modelo InterventionPlan.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.models.intervention_plan import InterventionPlan, PlanStatus, ReviewFrequency
from app.models.student import Student
from app.models.professional import Professional, ProfessionalRole
from app.models.user import User, UserRole


@pytest.fixture
def teacher(db_session):
    """Cria professor para testes."""
    teacher = User(
        email=f"teacher.teste.{uuid4().hex[:8]}@example.com",
        hashed_password="$2b$12$hashedpassword",  # Dummy hashed password
        full_name="Professor Teste",
        role=UserRole.TEACHER,
        is_active=True,
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher


@pytest.fixture
def student(db_session, teacher):
    """Cria estudante para testes."""
    student = Student(
        name="Aluno Teste",
        date_of_birth=date(2015, 1, 1),
        age=10,
        diagnosis="Autismo Nível 1",
        teacher_id=teacher.id,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def professional(db_session):
    """Cria profissional para testes."""
    prof = Professional(
        name="Prof Teste",
        email=f"prof.teste.{uuid4().hex[:8]}@example.com",
        role=ProfessionalRole.PSYCHOLOGIST,
        organization="Clínica Teste",
    )
    db_session.add(prof)
    db_session.commit()
    db_session.refresh(prof)
    return prof


class TestNeedsReviewCalculation:
    """Testes para cálculo de needs_review."""

    def test_plan_never_reviewed_needs_review(self, db_session, student, professional):
        """Plano que nunca foi revisado deve precisar de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Teste",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=None,  # Nunca foi revisado
        )
        db_session.add(plan)
        db_session.commit()

        # Plano nunca revisado deve precisar de revisão
        assert plan.calculate_needs_review() is True

    def test_plan_completed_does_not_need_review(self, db_session, student, professional):
        """Plano completado não precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Completado",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=90),
            end_date=date.today() - timedelta(days=10),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.COMPLETED,
            last_reviewed_at=None,
        )
        db_session.add(plan)
        db_session.commit()

        # Plano completado não precisa revisão
        assert plan.calculate_needs_review() is False

    def test_plan_weekly_reviewed_yesterday_no_review_needed(self, db_session, student, professional):
        """Plano semanal revisado ontem não precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Semanal",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=1),  # Revisado ontem
        )
        db_session.add(plan)
        db_session.commit()

        # Revisado há 1 dia, frequência semanal (7 dias) - não precisa revisão
        assert plan.calculate_needs_review() is False

    def test_plan_weekly_reviewed_8_days_ago_needs_review(self, db_session, student, professional):
        """Plano semanal revisado há 8 dias precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Semanal Atrasado",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=8),  # Revisado há 8 dias
        )
        db_session.add(plan)
        db_session.commit()

        # Revisado há 8 dias, frequência semanal (7 dias) - precisa revisão
        assert plan.calculate_needs_review() is True

    def test_plan_daily_reviewed_yesterday_needs_review(self, db_session, student, professional):
        """Plano diário revisado ontem precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Diário",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            review_frequency=ReviewFrequency.DAILY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=1),  # Revisado ontem
        )
        db_session.add(plan)
        db_session.commit()

        # Revisado há 1 dia, frequência diária (1 dia) - precisa revisão
        assert plan.calculate_needs_review() is True

    def test_plan_monthly_reviewed_20_days_ago_no_review_needed(self, db_session, student, professional):
        """Plano mensal revisado há 20 dias não precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Mensal",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() + timedelta(days=90),
            review_frequency=ReviewFrequency.MONTHLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=20),  # Revisado há 20 dias
        )
        db_session.add(plan)
        db_session.commit()

        # Revisado há 20 dias, frequência mensal (30 dias) - não precisa revisão
        assert plan.calculate_needs_review() is False

    def test_plan_quarterly_reviewed_100_days_ago_needs_review(self, db_session, student, professional):
        """Plano trimestral revisado há 100 dias precisa de revisão."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano Trimestral",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today() - timedelta(days=150),
            end_date=date.today() + timedelta(days=30),
            review_frequency=ReviewFrequency.QUARTERLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=date.today() - timedelta(days=100),  # Revisado há 100 dias
        )
        db_session.add(plan)
        db_session.commit()

        # Revisado há 100 dias, frequência trimestral (90 dias) - precisa revisão
        assert plan.calculate_needs_review() is True

    def test_update_needs_review_updates_field(self, db_session, student, professional):
        """Método update_needs_review deve atualizar o campo no banco."""
        plan = InterventionPlan(
            student_id=student.id,
            created_by_id=professional.id,
            title="Plano para Atualização",
            objective="Objetivo teste",
            strategies=[{"name": "Estratégia 1"}],
            target_behaviors=["Comportamento 1"],
            success_criteria={"goal": "Meta 1"},
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            review_frequency=ReviewFrequency.WEEKLY,
            status=PlanStatus.ACTIVE,
            last_reviewed_at=None,
            needs_review=False,  # Inicialmente False
        )
        db_session.add(plan)
        db_session.commit()

        # Campo deve estar False inicialmente
        assert plan.needs_review is False

        # Atualizar needs_review
        result = plan.update_needs_review()

        # Deve retornar True (nunca foi revisado)
        assert result is True
        # Campo deve ter sido atualizado
        assert plan.needs_review is True

        # Commit para persistir
        db_session.commit()
        db_session.refresh(plan)

        # Verificar que foi persistido
        assert plan.needs_review is True

    def test_review_frequency_thresholds(self, db_session, student, professional):
        """Testa os limiares corretos para cada frequência de revisão."""
        frequencies = {
            ReviewFrequency.DAILY: (1, 0),  # (threshold em dias, dias antes do threshold)
            ReviewFrequency.WEEKLY: (7, 6),
            ReviewFrequency.BIWEEKLY: (14, 13),
            ReviewFrequency.MONTHLY: (30, 29),
            ReviewFrequency.QUARTERLY: (90, 89),
        }

        for frequency, (threshold, days_before) in frequencies.items():
            # Teste 1: Revisado exatamente no threshold - deve precisar revisão
            plan_at_threshold = InterventionPlan(
                student_id=student.id,
                created_by_id=professional.id,
                title=f"Plano {frequency.value} - At Threshold",
                objective="Objetivo teste",
                strategies=[{"name": "Estratégia 1"}],
                target_behaviors=["Comportamento 1"],
                success_criteria={"goal": "Meta 1"},
                start_date=date.today() - timedelta(days=90),
                end_date=date.today() + timedelta(days=90),
                review_frequency=frequency,
                status=PlanStatus.ACTIVE,
                last_reviewed_at=date.today() - timedelta(days=threshold),
            )
            assert plan_at_threshold.calculate_needs_review() is True, \
                f"{frequency.value}: Deveria precisar revisão no threshold de {threshold} dias"

            # Teste 2: Revisado um dia antes do threshold - não deve precisar revisão
            plan_before_threshold = InterventionPlan(
                student_id=student.id,
                created_by_id=professional.id,
                title=f"Plano {frequency.value} - Before Threshold",
                objective="Objetivo teste",
                strategies=[{"name": "Estratégia 1"}],
                target_behaviors=["Comportamento 1"],
                success_criteria={"goal": "Meta 1"},
                start_date=date.today() - timedelta(days=90),
                end_date=date.today() + timedelta(days=90),
                review_frequency=frequency,
                status=PlanStatus.ACTIVE,
                last_reviewed_at=date.today() - timedelta(days=days_before),
            )
            assert plan_before_threshold.calculate_needs_review() is False, \
                f"{frequency.value}: NÃO deveria precisar revisão {days_before} dias antes do threshold"
