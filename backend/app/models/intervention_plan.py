"""
Intervention Plan model - Planos de intervenção multiprofissional.

Permite criação e acompanhamento de planos de intervenção colaborativos
entre diferentes profissionais.
"""

import enum
from datetime import date
from typing import Any, Dict, List, TYPE_CHECKING

from sqlalchemy import Boolean, Date, Integer, String, Text, Table, Column, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel
from app.db.types import GUID, PortableJSON

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.professional import Professional


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
    Column("intervention_plan_id", GUID, ForeignKey("intervention_plans.id", ondelete="CASCADE")),
    Column("professional_id", GUID, ForeignKey("professionals.id", ondelete="CASCADE")),
)


class InterventionPlan(BaseModel):
    """
    Plano de intervenção multiprofissional para estudante.

    Permite colaboração entre diferentes profissionais para definir
    objetivos, estratégias e acompanhar progresso.
    """

    __tablename__ = "intervention_plans"

    # Relacionamentos
    student_id: Mapped[GUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id: Mapped[GUID] = mapped_column(
        ForeignKey("professionals.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Dados do plano
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Estratégias e ações
    strategies: Mapped[List[Dict[str, Any]]] = mapped_column(PortableJSON, nullable=False)
    target_behaviors: Mapped[List[str]] = mapped_column(PortableJSON, nullable=False)
    success_criteria: Mapped[List[str]] = mapped_column(PortableJSON, nullable=False)

    # Período e acompanhamento
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    review_frequency: Mapped[ReviewFrequency] = mapped_column(
        SQLEnum(ReviewFrequency, name="review_frequency"),
        nullable=False,
        default=ReviewFrequency.WEEKLY,
    )

    # Status e progresso
    status: Mapped[PlanStatus] = mapped_column(
        SQLEnum(PlanStatus, name="plan_status"),
        nullable=False,
        default=PlanStatus.DRAFT,
        index=True,
    )
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    progress_notes: Mapped[Dict[str, Any] | None] = mapped_column(PortableJSON, nullable=True)
    needs_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Materiais e recursos
    required_materials: Mapped[List[str] | None] = mapped_column(PortableJSON, nullable=True)
    resources: Mapped[Dict[str, Any] | None] = mapped_column(PortableJSON, nullable=True)

    # Campo adicional para last_reviewed_at
    last_reviewed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relacionamentos ORM
    student: Mapped["Student"] = relationship("Student", back_populates="intervention_plans", lazy="selectin")
    created_by: Mapped["Professional"] = relationship("Professional", foreign_keys=[created_by_id], lazy="selectin")
    professionals_involved: Mapped[List["Professional"]] = relationship(
        "Professional",
        secondary=intervention_plan_professionals,
        backref="intervention_plans",
        lazy="selectin",
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
        from datetime import date as dt_date

        today = dt_date.today()
        if self.end_date < today:
            return 0
        return (self.end_date - today).days

    @property
    def is_overdue(self) -> bool:
        """Verifica se plano está atrasado."""
        from datetime import date as dt_date

        return self.end_date < dt_date.today() and self.status not in [PlanStatus.COMPLETED, PlanStatus.CANCELLED]

    def calculate_needs_review(self) -> bool:
        """
        Calcula se o plano precisa de revisão baseado na frequência configurada.

        Lógica:
        - Se nunca foi revisado (last_reviewed_at is None), sempre precisa revisão
        - Se foi revisado, verifica se passou o período da frequência configurada

        Returns:
            bool: True se precisa revisão, False caso contrário
        """
        from datetime import date as dt_date, timedelta

        # Planos não ativos não precisam revisão
        if self.status != PlanStatus.ACTIVE:
            return False

        # Se nunca foi revisado, precisa revisão
        if self.last_reviewed_at is None:
            return True

        # Calcula dias desde última revisão
        days_since_review = (dt_date.today() - self.last_reviewed_at).days

        # Define limites por frequência
        frequency_days = {
            ReviewFrequency.DAILY: 1,
            ReviewFrequency.WEEKLY: 7,
            ReviewFrequency.BIWEEKLY: 14,
            ReviewFrequency.MONTHLY: 30,
            ReviewFrequency.QUARTERLY: 90,
        }

        threshold = frequency_days.get(self.review_frequency, 7)  # Default: weekly

        return days_since_review >= threshold

    def update_needs_review(self) -> bool:
        """
        Atualiza o campo needs_review com valor calculado.

        Returns:
            bool: Valor atualizado de needs_review
        """
        self.needs_review = self.calculate_needs_review()
        return self.needs_review
