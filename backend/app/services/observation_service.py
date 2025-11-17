"""
Observation Service - Lógica de negócios para observações profissionais.

Gerenciamento de observações multiprofissionais sobre estudantes.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.observation import ObservationContext, ObservationType, ProfessionalObservation
from app.models.professional import Professional
from app.models.student import Student
from app.schemas.observation import (
    ObservationFilter,
    ObservationSummary,
    ProfessionalObservationCreate,
    ProfessionalObservationUpdate,
)


class ObservationService:
    """Service para operações com observações profissionais."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        observation_data: ProfessionalObservationCreate,
        professional_id: UUID,
    ) -> ProfessionalObservation:
        """
        Cria nova observação profissional.

        Args:
            observation_data: Dados da observação
            professional_id: ID do profissional que está criando

        Returns:
            ProfessionalObservation criada

        Raises:
            NotFoundException: Se estudante ou profissional não existe
        """
        # Verificar se estudante existe
        student = self.db.query(Student).filter(Student.id == observation_data.student_id).first()
        if not student:
            raise NotFoundException(f"Estudante {observation_data.student_id} não encontrado")

        # Verificar se profissional existe
        professional = self.db.query(Professional).filter(Professional.id == professional_id).first()
        if not professional:
            raise NotFoundException(f"Profissional {professional_id} não encontrado")

        # Criar observação
        observation = ProfessionalObservation(
            **observation_data.model_dump(),
            professional_id=professional_id,
        )

        self.db.add(observation)
        self.db.commit()
        self.db.refresh(observation)

        return observation

    def get_by_id(
        self,
        observation_id: UUID,
        requesting_professional_id: UUID,
    ) -> ProfessionalObservation:
        """
        Busca observação por ID com controle de acesso.

        Args:
            observation_id: ID da observação
            requesting_professional_id: ID do profissional solicitante

        Returns:
            ProfessionalObservation encontrada

        Raises:
            NotFoundException: Se observação não existe
            ForbiddenException: Se profissional não tem acesso
        """
        observation = (
            self.db.query(ProfessionalObservation)
            .filter(ProfessionalObservation.id == observation_id)
            .first()
        )

        if not observation:
            raise NotFoundException(f"Observação {observation_id} não encontrada")

        # Controle de acesso para observações privadas
        if observation.is_private:
            requesting_professional = (
                self.db.query(Professional)
                .filter(Professional.id == requesting_professional_id)
                .first()
            )
            if not requesting_professional or not requesting_professional.is_health_professional:
                raise ForbiddenException(
                    "Acesso negado. Esta observação é privada e visível apenas para profissionais de saúde."
                )

        return observation

    def update(
        self,
        observation_id: UUID,
        update_data: ProfessionalObservationUpdate,
        professional_id: UUID,
    ) -> ProfessionalObservation:
        """
        Atualiza observação.

        Args:
            observation_id: ID da observação
            update_data: Dados para atualização
            professional_id: ID do profissional que está atualizando

        Returns:
            ProfessionalObservation atualizada

        Raises:
            NotFoundException: Se observação não existe
            ForbiddenException: Se profissional não criou a observação
        """
        observation = self.get_by_id(observation_id, professional_id)

        # Apenas quem criou pode editar
        if observation.professional_id != professional_id:
            raise ForbiddenException("Apenas o profissional que criou a observação pode editá-la")

        # Atualizar campos fornecidos
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(observation, field, value)

        self.db.commit()
        self.db.refresh(observation)

        return observation

    def delete(self, observation_id: UUID, professional_id: UUID) -> bool:
        """
        Remove observação.

        Args:
            observation_id: ID da observação
            professional_id: ID do profissional que está removendo

        Returns:
            True se removido com sucesso

        Raises:
            NotFoundException: Se observação não existe
            ForbiddenException: Se profissional não criou a observação
        """
        observation = self.get_by_id(observation_id, professional_id)

        # Apenas quem criou pode deletar
        if observation.professional_id != professional_id:
            raise ForbiddenException("Apenas o profissional que criou a observação pode removê-la")

        self.db.delete(observation)
        self.db.commit()

        return True

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ObservationFilter] = None,
        requesting_professional_id: Optional[UUID] = None,
    ) -> tuple[List[ProfessionalObservation], int]:
        """
        Lista observações com filtros e paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            filters: Filtros opcionais
            requesting_professional_id: ID do profissional solicitante (para controle de acesso)

        Returns:
            Tupla (lista de observações, total)
        """
        query = self.db.query(ProfessionalObservation)

        # Controle de acesso para observações privadas
        if requesting_professional_id:
            requesting_professional = (
                self.db.query(Professional)
                .filter(Professional.id == requesting_professional_id)
                .first()
            )
            if requesting_professional and not requesting_professional.is_health_professional:
                # Profissionais de educação veem apenas observações não privadas
                query = query.filter(ProfessionalObservation.is_private == False)  # noqa: E712

        # Aplicar filtros
        if filters:
            if filters.student_id:
                query = query.filter(ProfessionalObservation.student_id == filters.student_id)

            if filters.professional_id:
                query = query.filter(ProfessionalObservation.professional_id == filters.professional_id)

            if filters.observation_type:
                query = query.filter(ProfessionalObservation.observation_type == filters.observation_type)

            if filters.context:
                query = query.filter(ProfessionalObservation.context == filters.context)

            if filters.severity_level_min is not None:
                query = query.filter(ProfessionalObservation.severity_level >= filters.severity_level_min)

            if filters.severity_level_max is not None:
                query = query.filter(ProfessionalObservation.severity_level <= filters.severity_level_max)

            if filters.requires_intervention is not None:
                query = query.filter(
                    ProfessionalObservation.requires_intervention == filters.requires_intervention
                )

            if filters.is_private is not None:
                query = query.filter(ProfessionalObservation.is_private == filters.is_private)

            if filters.tags:
                # Buscar observações que contenham pelo menos uma das tags
                for tag in filters.tags:
                    query = query.filter(ProfessionalObservation.tags.contains([tag]))

            if filters.date_from:
                query = query.filter(ProfessionalObservation.observed_at >= filters.date_from)

            if filters.date_to:
                query = query.filter(ProfessionalObservation.observed_at <= filters.date_to)

            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(ProfessionalObservation.content.ilike(search_pattern))

        # Total de registros
        total = query.count()

        # Ordenação (mais recentes primeiro) e paginação
        observations = (
            query.order_by(ProfessionalObservation.observed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return observations, total

    def get_by_student(
        self,
        student_id: UUID,
        skip: int = 0,
        limit: int = 100,
        requesting_professional_id: Optional[UUID] = None,
    ) -> tuple[List[ProfessionalObservation], int]:
        """Lista observações de um estudante específico."""
        filters = ObservationFilter(student_id=student_id)
        return self.list(
            skip=skip,
            limit=limit,
            filters=filters,
            requesting_professional_id=requesting_professional_id,
        )

    def get_by_professional(
        self,
        professional_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[ProfessionalObservation], int]:
        """Lista observações criadas por um profissional específico."""
        filters = ObservationFilter(professional_id=professional_id)
        return self.list(skip=skip, limit=limit, filters=filters)

    def get_requiring_intervention(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[ProfessionalObservation], int]:
        """Lista observações que requerem intervenção imediata."""
        filters = ObservationFilter(requires_intervention=True)
        return self.list(skip=skip, limit=limit, filters=filters)

    def get_summary_by_student(
        self,
        student_id: UUID,
        requesting_professional_id: UUID,
    ) -> ObservationSummary:
        """
        Gera resumo de observações para um estudante.

        Args:
            student_id: ID do estudante
            requesting_professional_id: ID do profissional solicitante

        Returns:
            ObservationSummary com estatísticas e observações recentes
        """
        # Buscar todas as observações do estudante (respeitando privacidade)
        all_observations, total = self.get_by_student(
            student_id=student_id,
            skip=0,
            limit=10000,  # Pegar todas para estatísticas
            requesting_professional_id=requesting_professional_id,
        )

        # Total de observações
        total_observations = len(all_observations)

        # Por tipo
        by_type = {}
        for obs in all_observations:
            type_str = str(obs.observation_type)
            by_type[type_str] = by_type.get(type_str, 0) + 1

        # Por severidade
        by_severity = {}
        for obs in all_observations:
            sev = obs.severity_level
            by_severity[sev] = by_severity.get(sev, 0) + 1

        # Requer intervenção
        requires_intervention_count = sum(
            1 for obs in all_observations if obs.requires_intervention
        )

        # Contextos mais comuns (top 5)
        context_counts = {}
        for obs in all_observations:
            context_str = str(obs.context)
            context_counts[context_str] = context_counts.get(context_str, 0) + 1

        most_common_contexts = [
            {"context": ctx, "count": count}
            for ctx, count in sorted(
                context_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5]
        ]

        # Tags mais comuns (top 10)
        tag_counts = {}
        for obs in all_observations:
            if obs.tags:
                for tag in obs.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        most_common_tags = [
            {"tag": tag, "count": count}
            for tag, count in sorted(
                tag_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
        ]

        # Observações recentes (últimas 10)
        recent_observations = sorted(
            all_observations,
            key=lambda x: x.observed_at,
            reverse=True,
        )[:10]

        return ObservationSummary(
            student_id=student_id,
            total_observations=total_observations,
            by_type=by_type,
            by_severity=by_severity,
            requires_intervention_count=requires_intervention_count,
            most_common_contexts=most_common_contexts,
            most_common_tags=most_common_tags,
            recent_observations=recent_observations,
        )
