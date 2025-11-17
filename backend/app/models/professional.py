"""
Professional model - Profissionais que acompanham estudantes.

Suporta profissionais de Educação e Saúde em um sistema multiprofissional integrado.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid

from app.db.base import Base


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


class Professional(Base):
    """
    Profissional que acompanha estudantes no sistema.

    Suporta múltiplos tipos de profissionais de Educação e Saúde,
    permitindo colaboração multiprofissional integrada.
    """

    __tablename__ = "professionals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(Enum(ProfessionalRole), nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    organization = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
