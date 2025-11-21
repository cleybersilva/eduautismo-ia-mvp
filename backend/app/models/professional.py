"""
Professional model - Profissionais que acompanham estudantes.

Suporta profissionais de Educação e Saúde em um sistema multiprofissional integrado.
"""

import enum
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.observation import ProfessionalObservation
    from app.models.socioemotional_indicator import SocialEmotionalIndicator


class ProfessionalRole(str, enum.Enum):
    """Tipos de profissionais no sistema."""

    # Educação
    TEACHER = "teacher"
    SPECIAL_EDUCATOR = "special_educator"
    SCHOOL_COORDINATOR = "school_coordinator"
    SCHOOL_MANAGER = "school_manager"
    PSYCHOPEDAGOGIST = "psychopedagogist"

    # Saúde
    PSYCHOLOGIST = "psychologist"
    PSYCHIATRIST = "psychiatrist"
    NEUROPEDIATRICIAN = "neuropediatrician"
    OCCUPATIONAL_THERAPIST = "occupational_therapist"
    SPEECH_THERAPIST = "speech_therapist"
    PHYSIOTHERAPIST = "physiotherapist"

    # Outros
    SOCIAL_WORKER = "social_worker"
    NUTRITIONIST = "nutritionist"


class Professional(BaseModel):
    """
    Profissional que acompanha estudantes no sistema.

    Suporta múltiplos tipos de profissionais de Educação e Saúde,
    permitindo colaboração multiprofissional integrada.
    """

    __tablename__ = "professionals"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    role: Mapped[ProfessionalRole] = mapped_column(
        SQLEnum(ProfessionalRole, name="professional_role"), nullable=False, index=True
    )
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relacionamentos
    observations: Mapped[List["ProfessionalObservation"]] = relationship(
        "ProfessionalObservation", back_populates="professional", cascade="all, delete-orphan", lazy="selectin"
    )
    socioemotional_indicators: Mapped[List["SocialEmotionalIndicator"]] = relationship(
        "SocialEmotionalIndicator", back_populates="professional", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Professional(id={self.id}, name={self.name}, role={self.role})>"

    @property
    def role_display(self) -> str:
        """Retorna nome legível da função profissional."""
        role_names = {
            ProfessionalRole.TEACHER: "Professor(a)",
            ProfessionalRole.SPECIAL_EDUCATOR: "Educador(a) Especial",
            ProfessionalRole.SCHOOL_COORDINATOR: "Coordenador(a) Pedagógico(a)",
            ProfessionalRole.SCHOOL_MANAGER: "Gestor(a) Escolar",
            ProfessionalRole.PSYCHOPEDAGOGIST: "Psicopedagoga(o)",
            ProfessionalRole.PSYCHOLOGIST: "Psicóloga(o)",
            ProfessionalRole.PSYCHIATRIST: "Psiquiatra",
            ProfessionalRole.NEUROPEDIATRICIAN: "Neuropediatra",
            ProfessionalRole.OCCUPATIONAL_THERAPIST: "Terapeuta Ocupacional",
            ProfessionalRole.SPEECH_THERAPIST: "Fonoaudióloga(o)",
            ProfessionalRole.PHYSIOTHERAPIST: "Fisioterapeuta",
            ProfessionalRole.SOCIAL_WORKER: "Assistente Social",
            ProfessionalRole.NUTRITIONIST: "Nutricionista",
        }
        return role_names.get(self.role, str(self.role))

    @property
    def is_education_professional(self) -> bool:
        """Verifica se é profissional da área de Educação."""
        education_roles = {
            ProfessionalRole.TEACHER,
            ProfessionalRole.SPECIAL_EDUCATOR,
            ProfessionalRole.SCHOOL_COORDINATOR,
            ProfessionalRole.SCHOOL_MANAGER,
            ProfessionalRole.PSYCHOPEDAGOGIST,
        }
        return self.role in education_roles

    @property
    def is_health_professional(self) -> bool:
        """Verifica se é profissional da área de Saúde."""
        health_roles = {
            ProfessionalRole.PSYCHOLOGIST,
            ProfessionalRole.PSYCHIATRIST,
            ProfessionalRole.NEUROPEDIATRICIAN,
            ProfessionalRole.OCCUPATIONAL_THERAPIST,
            ProfessionalRole.SPEECH_THERAPIST,
            ProfessionalRole.PHYSIOTHERAPIST,
        }
        return self.role in health_roles
