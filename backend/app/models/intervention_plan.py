"""
Intervention Plan model - Planos de intervenção multiprofissional.

Permite criação e acompanhamento de planos de intervenção colaborativos
entre diferentes profissionais.
"""

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, Table
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.db.base import Base


class PlanStatus(str, enum.Enum):
    """Status do plano de intervenção."""

    DRAFT = "draft"  # Rascunho
    ACTIVE = "active"  # Ativo
    PAUSED = "paused"  # Pausado
    COMPLETED = "completed"  # Concluído
    CANCELLED = "cancelled"  # Cancelado


class ReviewFrequency(str, enum.Enum):
    """Frequência de revisão do plano."""

    DAILY = "daily"  # Diária
    WEEKLY = "weekly"  # Semanal
    BIWEEKLY = "biweekly"  # Quinzenal
    MONTHLY = "monthly"  # Mensal
    QUARTERLY = "quarterly"  # Trimestral


# Tabela de associação many-to-many entre InterventionPlan e Professional
intervention_plan_professionals = Table(
    "intervention_plan_professionals",
    Base.metadata,
    Column("intervention_plan_id", UUID(as_uuid=True), ForeignKey("intervention_plans.id")),
    Column("professional_id", UUID(as_uuid=True), ForeignKey("professionals.id")),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),
)


class InterventionPlan(Base):
    """
    Plano de intervenção multiprofissional para estudante.

    Permite colaboração entre diferentes profissionais para definir
    objetivos, estratégias e acompanhar progresso.
    """

    __tablename__ = "intervention_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relacionamentos
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("professionals.id"),
        nullable=False,
        comment="Profissional que criou o plano",
    )

    # Dados do plano
    title = Column(String(500), nullable=False)
    objective = Column(Text, nullable=False, comment="Objetivo principal do plano")
    description = Column(Text, nullable=True, comment="Descrição detalhada")

    # Estratégias e ações
    strategies = Column(
        JSON,
        nullable=False,
        comment="Lista de estratégias a serem implementadas",
    )
    target_behaviors = Column(
        JSON,
        nullable=False,
        comment="Comportamentos-alvo a serem desenvolvidos/modificados",
    )
    success_criteria = Column(
        JSON,
        nullable=False,
        comment="Critérios mensuráveis de sucesso",
    )

    # Período e acompanhamento
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    review_frequency = Column(
        Enum(ReviewFrequency),
        nullable=False,
        default=ReviewFrequency.WEEKLY,
    )

    # Status e progresso
    status = Column(
        Enum(PlanStatus),
        nullable=False,
        default=PlanStatus.DRAFT,
        index=True,
    )
    progress_percentage = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Percentual de progresso (0-100)",
    )
    progress_notes = Column(
        JSON,
        nullable=True,
        comment="Notas de progresso por data/profissional",
    )

    # Materiais e recursos
    required_materials = Column(JSON, nullable=True, comment="Materiais necessários")
    resources = Column(JSON, nullable=True, comment="Recursos adicionais")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos ORM
    student = relationship("Student", back_populates="intervention_plans")
    created_by = relationship("Professional", foreign_keys=[created_by_id])
    professionals_involved = relationship(
        "Professional",
        secondary=intervention_plan_professionals,
        backref="intervention_plans",
    )

    def __repr__(self):
        return f"<InterventionPlan(id={self.id}, title={self.title}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Verifica se plano está ativo."""
        return self.status == PlanStatus.ACTIVE

    @property
    def days_remaining(self) -> int:
        """Calcula dias restantes até o fim do plano."""
        from datetime import date

        if self.end_date < date.today():
            return 0
        return (self.end_date - date.today()).days

    @property
    def needs_review(self) -> bool:
        """Determina se plano precisa de revisão baseado na frequência."""
        from datetime import date, timedelta

        if not self.last_reviewed_at:
            return True

        frequency_days = {
            ReviewFrequency.DAILY: 1,
            ReviewFrequency.WEEKLY: 7,
            ReviewFrequency.BIWEEKLY: 14,
            ReviewFrequency.MONTHLY: 30,
            ReviewFrequency.QUARTERLY: 90,
        }

        days_since_review = (date.today() - self.last_reviewed_at.date()).days
        return days_since_review >= frequency_days.get(self.review_frequency, 7)
