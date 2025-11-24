"""
Intervention Plan Service - Lógica de negócios para planos de intervenção.

Gerenciamento de planos de intervenção multiprofissionais.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.intervention_plan import InterventionPlan, PlanStatus, intervention_plan_professionals
from app.models.professional import Professional
from app.models.student import Student
from app.schemas.intervention_plan import (
    InterventionPlanCreate,
    InterventionPlanFilter,
    InterventionPlanStatistics,
    InterventionPlanUpdate,
    ProgressNoteCreate,
)


class InterventionPlanService:
    """Service para operações com planos de intervenção."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        plan_data: InterventionPlanCreate,
        created_by_id: UUID,
    ) -> InterventionPlan:
        """
        Cria novo plano de intervenção.

        Args:
            plan_data: Dados do plano
            created_by_id: ID do profissional que está criando

        Returns:
            InterventionPlan criado

        Raises:
            NotFoundException: Se estudante, profissional ou profissionais envolvidos não existem
            ValidationException: Se datas são inválidas
        """
        # Verificar se estudante existe
        student = self.db.query(Student).filter(Student.id == plan_data.student_id).first()
        if not student:
            raise NotFoundException(f"Estudante {plan_data.student_id} não encontrado")

        # Verificar se criador existe
        creator = self.db.query(Professional).filter(Professional.id == created_by_id).first()
        if not creator:
            raise NotFoundException(f"Profissional {created_by_id} não encontrado")

        # Validar datas
        if plan_data.end_date <= plan_data.start_date:
            raise ValidationException("Data de término deve ser posterior à data de início")

        # Criar plano
        plan_dict = plan_data.model_dump(exclude={"professionals_involved_ids"})
        plan = InterventionPlan(
            **plan_dict,
            created_by_id=created_by_id,
        )

        self.db.add(plan)
        self.db.flush()  # Para obter o ID antes de adicionar profissionais

        # Adicionar profissionais envolvidos
        if plan_data.professionals_involved_ids:
            for prof_id in plan_data.professionals_involved_ids:
                professional = self.db.query(Professional).filter(Professional.id == prof_id).first()
                if professional:
                    plan.professionals_involved.append(professional)
                else:
                    self.db.rollback()
                    raise NotFoundException(f"Profissional {prof_id} não encontrado")

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_by_id(self, plan_id: UUID) -> InterventionPlan:
        """
        Busca plano por ID.

        Args:
            plan_id: ID do plano

        Returns:
            InterventionPlan encontrado

        Raises:
            NotFoundException: Se plano não existe
        """
        plan = self.db.query(InterventionPlan).filter(InterventionPlan.id == plan_id).first()

        if not plan:
            raise NotFoundException(f"Plano de intervenção {plan_id} não encontrado")

        # Atualizar needs_review automaticamente
        plan.update_needs_review()
        self.db.commit()

        return plan

    def update(
        self,
        plan_id: UUID,
        update_data: InterventionPlanUpdate,
        professional_id: UUID,
    ) -> InterventionPlan:
        """
        Atualiza plano de intervenção.

        Args:
            plan_id: ID do plano
            update_data: Dados para atualização
            professional_id: ID do profissional que está atualizando

        Returns:
            InterventionPlan atualizado

        Raises:
            NotFoundException: Se plano não existe
            ForbiddenException: Se profissional não está envolvido no plano
            ValidationException: Se datas são inválidas
        """
        plan = self.get_by_id(plan_id)

        # Verificar se profissional está envolvido no plano
        if not self._is_professional_involved(plan, professional_id):
            raise ForbiddenException("Apenas profissionais envolvidos no plano podem editá-lo")

        # Validar datas se fornecidas
        new_start = update_data.start_date or plan.start_date
        new_end = update_data.end_date or plan.end_date
        if new_end <= new_start:
            raise ValidationException("Data de término deve ser posterior à data de início")

        # Atualizar campos fornecidos
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(plan, field, value)

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def delete(self, plan_id: UUID, professional_id: UUID) -> bool:
        """
        Remove plano de intervenção.

        Args:
            plan_id: ID do plano
            professional_id: ID do profissional que está removendo

        Returns:
            True se removido com sucesso

        Raises:
            NotFoundException: Se plano não existe
            ForbiddenException: Se profissional não criou o plano
        """
        plan = self.get_by_id(plan_id)

        # Apenas quem criou pode deletar
        if plan.created_by_id != professional_id:
            raise ForbiddenException("Apenas o profissional que criou o plano pode removê-lo")

        self.db.delete(plan)
        self.db.commit()

        return True

    def add_progress_note(
        self,
        plan_id: UUID,
        note_data: ProgressNoteCreate,
        professional_id: UUID,
    ) -> InterventionPlan:
        """
        Adiciona nota de progresso ao plano.

        Args:
            plan_id: ID do plano
            note_data: Dados da nota de progresso
            professional_id: ID do profissional que está adicionando

        Returns:
            InterventionPlan atualizado

        Raises:
            NotFoundException: Se plano não existe
            ForbiddenException: Se profissional não está envolvido
        """
        plan = self.get_by_id(plan_id)

        # Verificar se profissional está envolvido
        if not self._is_professional_involved(plan, professional_id):
            raise ForbiddenException("Apenas profissionais envolvidos podem adicionar notas de progresso")

        # Criar nota de progresso
        progress_note = {
            "date": datetime.now().isoformat(),
            "professional_id": str(professional_id),
            "content": note_data.note,
            "challenges": note_data.challenges,
            "successes": note_data.successes,
            "next_steps": note_data.next_steps,
        }

        # Adicionar à lista de notas
        if plan.progress_notes is None:
            plan.progress_notes = []

        plan.progress_notes.append(progress_note)

        # Atualizar percentual de progresso se fornecido
        if note_data.progress_percentage is not None:
            plan.progress_percentage = note_data.progress_percentage

        # Atualizar data de última revisão
        plan.last_reviewed_at = datetime.now()

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def change_status(
        self,
        plan_id: UUID,
        new_status: PlanStatus,
        professional_id: UUID,
    ) -> InterventionPlan:
        """Altera status do plano."""
        plan = self.get_by_id(plan_id)

        if not self._is_professional_involved(plan, professional_id):
            raise ForbiddenException("Apenas profissionais envolvidos podem alterar o status")

        plan.status = new_status
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def add_professional(
        self,
        plan_id: UUID,
        professional_id_to_add: UUID,
        requesting_professional_id: UUID,
    ) -> InterventionPlan:
        """Adiciona profissional ao plano."""
        plan = self.get_by_id(plan_id)

        # Apenas criador pode adicionar profissionais
        if plan.created_by_id != requesting_professional_id:
            raise ForbiddenException("Apenas o criador do plano pode adicionar profissionais")

        # Verificar se profissional existe
        professional = self.db.query(Professional).filter(Professional.id == professional_id_to_add).first()
        if not professional:
            raise NotFoundException(f"Profissional {professional_id_to_add} não encontrado")

        # Verificar se já está envolvido
        if professional in plan.professionals_involved:
            raise ValidationException("Profissional já está envolvido neste plano")

        plan.professionals_involved.append(professional)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def remove_professional(
        self,
        plan_id: UUID,
        professional_id_to_remove: UUID,
        requesting_professional_id: UUID,
    ) -> InterventionPlan:
        """Remove profissional do plano."""
        plan = self.get_by_id(plan_id)

        # Apenas criador pode remover profissionais
        if plan.created_by_id != requesting_professional_id:
            raise ForbiddenException("Apenas o criador do plano pode remover profissionais")

        # Buscar profissional na lista
        professional = next(
            (p for p in plan.professionals_involved if p.id == professional_id_to_remove),
            None,
        )

        if not professional:
            raise NotFoundException("Profissional não está envolvido neste plano")

        plan.professionals_involved.remove(professional)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InterventionPlanFilter] = None,
    ) -> tuple[List[InterventionPlan], int]:
        """
        Lista planos com filtros e paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            filters: Filtros opcionais

        Returns:
            Tupla (lista de planos, total)
        """
        query = self.db.query(InterventionPlan)

        # Aplicar filtros
        if filters:
            if filters.student_id:
                query = query.filter(InterventionPlan.student_id == filters.student_id)

            if filters.created_by_id:
                query = query.filter(InterventionPlan.created_by_id == filters.created_by_id)

            if filters.professional_id:
                # Filtrar por profissional envolvido
                query = query.join(intervention_plan_professionals).filter(
                    intervention_plan_professionals.c.professional_id == filters.professional_id
                )

            if filters.status:
                query = query.filter(InterventionPlan.status == filters.status)

            if filters.review_frequency:
                query = query.filter(InterventionPlan.review_frequency == filters.review_frequency)

            if filters.needs_review is not None:
                # Filtrar por planos que precisam revisão
                query = query.filter(InterventionPlan.needs_review == filters.needs_review)

            if filters.start_date_from:
                query = query.filter(InterventionPlan.start_date >= filters.start_date_from)

            if filters.start_date_to:
                query = query.filter(InterventionPlan.start_date <= filters.start_date_to)

            if filters.end_date_from:
                query = query.filter(InterventionPlan.end_date >= filters.end_date_from)

            if filters.end_date_to:
                query = query.filter(InterventionPlan.end_date <= filters.end_date_to)

            if filters.progress_min is not None:
                query = query.filter(InterventionPlan.progress_percentage >= filters.progress_min)

            if filters.progress_max is not None:
                query = query.filter(InterventionPlan.progress_percentage <= filters.progress_max)

            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        InterventionPlan.title.ilike(search_pattern),
                        InterventionPlan.objective.ilike(search_pattern),
                    )
                )

        # Total de registros
        total = query.count()

        # Ordenação (mais recentes primeiro) e paginação
        plans = query.order_by(InterventionPlan.created_at.desc()).offset(skip).limit(limit).all()

        # Atualizar needs_review automaticamente para cada plano
        for plan in plans:
            plan.update_needs_review()
        if plans:
            self.db.commit()

        return plans, total

    def get_by_student(
        self,
        student_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[InterventionPlan], int]:
        """Lista planos de um estudante específico."""
        filters = InterventionPlanFilter(student_id=student_id)
        return self.list(skip=skip, limit=limit, filters=filters)

    def get_active_plans(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[InterventionPlan], int]:
        """Lista apenas planos ativos."""
        filters = InterventionPlanFilter(status=PlanStatus.ACTIVE)
        return self.list(skip=skip, limit=limit, filters=filters)

    def get_statistics(self) -> InterventionPlanStatistics:
        """
        Obtém estatísticas de planos de intervenção.

        Returns:
            Estatísticas agregadas
        """
        # Total de planos
        total = self.db.query(InterventionPlan).count()

        # Planos ativos
        active = self.db.query(InterventionPlan).filter(InterventionPlan.status == PlanStatus.ACTIVE).count()

        # Planos concluídos
        completed = self.db.query(InterventionPlan).filter(InterventionPlan.status == PlanStatus.COMPLETED).count()

        # Por status
        by_status_query = (
            self.db.query(InterventionPlan.status, func.count(InterventionPlan.id))
            .group_by(InterventionPlan.status)
            .all()
        )
        by_status = {str(status): count for status, count in by_status_query}

        # Progresso médio
        avg_progress = self.db.query(func.avg(InterventionPlan.progress_percentage)).scalar() or 0.0

        # Planos que precisam revisão (simplificado - planos ativos sem revisão recente)
        needs_review = (
            self.db.query(InterventionPlan)
            .filter(
                and_(
                    InterventionPlan.status == PlanStatus.ACTIVE,
                    InterventionPlan.last_reviewed_at == None,  # noqa: E711
                )
            )
            .count()
        )

        # Por estudante
        by_student_query = (
            self.db.query(InterventionPlan.student_id, func.count(InterventionPlan.id))
            .group_by(InterventionPlan.student_id)
            .all()
        )
        by_student = {str(student_id): count for student_id, count in by_student_query}

        # Duração média (dias)
        plans_with_dates = self.db.query(InterventionPlan).all()
        if plans_with_dates:
            total_days = sum((plan.end_date - plan.start_date).days for plan in plans_with_dates)
            avg_duration = total_days / len(plans_with_dates)
        else:
            avg_duration = 0.0

        return InterventionPlanStatistics(
            total_plans=total,
            active_plans=active,
            completed_plans=completed,
            by_status=by_status,
            average_progress=avg_progress,
            needs_review_count=needs_review,
            by_student=by_student,
            average_duration_days=avg_duration,
        )

    def _is_professional_involved(self, plan: InterventionPlan, professional_id: UUID) -> bool:
        """Verifica se profissional está envolvido no plano."""
        if plan.created_by_id == professional_id:
            return True

        return any(p.id == professional_id for p in plan.professionals_involved)
