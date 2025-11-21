"""
Professional Service - Lógica de negócios para profissionais.

Gerenciamento de profissionais do sistema multiprofissional.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.models.professional import Professional, ProfessionalRole
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalFilter,
    ProfessionalStatistics,
    ProfessionalUpdate,
)


class ProfessionalService:
    """Service para operações com profissionais."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, professional_data: ProfessionalCreate) -> Professional:
        """
        Cria novo profissional.

        Args:
            professional_data: Dados do profissional

        Returns:
            Professional criado

        Raises:
            ValidationException: Se email já existe
        """
        # Verificar se email já existe
        existing = self.db.query(Professional).filter(Professional.email == professional_data.email).first()
        if existing:
            raise ValidationException(f"Email {professional_data.email} já está cadastrado")

        professional = Professional(**professional_data.model_dump())
        self.db.add(professional)
        self.db.commit()
        self.db.refresh(professional)

        return professional

    def get_by_id(self, professional_id: UUID) -> Professional:
        """
        Busca profissional por ID.

        Args:
            professional_id: ID do profissional

        Returns:
            Professional encontrado

        Raises:
            NotFoundException: Se profissional não existe
        """
        professional = self.db.query(Professional).filter(Professional.id == professional_id).first()
        if not professional:
            raise NotFoundException(f"Profissional {professional_id} não encontrado")

        return professional

    def get_by_email(self, email: str) -> Optional[Professional]:
        """Busca profissional por email."""
        return self.db.query(Professional).filter(Professional.email == email).first()

    def update(self, professional_id: UUID, update_data: ProfessionalUpdate) -> Professional:
        """
        Atualiza profissional.

        Args:
            professional_id: ID do profissional
            update_data: Dados para atualização

        Returns:
            Professional atualizado

        Raises:
            NotFoundException: Se profissional não existe
            ValidationException: Se email já existe (quando atualizado)
        """
        professional = self.get_by_id(professional_id)

        # Se atualizando email, verificar se já existe
        if update_data.email and update_data.email != professional.email:
            existing = self.get_by_email(update_data.email)
            if existing:
                raise ValidationException(f"Email {update_data.email} já está cadastrado")

        # Atualizar campos fornecidos
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(professional, field, value)

        self.db.commit()
        self.db.refresh(professional)

        return professional

    def delete(self, professional_id: UUID) -> bool:
        """
        Remove profissional (soft delete - marca como inativo).

        Args:
            professional_id: ID do profissional

        Returns:
            True se removido com sucesso

        Raises:
            NotFoundException: Se profissional não existe
        """
        professional = self.get_by_id(professional_id)
        professional.is_active = False
        self.db.commit()

        return True

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ProfessionalFilter] = None,
    ) -> tuple[List[Professional], int]:
        """
        Lista profissionais com filtros e paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            filters: Filtros opcionais

        Returns:
            Tupla (lista de profissionais, total)
        """
        query = self.db.query(Professional)

        # Aplicar filtros
        if filters:
            if filters.role:
                query = query.filter(Professional.role == filters.role)

            if filters.organization:
                query = query.filter(Professional.organization.ilike(f"%{filters.organization}%"))

            if filters.is_active is not None:
                query = query.filter(Professional.is_active == filters.is_active)

            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Professional.name.ilike(search_pattern),
                        Professional.email.ilike(search_pattern),
                    )
                )

            if filters.is_education is not None:
                education_roles = [
                    ProfessionalRole.TEACHER,
                    ProfessionalRole.SPECIAL_EDUCATOR,
                    ProfessionalRole.SCHOOL_COORDINATOR,
                    ProfessionalRole.SCHOOL_MANAGER,
                    ProfessionalRole.PSYCHOPEDAGOGIST,
                ]
                if filters.is_education:
                    query = query.filter(Professional.role.in_(education_roles))
                else:
                    query = query.filter(~Professional.role.in_(education_roles))

            if filters.is_health is not None:
                health_roles = [
                    ProfessionalRole.PSYCHOLOGIST,
                    ProfessionalRole.PSYCHIATRIST,
                    ProfessionalRole.NEUROPEDIATRICIAN,
                    ProfessionalRole.OCCUPATIONAL_THERAPIST,
                    ProfessionalRole.SPEECH_THERAPIST,
                    ProfessionalRole.PHYSIOTHERAPIST,
                ]
                if filters.is_health:
                    query = query.filter(Professional.role.in_(health_roles))
                else:
                    query = query.filter(~Professional.role.in_(health_roles))

        # Total de registros
        total = query.count()

        # Ordenação e paginação
        professionals = query.order_by(Professional.name).offset(skip).limit(limit).all()

        return professionals, total

    def get_by_role(self, role: ProfessionalRole) -> List[Professional]:
        """Lista todos os profissionais de uma função específica."""
        return (
            self.db.query(Professional)
            .filter(and_(Professional.role == role, Professional.is_active == True))  # noqa: E712
            .order_by(Professional.name)
            .all()
        )

    def get_by_organization(self, organization: str) -> List[Professional]:
        """Lista todos os profissionais de uma organização."""
        return (
            self.db.query(Professional)
            .filter(
                and_(
                    Professional.organization.ilike(f"%{organization}%"),
                    Professional.is_active == True,  # noqa: E712
                )
            )
            .order_by(Professional.name)
            .all()
        )

    def get_statistics(self) -> ProfessionalStatistics:
        """
        Obtém estatísticas de profissionais no sistema.

        Returns:
            Estatísticas agregadas
        """
        # Total de profissionais
        total = self.db.query(Professional).count()
        total_active = self.db.query(Professional).filter(Professional.is_active == True).count()  # noqa: E712
        total_inactive = total - total_active

        # Por role
        by_role_query = self.db.query(Professional.role, func.count(Professional.id)).group_by(Professional.role).all()
        by_role = {str(role): count for role, count in by_role_query}

        # Profissionais de educação vs saúde
        education_roles = [
            ProfessionalRole.TEACHER,
            ProfessionalRole.SPECIAL_EDUCATOR,
            ProfessionalRole.SCHOOL_COORDINATOR,
            ProfessionalRole.SCHOOL_MANAGER,
            ProfessionalRole.PSYCHOPEDAGOGIST,
        ]
        health_roles = [
            ProfessionalRole.PSYCHOLOGIST,
            ProfessionalRole.PSYCHIATRIST,
            ProfessionalRole.NEUROPEDIATRICIAN,
            ProfessionalRole.OCCUPATIONAL_THERAPIST,
            ProfessionalRole.SPEECH_THERAPIST,
            ProfessionalRole.PHYSIOTHERAPIST,
        ]

        education_count = self.db.query(Professional).filter(Professional.role.in_(education_roles)).count()
        health_count = self.db.query(Professional).filter(Professional.role.in_(health_roles)).count()

        # Número de organizações distintas
        organizations_count = self.db.query(func.count(func.distinct(Professional.organization))).scalar()

        return ProfessionalStatistics(
            total_professionals=total,
            total_active=total_active,
            total_inactive=total_inactive,
            by_role=by_role,
            education_professionals=education_count,
            health_professionals=health_count,
            organizations_count=organizations_count,
        )
