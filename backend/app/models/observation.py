"""
Professional Observation model - Observações de profissionais sobre estudantes.

Permite que diferentes profissionais registrem observações comportamentais,
socioemocionais e de desenvolvimento.
"""

import enum
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.types import GUID, PortableJSON

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.professional import Professional


class ObservationType(str, enum.Enum):
    """Tipos de observação profissional."""

    BEHAVIORAL = "behavioral"  # Comportamental
    ACADEMIC = "academic"  # Acadêmica/Pedagógica
    SOCIAL = "social"  # Interação Social
    EMOTIONAL = "emotional"  # Socioemocional
    SENSORY = "sensory"  # Sensorial
    COMMUNICATION = "communication"  # Comunicação
    MOTOR = "motor"  # Motor/Físico
    CLINICAL = "clinical"  # Clínica (profissionais de saúde)
    GENERAL = "general"  # Observação Geral


class ObservationContext(str, enum.Enum):
    """Contexto onde a observação foi realizada."""

    CLASSROOM = "classroom"  # Sala de aula
    RECESS = "recess"  # Recreio
    PE_CLASS = "pe_class"  # Educação Física
    THERAPY = "therapy"  # Sessão terapêutica
    LUNCH = "lunch"  # Hora do almoço
    TRANSITION = "transition"  # Transição entre atividades
    GROUP_ACTIVITY = "group_activity"  # Atividade em grupo
    INDIVIDUAL_ACTIVITY = "individual_activity"  # Atividade individual
    HOME = "home"  # Casa (relato familiar)
    OTHER = "other"  # Outro contexto


class ProfessionalObservation(BaseModel):
    """
    Observação registrada por profissional sobre estudante.

    Permite registro estruturado de observações multiprofissionais
    com indicadores comportamentais e socioemocionais.
    """

    __tablename__ = "professional_observations"

    # Relacionamentos
    student_id: Mapped[GUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    professional_id: Mapped[GUID] = mapped_column(
        ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Dados da observação
    observation_type: Mapped[ObservationType] = mapped_column(
        SQLEnum(ObservationType, name="observation_type"), nullable=False, index=True
    )
    context: Mapped[ObservationContext] = mapped_column(
        SQLEnum(ObservationContext, name="observation_context"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Indicadores estruturados
    behavioral_indicators: Mapped[Dict[str, Any] | None] = mapped_column(PortableJSON, nullable=True)
    socioemotional_indicators: Mapped[Dict[str, Any] | None] = mapped_column(PortableJSON, nullable=True)

    # Classificação e urgência
    severity_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    requires_intervention: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Privacidade e acesso
    is_private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Metadados
    tags: Mapped[List[str] | None] = mapped_column(PortableJSON, nullable=True)
    attachments: Mapped[List[str] | None] = mapped_column(PortableJSON, nullable=True)

    # Timestamps adicionais
    observed_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relacionamentos ORM
    student: Mapped["Student"] = relationship("Student", back_populates="observations", lazy="selectin")
    professional: Mapped["Professional"] = relationship("Professional", back_populates="observations", lazy="selectin")

    def __repr__(self):
        return (
            f"<ProfessionalObservation(id={self.id}, " f"type={self.observation_type}, severity={self.severity_level})>"
        )

    @property
    def requires_immediate_attention(self) -> bool:
        """Determina se observação requer atenção imediata."""
        return self.severity_level >= 4 or self.requires_intervention

    @property
    def is_accessible_by_education_only(self) -> bool:
        """Determina se observação é acessível apenas por profissionais de educação."""
        return not self.is_private and self.observation_type in {
            ObservationType.ACADEMIC,
            ObservationType.BEHAVIORAL,
            ObservationType.GENERAL,
        }
