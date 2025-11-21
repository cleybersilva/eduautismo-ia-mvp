"""
Professional Observation model - Observações de profissionais sobre estudantes.

Permite que diferentes profissionais registrem observações comportamentais,
socioemocionais e de desenvolvimento.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.db.base import Base


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


class ProfessionalObservation(Base):
    """
    Observação registrada por profissional sobre estudante.

    Permite registro estruturado de observações multiprofissionais
    com indicadores comportamentais e socioemocionais.
    """

    __tablename__ = "professional_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relacionamentos
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    professional_id = Column(UUID(as_uuid=True), ForeignKey("professionals.id"), nullable=False, index=True)

    # Dados da observação
    observation_type = Column(Enum(ObservationType), nullable=False, index=True)
    context = Column(Enum(ObservationContext), nullable=False)
    content = Column(Text, nullable=False)

    # Indicadores estruturados
    behavioral_indicators = Column(
        JSON,
        nullable=True,
        comment="Indicadores comportamentais observados",
    )
    socioemotional_indicators = Column(
        JSON,
        nullable=True,
        comment="Indicadores socioemocionais observados",
    )

    # Classificação e urgência
    severity_level = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Nível de severidade/urgência: 1 (baixo) a 5 (crítico)",
    )
    requires_intervention = Column(Boolean, default=False, nullable=False, comment="Requer intervenção imediata")

    # Privacidade e acesso
    is_private = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Visível apenas para profissionais de saúde autorizados",
    )

    # Metadados
    tags = Column(JSON, nullable=True, comment="Tags para categorização e busca")
    attachments = Column(JSON, nullable=True, comment="URLs de anexos (fotos, vídeos, docs)")

    # Timestamps
    observed_at = Column(DateTime(timezone=True), nullable=False, comment="Data/hora da observação")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos ORM
    student = relationship("Student", back_populates="observations")
    professional = relationship("Professional", back_populates="observations")

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
