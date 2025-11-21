"""
Social Emotional Indicator model - Indicadores socioemocionais de estudantes.

Permite monitoramento estruturado de aspectos socioemocionais e comportamentais
fundamentais para estudantes com TEA.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.professional import Professional


class IndicatorType(str, enum.Enum):
    """Tipos de indicadores socioemocionais monitorados."""

    EMOTIONAL_REGULATION = "emotional_regulation"  # Regulação Emocional
    SOCIAL_INTERACTION = "social_interaction"  # Interação Social
    COMMUNICATION_SKILLS = "communication_skills"  # Habilidades Comunicativas
    ADAPTIVE_BEHAVIOR = "adaptive_behavior"  # Comportamento Adaptativo
    SENSORY_PROCESSING = "sensory_processing"  # Processamento Sensorial
    ATTENTION_FOCUS = "attention_focus"  # Atenção e Foco
    ANXIETY_LEVEL = "anxiety_level"  # Nível de Ansiedade
    FRUSTRATION_TOLERANCE = "frustration_tolerance"  # Tolerância à Frustração
    SELF_REGULATION = "self_regulation"  # Autorregulação
    PEER_RELATIONSHIP = "peer_relationship"  # Relacionamento com Pares
    EXECUTIVE_FUNCTION = "executive_function"  # Função Executiva
    FLEXIBILITY = "flexibility"  # Flexibilidade Cognitiva/Comportamental


class MeasurementContext(str, enum.Enum):
    """Contexto da medição do indicador."""

    CLASSROOM = "classroom"  # Sala de aula
    RECESS = "recess"  # Recreio
    THERAPY_SESSION = "therapy_session"  # Sessão terapêutica
    GROUP_ACTIVITY = "group_activity"  # Atividade em grupo
    INDIVIDUAL_ACTIVITY = "individual_activity"  # Atividade individual
    TRANSITION = "transition"  # Transição entre atividades
    STRUCTURED_TASK = "structured_task"  # Tarefa estruturada
    UNSTRUCTURED_TIME = "unstructured_time"  # Tempo não estruturado
    HOME = "home"  # Casa
    OTHER = "other"  # Outro


class SocialEmotionalIndicator(BaseModel):
    """
    Indicador socioemocional medido para estudante.

    Permite monitoramento longitudinal de aspectos socioemocionais
    críticos para desenvolvimento de estudantes com TEA.
    """

    __tablename__ = "socioemotional_indicators"

    # Relacionamentos
    student_id: Mapped[GUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    professional_id: Mapped[GUID] = mapped_column(
        ForeignKey("professionals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e contexto
    indicator_type: Mapped[IndicatorType] = mapped_column(
        SQLEnum(IndicatorType, name="indicator_type"), nullable=False, index=True
    )
    context: Mapped[MeasurementContext] = mapped_column(
        SQLEnum(MeasurementContext, name="measurement_context"), nullable=False
    )

    # Medição
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Observações qualitativas
    observations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    specific_behaviors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Fatores contextuais
    environmental_factors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    triggers: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    supports_used: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps adicionais
    measured_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
    )

    # Relacionamentos ORM
    student: Mapped["Student"] = relationship("Student", back_populates="socioemotional_indicators", lazy="selectin")
    professional: Mapped["Professional"] = relationship(
        "Professional", back_populates="socioemotional_indicators", lazy="selectin"
    )

    def __repr__(self):
        return f"<SocialEmotionalIndicator(id={self.id}, " f"type={self.indicator_type}, score={self.score})>"

    @property
    def score_level(self) -> str:
        """Retorna nível qualitativo baseado no score."""
        if self.score <= 2:
            return "Muito Baixo"
        elif self.score <= 4:
            return "Baixo"
        elif self.score <= 6:
            return "Moderado"
        elif self.score <= 8:
            return "Alto"
        else:
            return "Muito Alto"

    @property
    def is_concerning(self) -> bool:
        """
        Determina se indicador é preocupante.

        Para indicadores positivos (como regulação emocional), scores baixos são preocupantes.
        Para indicadores negativos (como ansiedade), scores altos são preocupantes.
        """
        positive_indicators = {
            IndicatorType.EMOTIONAL_REGULATION,
            IndicatorType.SOCIAL_INTERACTION,
            IndicatorType.COMMUNICATION_SKILLS,
            IndicatorType.ADAPTIVE_BEHAVIOR,
            IndicatorType.ATTENTION_FOCUS,
            IndicatorType.FRUSTRATION_TOLERANCE,
            IndicatorType.SELF_REGULATION,
            IndicatorType.PEER_RELATIONSHIP,
            IndicatorType.FLEXIBILITY,
        }

        if self.indicator_type in positive_indicators:
            return self.score <= 4  # Score baixo é preocupante
        else:
            return self.score >= 7  # Score alto é preocupante

    @property
    def indicator_display_name(self) -> str:
        """Retorna nome legível do indicador."""
        names = {
            IndicatorType.EMOTIONAL_REGULATION: "Regulação Emocional",
            IndicatorType.SOCIAL_INTERACTION: "Interação Social",
            IndicatorType.COMMUNICATION_SKILLS: "Habilidades Comunicativas",
            IndicatorType.ADAPTIVE_BEHAVIOR: "Comportamento Adaptativo",
            IndicatorType.SENSORY_PROCESSING: "Processamento Sensorial",
            IndicatorType.ATTENTION_FOCUS: "Atenção e Foco",
            IndicatorType.ANXIETY_LEVEL: "Nível de Ansiedade",
            IndicatorType.FRUSTRATION_TOLERANCE: "Tolerância à Frustração",
            IndicatorType.SELF_REGULATION: "Autorregulação",
            IndicatorType.PEER_RELATIONSHIP: "Relacionamento com Pares",
            IndicatorType.EXECUTIVE_FUNCTION: "Função Executiva",
            IndicatorType.FLEXIBILITY: "Flexibilidade",
        }
        return names.get(self.indicator_type, str(self.indicator_type))
