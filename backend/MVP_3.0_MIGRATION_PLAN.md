# 📋 MVP 3.0: Plano de Migração para Plataforma Multidisciplinar

**Versão**: 3.0.0
**Data de Criação**: 2025-11-30
**Autor**: Cleyber Silva
**Status**: PLANEJAMENTO

---

## 📊 RESUMO EXECUTIVO

### Objetivo

Transformar o EduAutismo IA de uma plataforma de atividades TEA genéricas em uma **Plataforma Multidisciplinar Inteligente** que permita aos professores criar atividades curriculares para Matemática, Português, Ciências, História, Geografia, Arte e Educação Física, **alinhadas à BNCC**.

### Escopo da Migração

| Componente | Mudanças | Complexidade | Tempo Estimado |
|------------|----------|--------------|----------------|
| **1. Enums e Constants** | Adicionar Subject + GradeLevel | Baixa | 2h |
| **2. Models (SQLAlchemy)** | Expandir Activity model | Baixa | 3h |
| **3. Schemas (Pydantic)** | Atualizar DTOs | Baixa | 2h |
| **4. Database Migration** | Adicionar colunas | Baixa | 2h |
| **5. NLP Service** | Atualizar prompts IA | Média | 8h |
| **6. API Endpoints** | Novos filtros | Baixa | 4h |
| **7. Testes** | Adicionar cobertura | Média | 8h |
| **8. Documentação** | Atualizar guias | Baixa | 4h |
| **TOTAL** | - | **Média** | **~33h (~1 semana)** |

### Princípios da Migração

✅ **100% Backwards-Compatible**: Atividades antigas continuam funcionando
✅ **Incremental**: Pode ser feito em sprints pequenos
✅ **Testado**: Cada mudança tem testes
✅ **Documentado**: Código autodocumentado + guias

---

## 🎯 SPRINT 1: Enums e Estruturas de Dados (2 dias)

### Objetivo
Criar as estruturas de dados que suportarão disciplinas e séries escolares.

### 1.1. Adicionar Enums de Disciplinas

**Arquivo**: `backend/app/utils/constants.py`

```python
# ============================================================================
# Academic Subjects (NOVO v3.0)
# ============================================================================

class Subject(str, Enum):
    """
    Disciplinas escolares alinhadas à BNCC.

    Categorias:
    - Educação Infantil: Campos de experiência
    - Fundamental I e II: Disciplinas curriculares
    - Ensino Médio: Áreas de conhecimento
    """

    # Educação Infantil (Campos de Experiência BNCC)
    INFANTIL_SELF_OTHERS = "infantil_self_others"  # O eu, o outro e o nós
    INFANTIL_BODY_MOVEMENT = "infantil_body_movement"  # Corpo, gestos e movimentos
    INFANTIL_SOUNDS_RHYTHM = "infantil_sounds_rhythm"  # Traços, sons, cores e formas
    INFANTIL_ORAL_WRITTEN = "infantil_oral_written"  # Escuta, fala, pensamento e imaginação
    INFANTIL_SPACES_QUANTITIES = "infantil_spaces_quantities"  # Espaços, tempos, quantidades

    # Ensino Fundamental I e II
    MATEMATICA = "matematica"
    PORTUGUES = "portugues"
    CIENCIAS = "ciencias"
    HISTORIA = "historia"
    GEOGRAFIA = "geografia"
    ARTE = "arte"
    EDUCACAO_FISICA = "educacao_fisica"
    INGLES = "ingles"

    # Ensino Médio (Áreas de Conhecimento)
    BIOLOGIA = "biologia"
    FISICA = "fisica"
    QUIMICA = "quimica"
    FILOSOFIA = "filosofia"
    SOCIOLOGIA = "sociologia"
    LITERATURA = "literatura"
    REDACAO = "redacao"

    @classmethod
    def get_by_grade_level(cls, grade_level: str) -> List["Subject"]:
        """
        Retorna disciplinas disponíveis para um nível escolar.

        Args:
            grade_level: Nível escolar (ex: "fundamental_1_3ano")

        Returns:
            Lista de disciplinas aplicáveis
        """
        if "infantil" in grade_level:
            return [
                cls.INFANTIL_SELF_OTHERS,
                cls.INFANTIL_BODY_MOVEMENT,
                cls.INFANTIL_SOUNDS_RHYTHM,
                cls.INFANTIL_ORAL_WRITTEN,
                cls.INFANTIL_SPACES_QUANTITIES,
            ]

        if "fundamental_1" in grade_level or "fundamental_2" in grade_level:
            subjects = [
                cls.MATEMATICA,
                cls.PORTUGUES,
                cls.CIENCIAS,
                cls.HISTORIA,
                cls.GEOGRAFIA,
                cls.ARTE,
                cls.EDUCACAO_FISICA,
            ]
            # Inglês a partir do 6º ano
            if "fundamental_2" in grade_level:
                subjects.append(cls.INGLES)
            return subjects

        if "medio" in grade_level:
            return [
                cls.MATEMATICA,
                cls.PORTUGUES,
                cls.BIOLOGIA,
                cls.FISICA,
                cls.QUIMICA,
                cls.HISTORIA,
                cls.GEOGRAFIA,
                cls.FILOSOFIA,
                cls.SOCIOLOGIA,
                cls.ARTE,
                cls.EDUCACAO_FISICA,
                cls.INGLES,
                cls.LITERATURA,
                cls.REDACAO,
            ]

        return []


# ============================================================================
# Grade Levels (NOVO v3.0)
# ============================================================================

class GradeLevel(str, Enum):
    """
    Níveis de ensino do sistema educacional brasileiro.

    Referência: LDB 9.394/96
    """

    # Educação Infantil (0-5 anos)
    CRECHE_0_1 = "creche_0_1"  # Berçário I
    CRECHE_1_2 = "creche_1_2"  # Berçário II
    CRECHE_2_3 = "creche_2_3"  # Maternal I
    PRE_ESCOLA_4 = "pre_escola_4"  # Pré I
    PRE_ESCOLA_5 = "pre_escola_5"  # Pré II

    # Ensino Fundamental I (6-10 anos)
    FUNDAMENTAL_1_ANO = "fundamental_1_ano"
    FUNDAMENTAL_2_ANO = "fundamental_2_ano"
    FUNDAMENTAL_3_ANO = "fundamental_3_ano"
    FUNDAMENTAL_4_ANO = "fundamental_4_ano"
    FUNDAMENTAL_5_ANO = "fundamental_5_ano"

    # Ensino Fundamental II (11-14 anos)
    FUNDAMENTAL_6_ANO = "fundamental_6_ano"
    FUNDAMENTAL_7_ANO = "fundamental_7_ano"
    FUNDAMENTAL_8_ANO = "fundamental_8_ano"
    FUNDAMENTAL_9_ANO = "fundamental_9_ano"

    # Ensino Médio (15-17 anos)
    MEDIO_1_ANO = "medio_1_ano"
    MEDIO_2_ANO = "medio_2_ano"
    MEDIO_3_ANO = "medio_3_ano"

    # EJA (Educação de Jovens e Adultos)
    EJA_FUNDAMENTAL_I = "eja_fundamental_i"
    EJA_FUNDAMENTAL_II = "eja_fundamental_ii"
    EJA_MEDIO = "eja_medio"

    @classmethod
    def get_age_range(cls, grade_level: "GradeLevel") -> Tuple[int, int]:
        """
        Retorna faixa etária típica para um nível escolar.

        Args:
            grade_level: Nível escolar

        Returns:
            Tupla (idade_min, idade_max)
        """
        age_ranges = {
            # Infantil
            cls.CRECHE_0_1: (0, 1),
            cls.CRECHE_1_2: (1, 2),
            cls.CRECHE_2_3: (2, 3),
            cls.PRE_ESCOLA_4: (4, 4),
            cls.PRE_ESCOLA_5: (5, 5),

            # Fundamental I
            cls.FUNDAMENTAL_1_ANO: (6, 6),
            cls.FUNDAMENTAL_2_ANO: (7, 7),
            cls.FUNDAMENTAL_3_ANO: (8, 8),
            cls.FUNDAMENTAL_4_ANO: (9, 9),
            cls.FUNDAMENTAL_5_ANO: (10, 10),

            # Fundamental II
            cls.FUNDAMENTAL_6_ANO: (11, 11),
            cls.FUNDAMENTAL_7_ANO: (12, 12),
            cls.FUNDAMENTAL_8_ANO: (13, 13),
            cls.FUNDAMENTAL_9_ANO: (14, 14),

            # Médio
            cls.MEDIO_1_ANO: (15, 15),
            cls.MEDIO_2_ANO: (16, 16),
            cls.MEDIO_3_ANO: (17, 17),

            # EJA
            cls.EJA_FUNDAMENTAL_I: (15, 99),
            cls.EJA_FUNDAMENTAL_II: (15, 99),
            cls.EJA_MEDIO: (18, 99),
        }
        return age_ranges.get(grade_level, (6, 18))

    @classmethod
    def get_education_level(cls, grade_level: "GradeLevel") -> str:
        """
        Retorna nível de ensino (Infantil, Fundamental I, etc.).

        Args:
            grade_level: Nível escolar

        Returns:
            Nome do nível de ensino
        """
        if grade_level.value.startswith("creche") or grade_level.value.startswith("pre_escola"):
            return "Educação Infantil"
        elif grade_level.value.startswith("fundamental_") and int(grade_level.value.split("_")[1][0]) <= 5:
            return "Ensino Fundamental I"
        elif grade_level.value.startswith("fundamental_"):
            return "Ensino Fundamental II"
        elif grade_level.value.startswith("medio"):
            return "Ensino Médio"
        elif grade_level.value.startswith("eja"):
            return "EJA"
        return "Indefinido"


# ============================================================================
# BNCC Structures (OPCIONAL MVP 3.0 - COMPLETO MVP 4.0)
# ============================================================================

class BNCCCompetencyArea(str, Enum):
    """Áreas de competência da BNCC."""

    LINGUAGENS = "linguagens"
    MATEMATICA = "matematica"
    CIENCIAS_NATUREZA = "ciencias_natureza"
    CIENCIAS_HUMANAS = "ciencias_humanas"
    ENSINO_RELIGIOSO = "ensino_religioso"


# ============================================================================
# Helper Functions (NOVO v3.0)
# ============================================================================

def get_subjects() -> List[str]:
    """Get list of all subjects."""
    return [subject.value for subject in Subject]


def get_grade_levels() -> List[str]:
    """Get list of all grade levels."""
    return [level.value for level in GradeLevel]


def get_subjects_for_grade(grade_level: str) -> List[str]:
    """
    Get applicable subjects for a grade level.

    Args:
        grade_level: Grade level code

    Returns:
        List of applicable subject codes
    """
    try:
        level = GradeLevel(grade_level)
        subjects = Subject.get_by_grade_level(grade_level)
        return [s.value for s in subjects]
    except ValueError:
        return []
```

**Checklist Sprint 1.1:**
- [ ] Copiar código acima para `constants.py`
- [ ] Adicionar imports necessários (`from typing import List, Tuple`)
- [ ] Executar linter: `flake8 app/utils/constants.py`
- [ ] Executar formatter: `black app/utils/constants.py`
- [ ] Commitar: `git commit -m "feat: adicionar enums Subject e GradeLevel para MVP 3.0"`

---

## 🗃️ SPRINT 2: Modelos de Dados (2 dias)

### Objetivo
Expandir o modelo `Activity` para suportar disciplinas e níveis escolares.

### 2.1. Atualizar Activity Model

**Arquivo**: `backend/app/models/activity.py`

```python
"""
Activity Model - EduAutismo IA v3.0

CHANGELOG v3.0:
- Adicionado campo 'subject' (disciplina)
- Adicionado campo 'grade_level' (série/ano)
- Adicionado campo 'bncc_competencies' (códigos BNCC)
- Adicionado campo 'bncc_skills' (habilidades BNCC)
- Adicionado campo 'knowledge_objects' (objetos de conhecimento)
- 100% backwards-compatible (todos os campos opcionais)
"""

from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.types import GUID, PortableJSON, StringArray
from app.utils.constants import ActivityType, DifficultyLevel, Subject, GradeLevel  # NOVO

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.student import Student
    from app.models.user import User


class Activity(BaseModel):
    """
    Activity model representing personalized educational activities.

    Activities are generated by AI based on student profiles and can be
    assessed for effectiveness.

    v3.0: Extended with multidisciplinary support and BNCC alignment.
    """

    __tablename__ = "activities"

    # Basic Information
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Activity Type and Difficulty
    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, name="activity_type"), nullable=False, index=True
    )

    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SQLEnum(DifficultyLevel, name="difficulty_level"), nullable=False
    )

    # ============================================================================
    # NOVO v3.0: Multidisciplinary Fields
    # ============================================================================

    subject: Mapped[Subject | None] = mapped_column(
        SQLEnum(Subject, name="subject"),
        nullable=True,
        index=True,
        comment="Disciplina curricular (Matemática, Português, etc.)"
    )

    grade_level: Mapped[GradeLevel | None] = mapped_column(
        SQLEnum(GradeLevel, name="grade_level"),
        nullable=True,
        index=True,
        comment="Ano/Série escolar (Fundamental 1º ano, etc.)"
    )

    # ============================================================================
    # NOVO v3.0: BNCC Alignment (Optional - MVP 4.0 completo)
    # ============================================================================

    bncc_competencies: Mapped[List[str] | None] = mapped_column(
        StringArray,
        nullable=True,
        comment="Códigos de competências BNCC (ex: EF01MA01)"
    )

    bncc_skills: Mapped[List[str] | None] = mapped_column(
        StringArray,
        nullable=True,
        comment="Códigos de habilidades BNCC"
    )

    knowledge_objects: Mapped[List[str] | None] = mapped_column(
        StringArray,
        nullable=True,
        comment="Objetos de conhecimento BNCC"
    )

    # ============================================================================
    # Existing Fields (unchanged)
    # ============================================================================

    # Duration
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Content
    objectives: Mapped[List[str]] = mapped_column(StringArray, nullable=False)
    materials: Mapped[List[str]] = mapped_column(StringArray, nullable=False)
    instructions: Mapped[List[str]] = mapped_column(StringArray, nullable=False)

    # Adaptations and Supports
    adaptations: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True)
    visual_supports: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True)
    success_criteria: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True)

    # Theme/Topic
    theme: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True, index=True)

    # Generation Metadata
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    generation_metadata: Mapped[Dict[str, Any] | None] = mapped_column(
        PortableJSON, nullable=True, comment="AI generation parameters and metadata"
    )

    # Resources
    resources_urls: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True)
    attachments: Mapped[List[str] | None] = mapped_column(StringArray, nullable=True)

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Foreign Keys
    student_id: Mapped[GUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id: Mapped[GUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="activities", lazy="selectin")
    created_by: Mapped["User"] = relationship("User", lazy="selectin")
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment", back_populates="activity", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation."""
        subject_info = f", subject={self.subject.value}" if self.subject else ""
        return f"<Activity(id={self.id}, title={self.title}, type={self.activity_type}{subject_info})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AI processing."""
        base_dict = {
            "title": self.title,
            "description": self.description,
            "type": self.activity_type.value,
            "difficulty": self.difficulty.value,
            "duration_minutes": self.duration_minutes,
            "objectives": self.objectives,
            "materials": self.materials,
            "instructions": self.instructions,
            "theme": self.theme,
        }

        # NOVO v3.0: Add multidisciplinary fields
        if self.subject:
            base_dict["subject"] = self.subject.value
        if self.grade_level:
            base_dict["grade_level"] = self.grade_level.value
        if self.bncc_competencies:
            base_dict["bncc_competencies"] = self.bncc_competencies
        if self.knowledge_objects:
            base_dict["knowledge_objects"] = self.knowledge_objects

        return base_dict

    # ============================================================================
    # NOVO v3.0: Helper Methods
    # ============================================================================

    @property
    def subject_name(self) -> str:
        """Get human-readable subject name."""
        subject_names = {
            Subject.MATEMATICA: "Matemática",
            Subject.PORTUGUES: "Português",
            Subject.CIENCIAS: "Ciências",
            Subject.HISTORIA: "História",
            Subject.GEOGRAFIA: "Geografia",
            Subject.ARTE: "Arte",
            Subject.EDUCACAO_FISICA: "Educação Física",
            Subject.INGLES: "Inglês",
            # ... adicionar outros
        }
        return subject_names.get(self.subject, self.subject.value if self.subject else "N/A")

    @property
    def grade_level_name(self) -> str:
        """Get human-readable grade level name."""
        if not self.grade_level:
            return "N/A"

        level_names = {
            GradeLevel.FUNDAMENTAL_1_ANO: "1º ano Fundamental",
            GradeLevel.FUNDAMENTAL_2_ANO: "2º ano Fundamental",
            GradeLevel.FUNDAMENTAL_3_ANO: "3º ano Fundamental",
            # ... adicionar outros
        }
        return level_names.get(self.grade_level, self.grade_level.value)

    def is_aligned_with_bncc(self) -> bool:
        """Check if activity has BNCC alignment."""
        return bool(self.bncc_competencies or self.bncc_skills or self.knowledge_objects)
```

**Checklist Sprint 2.1:**
- [ ] Atualizar `activity.py` com código acima
- [ ] Executar linter e formatter
- [ ] Testar imports: `python -c "from app.models.activity import Activity"`
- [ ] Commitar: `git commit -m "feat: expandir Activity model com campos multidisciplinares"`

---

## 💾 SPRINT 3: Database Migration (1 dia)

### Objetivo
Criar migration Alembic para adicionar novas colunas ao banco de dados.

### 3.1. Criar Migration

```bash
cd backend
alembic revision --autogenerate -m "add multidisciplinary fields to activities"
```

**Arquivo gerado**: `alembic/versions/YYYYMMDD_HHMM_add_multidisciplinary_fields.py`

```python
"""add multidisciplinary fields to activities

Revision ID: xxx
Revises: yyy
Create Date: 2025-11-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add multidisciplinary fields to activities table.

    NEW FIELDS:
    - subject: Enum (disciplina curricular)
    - grade_level: Enum (ano/série escolar)
    - bncc_competencies: ARRAY (códigos BNCC)
    - bncc_skills: ARRAY (habilidades BNCC)
    - knowledge_objects: ARRAY (objetos de conhecimento)

    BACKWARDS COMPATIBLE: All fields nullable
    """

    # Create Subject enum
    subject_enum = postgresql.ENUM(
        'infantil_self_others', 'infantil_body_movement', 'infantil_sounds_rhythm',
        'infantil_oral_written', 'infantil_spaces_quantities',
        'matematica', 'portugues', 'ciencias', 'historia', 'geografia',
        'arte', 'educacao_fisica', 'ingles',
        'biologia', 'fisica', 'quimica', 'filosofia', 'sociologia',
        'literatura', 'redacao',
        name='subject'
    )
    subject_enum.create(op.get_bind(), checkfirst=True)

    # Create GradeLevel enum
    grade_level_enum = postgresql.ENUM(
        'creche_0_1', 'creche_1_2', 'creche_2_3', 'pre_escola_4', 'pre_escola_5',
        'fundamental_1_ano', 'fundamental_2_ano', 'fundamental_3_ano',
        'fundamental_4_ano', 'fundamental_5_ano',
        'fundamental_6_ano', 'fundamental_7_ano', 'fundamental_8_ano', 'fundamental_9_ano',
        'medio_1_ano', 'medio_2_ano', 'medio_3_ano',
        'eja_fundamental_i', 'eja_fundamental_ii', 'eja_medio',
        name='grade_level'
    )
    grade_level_enum.create(op.get_bind(), checkfirst=True)

    # Add columns
    op.add_column('activities', sa.Column('subject', subject_enum, nullable=True))
    op.add_column('activities', sa.Column('grade_level', grade_level_enum, nullable=True))
    op.add_column('activities', sa.Column('bncc_competencies', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('activities', sa.Column('bncc_skills', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('activities', sa.Column('knowledge_objects', postgresql.ARRAY(sa.String()), nullable=True))

    # Create indexes for filtering
    op.create_index('ix_activities_subject', 'activities', ['subject'], unique=False)
    op.create_index('ix_activities_grade_level', 'activities', ['grade_level'], unique=False)


def downgrade() -> None:
    """Remove multidisciplinary fields."""

    # Drop indexes
    op.drop_index('ix_activities_grade_level', table_name='activities')
    op.drop_index('ix_activities_subject', table_name='activities')

    # Drop columns
    op.drop_column('activities', 'knowledge_objects')
    op.drop_column('activities', 'bncc_skills')
    op.drop_column('activities', 'bncc_competencies')
    op.drop_column('activities', 'grade_level')
    op.drop_column('activities', 'subject')

    # Drop enums
    sa.Enum(name='grade_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subject').drop(op.get_bind(), checkfirst=True)
```

**Checklist Sprint 3.1:**
- [ ] Gerar migration: `alembic revision --autogenerate -m "add multidisciplinary fields"`
- [ ] Revisar migration gerado
- [ ] Testar upgrade: `alembic upgrade head`
- [ ] Verificar no banco: `SELECT * FROM activities LIMIT 1;`
- [ ] Testar downgrade: `alembic downgrade -1`
- [ ] Testar upgrade novamente: `alembic upgrade head`
- [ ] Commitar: `git commit -m "feat: adicionar migration para campos multidisciplinares"`

---

## 📝 SPRINT 4: Schemas Pydantic (1 dia)

### Objetivo
Atualizar schemas de request/response para suportar novos campos.

### 4.1. Atualizar Activity Schemas

**Arquivo**: `backend/app/schemas/activity.py`

```python
"""
Activity Schemas - EduAutismo IA v3.0

CHANGELOG v3.0:
- Adicionado campos multidisciplinares nos schemas
- Novo schema ActivityGenerateMultidisciplinary
- Backward-compatible com schemas v2.0
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseResponseSchema, BaseSchema
from app.utils.constants import (
    MAX_ACTIVITY_DURATION,
    MIN_ACTIVITY_DURATION,
    ActivityType,
    DifficultyLevel,
    Subject,  # NOVO v3.0
    GradeLevel,  # NOVO v3.0
)


# ============================================================================
# NOVO v3.0: Multidisciplinary Activity Generation
# ============================================================================

class ActivityGenerateMultidisciplinary(BaseSchema):
    """
    Schema for generating multidisciplinary activity with AI (v3.0).

    NEW FIELDS:
    - subject: Disciplina curricular (Matemática, Português, etc.)
    - grade_level: Ano/série escolar
    - bncc_code: Código de competência BNCC (opcional)
    """

    student_id: UUID = Field(..., description="Student ID for personalization")

    # NOVO v3.0: Campos multidisciplinares
    subject: Subject = Field(..., description="Disciplina curricular")
    grade_level: GradeLevel = Field(..., description="Ano/série escolar")

    # Campos existentes
    activity_type: ActivityType = Field(..., description="Type of activity")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    duration_minutes: int = Field(
        ..., ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION, description="Duration in minutes"
    )
    theme: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional theme/topic",
        examples=["dinossauros", "sistema solar", "cores"],
    )

    # NOVO v3.0: BNCC alignment (opcional)
    bncc_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Código BNCC da competência desejada (ex: EF01MA01)",
        examples=["EF01MA01", "EF03LP01", "EI03EO01"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "subject": "matematica",
                "grade_level": "fundamental_3_ano",
                "activity_type": "cognitive",
                "difficulty": "medium",
                "duration_minutes": 30,
                "theme": "dinossauros",
                "bncc_code": "EF03MA06"
            }
        }


# ============================================================================
# Updated Existing Schemas (backwards-compatible)
# ============================================================================

class ActivityGenerate(BaseSchema):
    """
    Schema for generating activity with AI (v2.0 - mantido para compatibilidade).
    """

    student_id: UUID = Field(..., description="Student ID for personalization")
    activity_type: ActivityType = Field(..., description="Type of activity")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    duration_minutes: int = Field(
        ..., ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION, description="Duration in minutes"
    )
    theme: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional theme/topic",
        examples=["dinossauros", "sistema solar", "cores"],
    )


class ActivityCreate(BaseSchema):
    """Schema for creating activity manually (updated v3.0)."""

    student_id: UUID = Field(..., description="Student ID")
    title: str = Field(..., min_length=3, max_length=500, description="Activity title")
    description: str = Field(..., min_length=10, description="Activity description")
    activity_type: ActivityType = Field(default=ActivityType.COGNITIVE, description="Activity type")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY, description="Difficulty level")
    duration_minutes: int = Field(
        default=30, ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION, description="Duration in minutes"
    )
    objectives: List[str] = Field(..., description="Learning objectives")
    materials: List[str] = Field(..., description="Required materials")
    instructions: List[str] = Field(..., description="Step-by-step instructions")
    adaptations: Optional[List[str]] = Field(default=None, description="Adaptations")
    visual_supports: Optional[List[str]] = Field(default=None, description="Visual supports")
    success_criteria: Optional[List[str]] = Field(default=None, description="Success criteria")
    theme: Optional[str] = Field(default=None, max_length=255, description="Theme")
    tags: Optional[List[str]] = Field(default=None, description="Tags")

    # NOVO v3.0: Campos multidisciplinares
    subject: Optional[Subject] = Field(default=None, description="Disciplina curricular")
    grade_level: Optional[GradeLevel] = Field(default=None, description="Ano/série escolar")
    bncc_competencies: Optional[List[str]] = Field(default=None, description="Códigos BNCC competências")
    bncc_skills: Optional[List[str]] = Field(default=None, description="Códigos BNCC habilidades")
    knowledge_objects: Optional[List[str]] = Field(default=None, description="Objetos de conhecimento BNCC")

    @field_validator("objectives", "materials", "instructions", mode="before")
    @classmethod
    def validate_not_empty_list(cls, value: List[str]) -> List[str]:
        """Validate lists are not empty and contain non-whitespace items."""
        if not value:
            raise ValueError("Lista não pode estar vazia")

        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]

        if not cleaned:
            raise ValueError("Lista não pode estar vazia")

        return cleaned


class ActivityUpdate(BaseSchema):
    """Schema for updating activity (updated v3.0)."""

    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, min_length=10)
    activity_type: Optional[ActivityType] = Field(default=None)
    difficulty: Optional[DifficultyLevel] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=MIN_ACTIVITY_DURATION, le=MAX_ACTIVITY_DURATION)
    objectives: Optional[List[str]] = Field(default=None)
    materials: Optional[List[str]] = Field(default=None)
    instructions: Optional[List[str]] = Field(default=None)
    adaptations: Optional[List[str]] = Field(default=None)
    visual_supports: Optional[List[str]] = Field(default=None)
    success_criteria: Optional[List[str]] = Field(default=None)
    theme: Optional[str] = Field(default=None, max_length=255)
    tags: Optional[List[str]] = Field(default=None)
    is_published: Optional[bool] = Field(default=None)

    # NOVO v3.0
    subject: Optional[Subject] = Field(default=None)
    grade_level: Optional[GradeLevel] = Field(default=None)
    bncc_competencies: Optional[List[str]] = Field(default=None)
    bncc_skills: Optional[List[str]] = Field(default=None)
    knowledge_objects: Optional[List[str]] = Field(default=None)


class ActivityResponse(BaseResponseSchema):
    """Schema for activity response (updated v3.0)."""

    title: str
    description: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    duration_minutes: int
    objectives: List[str]
    materials: List[str]
    instructions: List[str]
    adaptations: Optional[List[str]] = None
    visual_supports: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    theme: Optional[str] = None
    tags: Optional[List[str]] = None
    generated_by_ai: bool
    generation_metadata: Optional[Dict[str, Any]] = None
    is_published: bool
    is_template: bool
    student_id: UUID
    created_by_id: Optional[UUID] = None

    # NOVO v3.0
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
    subject_name: Optional[str] = Field(default=None, description="Nome legível da disciplina")
    grade_level_name: Optional[str] = Field(default=None, description="Nome legível do ano/série")
    bncc_competencies: Optional[List[str]] = None
    bncc_skills: Optional[List[str]] = None
    knowledge_objects: Optional[List[str]] = None
    is_bncc_aligned: Optional[bool] = Field(default=None, description="Se tem alinhamento BNCC")


class ActivityListResponse(BaseResponseSchema):
    """Schema for activity in list (updated v3.0)."""

    title: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    duration_minutes: int
    theme: Optional[str] = None
    generated_by_ai: bool
    student_id: UUID

    # NOVO v3.0
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
    subject_name: Optional[str] = None
    grade_level_name: Optional[str] = None


class ActivityFilterParams(BaseSchema):
    """Query parameters for filtering activities (updated v3.0)."""

    activity_type: Optional[ActivityType] = Field(default=None, description="Filter by type")
    difficulty: Optional[DifficultyLevel] = Field(default=None, description="Filter by difficulty")
    theme: Optional[str] = Field(default=None, description="Filter by theme")
    generated_by_ai: Optional[bool] = Field(default=None, description="Filter AI-generated")
    student_id: Optional[UUID] = Field(default=None, description="Filter by student")

    # NOVO v3.0: Filtros multidisciplinares
    subject: Optional[Subject] = Field(default=None, description="Filter by subject")
    grade_level: Optional[GradeLevel] = Field(default=None, description="Filter by grade level")
    has_bncc: Optional[bool] = Field(default=None, description="Filter activities with BNCC alignment")
```

**Checklist Sprint 4.1:**
- [ ] Atualizar `activity.py` schemas
- [ ] Executar linter e formatter
- [ ] Testar imports
- [ ] Commitar: `git commit -m "feat: atualizar activity schemas com campos multidisciplinares"`

---

## 🤖 SPRINT 5: NLP Service - Prompts Multidisciplinares (3 dias)

### Objetivo
Atualizar o serviço de IA generativa (GPT-4o) para gerar atividades contextualizadas por disciplina e alinhadas à BNCC.

### 5.1. Atualizar NLP Service

**Arquivo**: `backend/app/services/nlp_service.py`

```python
"""
NLP Service - EduAutismo IA v3.0

CHANGELOG v3.0:
- Prompts contextualizados por disciplina
- Sugestões automáticas de objetivos BNCC
- Templates específicos por matéria
- Ajuste de linguagem por nível escolar
"""

from typing import Dict, List, Optional
import openai

from app.core.config import settings
from app.core.exceptions import NLPServiceError
from app.utils.constants import Subject, GradeLevel, ActivityType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NLPService:
    """Service for OpenAI GPT-4o integration with multidisciplinary support."""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    # ============================================================================
    # NOVO v3.0: Multidisciplinary Activity Generation
    # ============================================================================

    async def generate_multidisciplinary_activity(
        self,
        student_age: int,
        subject: Subject,
        grade_level: GradeLevel,
        activity_type: ActivityType,
        difficulty: str,
        duration_minutes: int,
        theme: Optional[str] = None,
        bncc_code: Optional[str] = None,
        cognitive_profile: Optional[Dict] = None,
        sensory_profile: Optional[Dict] = None,
        interests: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Generate multidisciplinary activity with BNCC alignment.

        Args:
            student_age: Student's age
            subject: Academic subject (Matemática, Português, etc.)
            grade_level: Grade level (Fundamental 3º ano, etc.)
            activity_type: Type of activity (cognitive, social, etc.)
            difficulty: Difficulty level
            duration_minutes: Activity duration
            theme: Optional theme to incorporate
            bncc_code: Optional BNCC competency code to target
            cognitive_profile: Student's cognitive abilities
            sensory_profile: Student's sensory preferences
            interests: Student's special interests

        Returns:
            Dictionary with activity content and BNCC alignment

        Raises:
            NLPServiceError: If generation fails
        """
        try:
            # Build subject-specific prompt
            prompt = self._build_multidisciplinary_prompt(
                student_age=student_age,
                subject=subject,
                grade_level=grade_level,
                activity_type=activity_type,
                difficulty=difficulty,
                duration_minutes=duration_minutes,
                theme=theme,
                bncc_code=bncc_code,
                cognitive_profile=cognitive_profile,
                sensory_profile=sensory_profile,
                interests=interests,
            )

            # Get subject-specific system prompt
            system_prompt = self._get_subject_system_prompt(subject, grade_level)

            logger.info(
                "Calling OpenAI API for multidisciplinary activity generation",
                extra={
                    "subject": subject.value,
                    "grade_level": grade_level.value,
                    "bncc_code": bncc_code,
                },
            )

            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
            )

            # Parse response
            content = response.choices[0].message.content
            parsed_content = self._parse_activity_response(content)

            # Add metadata
            parsed_content["generation_metadata"] = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "subject": subject.value,
                "grade_level": grade_level.value,
                "bncc_code": bncc_code,
                "version": "3.0",
            }

            logger.info(
                "Multidisciplinary activity generated successfully",
                extra={
                    "subject": subject.value,
                    "tokens_used": response.usage.total_tokens,
                    "has_bncc": bool(parsed_content.get("bncc_competencies")),
                },
            )

            return parsed_content

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise NLPServiceError(f"Failed to generate content: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error in NLP service: {str(e)}")
            raise NLPServiceError(f"Unexpected error: {str(e)}") from e

    # ============================================================================
    # NOVO v3.0: Subject-Specific Prompts
    # ============================================================================

    def _build_multidisciplinary_prompt(
        self,
        student_age: int,
        subject: Subject,
        grade_level: GradeLevel,
        activity_type: ActivityType,
        difficulty: str,
        duration_minutes: int,
        theme: Optional[str],
        bncc_code: Optional[str],
        cognitive_profile: Optional[Dict],
        sensory_profile: Optional[Dict],
        interests: Optional[List[str]],
    ) -> str:
        """Build detailed prompt for multidisciplinary activity generation."""

        # Get subject-specific context
        subject_context = self._get_subject_context(subject, grade_level)

        # Get BNCC context if code provided
        bncc_context = ""
        if bncc_code:
            bncc_context = self._get_bncc_context(bncc_code, subject, grade_level)

        prompt = f"""
Crie uma atividade pedagógica MULTIDISCIPLINAR personalizada para um aluno com TEA.

═══════════════════════════════════════════════════════════════
INFORMAÇÕES DO ALUNO
═══════════════════════════════════════════════════════════════

📚 **Perfil Acadêmico:**
- Idade: {student_age} anos
- Série/Ano: {self._format_grade_level(grade_level)}
- Diagnóstico: Transtorno do Espectro Autista (TEA)

🧠 **Perfil Cognitivo:**
{self._format_cognitive_profile(cognitive_profile)}

👂 **Perfil Sensorial:**
{self._format_sensory_profile(sensory_profile)}

🎯 **Interesses Especiais:**
{self._format_interests(interests)}

═══════════════════════════════════════════════════════════════
REQUISITOS DA ATIVIDADE
═══════════════════════════════════════════════════════════════

📖 **Disciplina:** {self._format_subject(subject)}
{subject_context}

📊 **Parâmetros:**
- Tipo de Atividade: {activity_type.value}
- Dificuldade: {difficulty}
- Duração: {duration_minutes} minutos
{f"- Tema para incorporar: {theme}" if theme else ""}

{bncc_context}

═══════════════════════════════════════════════════════════════
INSTRUÇÕES ESPECÍFICAS
═══════════════════════════════════════════════════════════════

**1. CONTEÚDO CURRICULAR:**
   - Seguir objetivos de aprendizagem da BNCC para {self._format_subject(subject)}
   - Adequar linguagem e complexidade ao {self._format_grade_level(grade_level)}
   - Incluir conceitos apropriados para a faixa etária

**2. ADAPTAÇÕES TEA:**
   - ✅ Instruções CLARAS e OBJETIVAS (passo a passo)
   - ✅ Rotina PREVISÍVEL (início, meio, fim bem definidos)
   - ✅ Apoios VISUAIS (cartões, imagens, diagramas)
   - ✅ Respeitar perfil SENSORIAL (evitar sobrecarga)
   - ✅ Incorporar INTERESSES ESPECIAIS quando possível
   - ✅ Dar opções de ESCOLHA (autonomia)

**3. ESTRUTURA DA ATIVIDADE:**
   - Título atrativo e claro
   - Objetivos de aprendizagem específicos
   - Lista de materiais necessários
   - Instruções passo a passo numeradas
   - Critérios de sucesso observáveis
   - Sugestões de adaptações adicionais

**4. FORMATO DE SAÍDA:**
   Responda em formato JSON válido com as seguintes chaves:
   {{
     "title": "Título da atividade",
     "description": "Descrição breve (2-3 frases)",
     "objectives": ["Objetivo 1", "Objetivo 2", ...],
     "materials": ["Material 1", "Material 2", ...],
     "instructions": ["Passo 1", "Passo 2", ...],
     "adaptations": ["Adaptação 1", "Adaptação 2", ...],
     "visual_supports": ["Apoio visual 1", "Apoio visual 2", ...],
     "success_criteria": ["Critério 1", "Critério 2", ...],
     "bncc_competencies": ["Código BNCC 1", ...],  // Se aplicável
     "knowledge_objects": ["Objeto de conhecimento 1", ...]  // Se aplicável
   }}

═══════════════════════════════════════════════════════════════
IMPORTANTE
═══════════════════════════════════════════════════════════════

⚠️ Esta atividade deve ser:
- ✅ **Inclusiva**: Adequada para aluno com TEA
- ✅ **Curricular**: Alinhada à BNCC e ao ano escolar
- ✅ **Motivadora**: Incorporar interesses quando possível
- ✅ **Estruturada**: Clara, previsível e com suporte visual
- ✅ **Respeitosa**: Valorizar as características do aluno

Agora, crie a atividade seguindo todas as diretrizes acima! 🎯
"""

        return prompt

    def _get_subject_system_prompt(self, subject: Subject, grade_level: GradeLevel) -> str:
        """Get system prompt specialized for subject and grade level."""

        base_prompt = """
Você é um ESPECIALISTA em educação especial e pedagogia inclusiva, com formação em:
- Transtorno do Espectro Autista (TEA)
- Metodologias ativas de ensino
- Base Nacional Comum Curricular (BNCC)
- Diferenciação pedagógica
"""

        # Add subject-specific expertise
        subject_expertise = {
            Subject.MATEMATICA: """
- Educação Matemática para alunos com TEA
- Materiais manipuláveis e representações visuais
- Resolução de problemas contextualizados
- Raciocínio lógico e pensamento computacional
""",
            Subject.PORTUGUES: """
- Alfabetização e letramento para alunos com TEA
- Comunicação alternativa e aumentativa
- Compreensão leitora e produção textual
- Gêneros textuais e oralidade
""",
            Subject.CIENCIAS: """
- Ensino de Ciências por investigação
- Experimentação segura e adaptada
- Método científico acessível
- Conexão com o cotidiano
""",
            Subject.HISTORIA: """
- Ensino de História contextualizado
- Linha do tempo visual
- Fontes históricas adaptadas
- Conexão passado-presente
""",
            Subject.GEOGRAFIA: """
- Alfabetização cartográfica
- Mapas e representações espaciais
- Relação local-global
- Sustentabilidade e meio ambiente
""",
            Subject.ARTE: """
- Expressão artística inclusiva
- Artes visuais, música, dança, teatro
- Materiais sensoriais adequados
- Arte como comunicação
""",
            Subject.EDUCACAO_FISICA: """
- Educação Física inclusiva
- Psicomotricidade e coordenação
- Jogos cooperativos
- Regulação sensorial através do movimento
""",
        }

        expertise = subject_expertise.get(subject, "")

        grade_context = f"""
Você está criando atividades para o {self._format_grade_level(grade_level)},
considerando as competências e habilidades da BNCC específicas para este nível.
"""

        return base_prompt + expertise + grade_context + """

**PRINCÍPIOS FUNDAMENTAIS:**
1. **Clareza**: Linguagem simples, objetiva e direta
2. **Estrutura**: Rotina previsível com início, meio e fim
3. **Visual**: Apoios visuais sempre que possível
4. **Sensorial**: Respeitar sensibilidades sensoriais
5. **Interesse**: Incorporar temas de interesse do aluno
6. **Autonomia**: Oferecer escolhas apropriadas
7. **Sucesso**: Critérios claros e alcançáveis
8. **Respeito**: Valorizar neurodiversidade

**FORMATO DE RESPOSTA:**
Sempre responda em formato JSON válido com todas as chaves solicitadas.
Seja específico, prático e baseado em evidências científicas.
"""

    def _get_subject_context(self, subject: Subject, grade_level: GradeLevel) -> str:
        """Get context about the subject and what should be covered."""

        # Subject descriptions by grade level would go here
        # This is a simplified version
        contexts = {
            Subject.MATEMATICA: """
**Foco em Matemática para este nível:**
- Números e operações
- Geometria e medidas
- Grandezas e medidas
- Probabilidade e estatística
- Álgebra (se aplicável ao nível)

**Competências esperadas:**
- Raciocínio lógico
- Resolução de problemas
- Representação matemática
- Uso de tecnologias
""",
            Subject.PORTUGUES: """
**Foco em Português para este nível:**
- Leitura e compreensão
- Produção textual
- Análise linguística
- Oralidade
- Práticas de linguagem

**Competências esperadas:**
- Comunicação oral e escrita
- Interpretação de textos
- Uso adequado da língua
- Produção de gêneros textuais
""",
            # ... adicionar outros
        }

        return contexts.get(subject, "")

    def _get_bncc_context(self, bncc_code: str, subject: Subject, grade_level: GradeLevel) -> str:
        """Get context about specific BNCC competency/skill."""

        # In a production environment, this would query a BNCC database
        # For now, we'll include the code in the prompt for AI to interpret

        return f"""
🎯 **Alinhamento BNCC:**
- Código solicitado: **{bncc_code}**
- Por favor, alinhe a atividade com esta competência/habilidade específica da BNCC
- Inclua o código BNCC no campo "bncc_competencies" da resposta
- Liste os objetos de conhecimento relacionados em "knowledge_objects"
"""

    # ============================================================================
    # Helper Methods
    # ============================================================================

    def _format_grade_level(self, grade_level: GradeLevel) -> str:
        """Format grade level for display."""
        names = {
            GradeLevel.FUNDAMENTAL_1_ANO: "1º ano do Ensino Fundamental",
            GradeLevel.FUNDAMENTAL_2_ANO: "2º ano do Ensino Fundamental",
            GradeLevel.FUNDAMENTAL_3_ANO: "3º ano do Ensino Fundamental",
            # ... adicionar outros
        }
        return names.get(grade_level, grade_level.value)

    def _format_subject(self, subject: Subject) -> str:
        """Format subject for display."""
        names = {
            Subject.MATEMATICA: "Matemática",
            Subject.PORTUGUES: "Língua Portuguesa",
            Subject.CIENCIAS: "Ciências da Natureza",
            Subject.HISTORIA: "História",
            Subject.GEOGRAFIA: "Geografia",
            Subject.ARTE: "Arte",
            Subject.EDUCACAO_FISICA: "Educação Física",
            # ... adicionar outros
        }
        return names.get(subject, subject.value)

    def _format_cognitive_profile(self, profile: Optional[Dict]) -> str:
        """Format cognitive profile for prompt."""
        if not profile:
            return "- Perfil não fornecido"

        return f"""
- Memória: {profile.get('memory', 'N/A')}/10
- Atenção: {profile.get('attention', 'N/A')}/10
- Velocidade de Processamento: {profile.get('processing_speed', 'N/A')}/10
- Função Executiva: {profile.get('executive_function', 'N/A')}/10
- Linguagem: {profile.get('language', 'N/A')}/10
- Visual-Espacial: {profile.get('visual_spatial', 'N/A')}/10
"""

    def _format_sensory_profile(self, profile: Optional[Dict]) -> str:
        """Format sensory profile for prompt."""
        if not profile:
            return "- Perfil não fornecido"

        sensitivity_labels = {
            0: "Nenhuma sensibilidade",
            1: "Baixa sensibilidade",
            2: "Sensibilidade moderada",
            3: "Alta sensibilidade"
        }

        return f"""
- Visual: {sensitivity_labels.get(profile.get('visual', 0))}
- Auditivo: {sensitivity_labels.get(profile.get('auditory', 0))}
- Tátil: {sensitivity_labels.get(profile.get('tactile', 0))}
- Vestibular: {sensitivity_labels.get(profile.get('vestibular', 0))}
- Proprioceptivo: {sensitivity_labels.get(profile.get('proprioceptive', 0))}
"""

    def _format_interests(self, interests: Optional[List[str]]) -> str:
        """Format interests for prompt."""
        if not interests:
            return "- Nenhum interesse especial informado"

        return "\n".join(f"- {interest.title()}" for interest in interests)

    def _parse_activity_response(self, content: str) -> Dict[str, any]:
        """Parse GPT response to extract activity fields."""
        import json

        try:
            # Try to parse as JSON
            parsed = json.loads(content)

            # Validate required fields
            required_fields = ["title", "description", "objectives", "materials", "instructions"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")

            return parsed

        except json.JSONDecodeError:
            # If not JSON, try to extract manually (fallback)
            logger.warning("Response not in JSON format, attempting manual extraction")

            lines = content.strip().split('\n')
            return {
                'title': lines[0] if lines else "Atividade Personalizada",
                'description': '\n'.join(lines[1:]) if len(lines) > 1 else content,
                'objectives': [],
                'materials': [],
                'instructions': [],
                'adaptations': [],
                'visual_supports': [],
                'success_criteria': [],
            }

    # ============================================================================
    # Backwards Compatibility: Keep existing method
    # ============================================================================

    async def generate_activity_content(
        self,
        subject: str,
        topic: str,
        difficulty: int,
        student_age: int,
        cognitive_profile: Optional[Dict] = None,
        sensory_profile: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate activity content (v2.0 compatibility method).

        This method is kept for backwards compatibility with existing code.
        New code should use generate_multidisciplinary_activity().
        """
        # Map to new method (simplified)
        try:
            result = await self.generate_multidisciplinary_activity(
                student_age=student_age,
                subject=Subject.MATEMATICA,  # Default, needs proper mapping
                grade_level=GradeLevel.FUNDAMENTAL_3_ANO,  # Default, needs proper mapping
                activity_type=ActivityType.COGNITIVE,
                difficulty="medium",
                duration_minutes=30,
                theme=topic,
                cognitive_profile=cognitive_profile,
                sensory_profile=sensory_profile,
            )

            return {
                'title': result.get('title', ''),
                'content': result.get('description', ''),
            }

        except Exception as e:
            logger.error(f"Error in backwards compatibility method: {str(e)}")
            raise
```

**Checklist Sprint 5.1:**
- [ ] Atualizar `nlp_service.py` com código acima
- [ ] Testar geração de atividade de Matemática
- [ ] Testar geração de atividade de Português
- [ ] Testar com e sem código BNCC
- [ ] Verificar formato JSON da resposta
- [ ] Executar linter e formatter
- [ ] Commitar: `git commit -m "feat: atualizar NLP service com prompts multidisciplinares"`

---

## 🌐 SPRINT 6: API Endpoints - Filtros e Rotas (2 dias)

### Objetivo
Atualizar endpoints REST para suportar filtros multidisciplinares e adicionar novas rotas.

### 6.1. Atualizar Activity Service

**Arquivo**: `backend/app/services/activity_service.py`

```python
"""
Activity Service - EduAutismo IA v3.0

CHANGELOG v3.0:
- Método generate_multidisciplinary_activity()
- Filtros por subject e grade_level
- Busca por BNCC
"""

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.activity import Activity
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityGenerateMultidisciplinary,  # NOVO v3.0
    ActivityFilterParams,
)
from app.services.nlp_service import NLPService
from app.services.student_service import StudentService
from app.utils.constants import Subject, GradeLevel  # NOVO v3.0
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ActivityService:
    """Service for activity operations with multidisciplinary support."""

    def __init__(self, db: Session):
        self.db = db
        self.nlp_service = NLPService()
        self.student_service = StudentService(db)

    # ============================================================================
    # NOVO v3.0: Multidisciplinary Activity Generation
    # ============================================================================

    async def generate_multidisciplinary_activity(
        self,
        request: ActivityGenerateMultidisciplinary,
        created_by_id: UUID,
    ) -> Activity:
        """
        Generate personalized multidisciplinary activity using AI.

        Args:
            request: Activity generation request with subject, grade_level, etc.
            created_by_id: ID of the user creating the activity

        Returns:
            Created Activity object

        Raises:
            StudentNotFoundError: If student doesn't exist
            NLPServiceError: If AI generation fails
        """
        # 1. Get student profile
        logger.info(f"Generating multidisciplinary activity for student {request.student_id}")
        student = self.student_service.get_by_id(request.student_id)

        # 2. Generate content with NLP service
        logger.info(
            f"Calling NLP service for {request.subject.value} activity",
            extra={
                "subject": request.subject.value,
                "grade_level": request.grade_level.value,
                "bncc_code": request.bncc_code,
            },
        )

        generated_content = await self.nlp_service.generate_multidisciplinary_activity(
            student_age=student.age,
            subject=request.subject,
            grade_level=request.grade_level,
            activity_type=request.activity_type,
            difficulty=request.difficulty.value,
            duration_minutes=request.duration_minutes,
            theme=request.theme,
            bncc_code=request.bncc_code,
            cognitive_profile=student.cognitive_profile,
            sensory_profile=student.sensory_profile,
            interests=student.interests,
        )

        # 3. Create activity in database
        activity = Activity(
            student_id=request.student_id,
            created_by_id=created_by_id,
            title=generated_content['title'],
            description=generated_content['description'],
            activity_type=request.activity_type,
            difficulty=request.difficulty,
            duration_minutes=request.duration_minutes,
            theme=request.theme,
            # NOVO v3.0: Multidisciplinary fields
            subject=request.subject,
            grade_level=request.grade_level,
            bncc_competencies=generated_content.get('bncc_competencies'),
            bncc_skills=generated_content.get('bncc_skills'),
            knowledge_objects=generated_content.get('knowledge_objects'),
            # Content
            objectives=generated_content['objectives'],
            materials=generated_content['materials'],
            instructions=generated_content['instructions'],
            adaptations=generated_content.get('adaptations'),
            visual_supports=generated_content.get('visual_supports'),
            success_criteria=generated_content.get('success_criteria'),
            generated_by_ai=True,
            generation_metadata=generated_content.get('generation_metadata'),
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        logger.info(
            f"Multidisciplinary activity generated successfully: {activity.id}",
            extra={
                "activity_id": str(activity.id),
                "subject": activity.subject.value if activity.subject else None,
                "has_bncc": activity.is_aligned_with_bncc(),
            },
        )

        return activity

    # ============================================================================
    # NOVO v3.0: Advanced Filtering
    # ============================================================================

    def list_with_filters(
        self,
        filters: ActivityFilterParams,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Activity], int]:
        """
        List activities with advanced filters (v3.0).

        Args:
            filters: Filter parameters including subject, grade_level, has_bncc
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (activities list, total count)
        """
        query = self.db.query(Activity)

        # Apply filters
        filter_conditions = []

        if filters.activity_type:
            filter_conditions.append(Activity.activity_type == filters.activity_type)

        if filters.difficulty:
            filter_conditions.append(Activity.difficulty == filters.difficulty)

        if filters.theme:
            filter_conditions.append(Activity.theme.ilike(f"%{filters.theme}%"))

        if filters.generated_by_ai is not None:
            filter_conditions.append(Activity.generated_by_ai == filters.generated_by_ai)

        if filters.student_id:
            filter_conditions.append(Activity.student_id == filters.student_id)

        # NOVO v3.0: Multidisciplinary filters
        if filters.subject:
            filter_conditions.append(Activity.subject == filters.subject)

        if filters.grade_level:
            filter_conditions.append(Activity.grade_level == filters.grade_level)

        if filters.has_bncc is not None:
            if filters.has_bncc:
                # Has BNCC alignment
                filter_conditions.append(
                    or_(
                        Activity.bncc_competencies.isnot(None),
                        Activity.bncc_skills.isnot(None),
                        Activity.knowledge_objects.isnot(None),
                    )
                )
            else:
                # No BNCC alignment
                filter_conditions.append(
                    and_(
                        Activity.bncc_competencies.is_(None),
                        Activity.bncc_skills.is_(None),
                        Activity.knowledge_objects.is_(None),
                    )
                )

        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        # Get total count
        total = query.count()

        # Apply pagination
        activities = query.offset(skip).limit(limit).all()

        logger.info(
            f"Listed {len(activities)} activities with filters",
            extra={
                "total": total,
                "filters_applied": len(filter_conditions),
                "subject": filters.subject.value if filters.subject else None,
                "grade_level": filters.grade_level.value if filters.grade_level else None,
            },
        )

        return activities, total

    def search_by_bncc_code(
        self,
        bncc_code: str,
        grade_level: Optional[GradeLevel] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Activity], int]:
        """
        Search activities by BNCC code (v3.0).

        Args:
            bncc_code: BNCC competency/skill code (e.g., "EF01MA01")
            grade_level: Optional filter by grade level
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (activities list, total count)
        """
        query = self.db.query(Activity).filter(
            or_(
                Activity.bncc_competencies.contains([bncc_code]),
                Activity.bncc_skills.contains([bncc_code]),
            )
        )

        if grade_level:
            query = query.filter(Activity.grade_level == grade_level)

        total = query.count()
        activities = query.offset(skip).limit(limit).all()

        logger.info(
            f"Found {len(activities)} activities for BNCC code {bncc_code}",
            extra={
                "bncc_code": bncc_code,
                "grade_level": grade_level.value if grade_level else None,
                "total": total,
            },
        )

        return activities, total

    # Existing methods remain unchanged...
    # (create, get_by_id, update, delete, etc.)
```

**Checklist Sprint 6.1:**
- [ ] Atualizar `activity_service.py`
- [ ] Testar método `generate_multidisciplinary_activity()`
- [ ] Testar `list_with_filters()` com novos filtros
- [ ] Testar `search_by_bncc_code()`
- [ ] Commitar: `git commit -m "feat: adicionar métodos multidisciplinares no activity service"`

### 6.2. Atualizar Activity Routes

**Arquivo**: `backend/app/api/routes/activities.py`

```python
"""
Activity Routes - EduAutismo IA v3.0

CHANGELOG v3.0:
- Endpoint POST /generate-multidisciplinary
- Filtros multidisciplinares no GET /
- Endpoint GET /search/bncc/{code}
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityGenerate,
    ActivityGenerateMultidisciplinary,  # NOVO v3.0
    ActivityFilterParams,
)
from app.schemas.common import PaginatedResponse
from app.services.activity_service import ActivityService
from app.utils.constants import Subject, GradeLevel  # NOVO v3.0
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/activities", tags=["activities"])


# ============================================================================
# NOVO v3.0: Multidisciplinary Activity Generation
# ============================================================================

@router.post(
    "/generate-multidisciplinary",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate multidisciplinary activity with AI (v3.0)",
    description="""
    Generate personalized activity for a specific subject and grade level,
    aligned with BNCC competencies.

    **New in v3.0:**
    - Subject selection (Matemática, Português, etc.)
    - Grade level targeting
    - Optional BNCC code alignment
    - Enhanced AI prompts with subject-specific context

    **Example:**
    ```json
    {
      "student_id": "uuid-here",
      "subject": "matematica",
      "grade_level": "fundamental_3_ano",
      "activity_type": "cognitive",
      "difficulty": "medium",
      "duration_minutes": 30,
      "theme": "dinossauros",
      "bncc_code": "EF03MA06"
    }
    ```
    """,
)
async def generate_multidisciplinary_activity(
    request: ActivityGenerateMultidisciplinary,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate multidisciplinary activity with AI (v3.0).

    This endpoint uses GPT-4o with subject-specific prompts to generate
    educational activities aligned with BNCC and adapted for TEA students.
    """
    try:
        service = ActivityService(db)
        activity = await service.generate_multidisciplinary_activity(
            request=request,
            created_by_id=UUID(current_user["sub"]),
        )

        logger.info(
            "Multidisciplinary activity generated via API",
            extra={
                "activity_id": str(activity.id),
                "subject": activity.subject.value if activity.subject else None,
                "user": current_user["sub"],
            },
        )

        return activity

    except Exception as e:
        logger.error(f"Error generating multidisciplinary activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate activity: {str(e)}",
        )


# ============================================================================
# UPDATED: List with Multidisciplinary Filters
# ============================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[ActivityListResponse],
    summary="List activities with filters (updated v3.0)",
    description="""
    List activities with optional filters.

    **New filters in v3.0:**
    - `subject`: Filter by subject (matematica, portugues, etc.)
    - `grade_level`: Filter by grade level (fundamental_3_ano, etc.)
    - `has_bncc`: Filter activities with BNCC alignment (true/false)
    """,
)
async def list_activities(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    # Existing filters
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    generated_by_ai: Optional[bool] = Query(None, description="Filter AI-generated"),
    student_id: Optional[UUID] = Query(None, description="Filter by student"),
    # NOVO v3.0: Multidisciplinary filters
    subject: Optional[Subject] = Query(None, description="Filter by subject"),
    grade_level: Optional[GradeLevel] = Query(None, description="Filter by grade level"),
    has_bncc: Optional[bool] = Query(None, description="Filter BNCC-aligned activities"),
    # Dependencies
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List activities with advanced filters (v3.0).
    """
    try:
        service = ActivityService(db)

        # Build filters
        filters = ActivityFilterParams(
            activity_type=activity_type,
            difficulty=difficulty,
            theme=theme,
            generated_by_ai=generated_by_ai,
            student_id=student_id,
            subject=subject,
            grade_level=grade_level,
            has_bncc=has_bncc,
        )

        # Calculate skip
        skip = (page - 1) * page_size

        # Get activities
        activities, total = service.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
        )

        return PaginatedResponse(
            items=activities,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )

    except Exception as e:
        logger.error(f"Error listing activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list activities: {str(e)}",
        )


# ============================================================================
# NOVO v3.0: Search by BNCC Code
# ============================================================================

@router.get(
    "/search/bncc/{code}",
    response_model=PaginatedResponse[ActivityListResponse],
    summary="Search activities by BNCC code (v3.0)",
    description="""
    Search activities that target a specific BNCC competency or skill code.

    **Example codes:**
    - `EF01MA01`: Fundamental I, Matemática
    - `EF03LP01`: Fundamental I, Português
    - `EI03EO01`: Educação Infantil

    **Use case:**
    - Find activities aligned with specific BNCC objectives
    - Browse repository of activities for a competency
    - Reuse activities across students
    """,
)
async def search_activities_by_bncc(
    code: str,
    grade_level: Optional[GradeLevel] = Query(None, description="Filter by grade level"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Search activities by BNCC code (v3.0).
    """
    try:
        service = ActivityService(db)

        skip = (page - 1) * page_size

        activities, total = service.search_by_bncc_code(
            bncc_code=code,
            grade_level=grade_level,
            skip=skip,
            limit=page_size,
        )

        logger.info(
            f"BNCC search performed for code {code}",
            extra={
                "bncc_code": code,
                "results": len(activities),
                "user": current_user["sub"],
            },
        )

        return PaginatedResponse(
            items=activities,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )

    except Exception as e:
        logger.error(f"Error searching by BNCC code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search activities: {str(e)}",
        )


# ============================================================================
# NOVO v3.0: Get Subjects and Grade Levels
# ============================================================================

@router.get(
    "/meta/subjects",
    response_model=List[dict],
    summary="Get available subjects (v3.0)",
)
async def get_available_subjects():
    """Get list of available subjects with metadata."""
    from app.utils.constants import Subject

    subjects = [
        {
            "code": subject.value,
            "name": subject.name,
            "display_name": subject.value.replace("_", " ").title(),
        }
        for subject in Subject
    ]

    return subjects


@router.get(
    "/meta/grade-levels",
    response_model=List[dict],
    summary="Get available grade levels (v3.0)",
)
async def get_available_grade_levels():
    """Get list of available grade levels with metadata."""
    from app.utils.constants import GradeLevel

    levels = [
        {
            "code": level.value,
            "name": level.name,
            "display_name": level.value.replace("_", " ").title(),
            "age_range": GradeLevel.get_age_range(level),
            "education_level": GradeLevel.get_education_level(level),
        }
        for level in GradeLevel
    ]

    return levels


# Existing endpoints remain unchanged...
# (POST /, GET /{id}, PUT /{id}, DELETE /{id}, etc.)
```

**Checklist Sprint 6.2:**
- [ ] Atualizar `activities.py` routes
- [ ] Testar POST `/generate-multidisciplinary`
- [ ] Testar GET `/` com novos filtros
- [ ] Testar GET `/search/bncc/{code}`
- [ ] Testar GET `/meta/subjects`
- [ ] Testar GET `/meta/grade-levels`
- [ ] Atualizar OpenAPI docs: http://localhost:8000/docs
- [ ] Commitar: `git commit -m "feat: adicionar endpoints multidisciplinares"`

---

## 🧪 SPRINT 7: Testes Completos (3 dias)

### Objetivo
Garantir 85%+ de cobertura de testes para todas as mudanças do MVP 3.0.

### 7.1. Testes Unitários - Constants e Enums

**Arquivo**: `backend/tests/unit/test_constants_v3.py`

```python
"""
Unit tests for constants.py enums (v3.0).
"""

import pytest

from app.utils.constants import Subject, GradeLevel


class TestSubjectEnum:
    """Test Subject enum."""

    def test_subject_enum_values(self):
        """Test that all expected subjects are defined."""
        expected_subjects = [
            "matematica",
            "portugues",
            "ciencias",
            "historia",
            "geografia",
            "arte",
            "educacao_fisica",
            "ingles",
            "biologia",
            "fisica",
            "quimica",
        ]

        for subject_code in expected_subjects:
            assert any(s.value == subject_code for s in Subject)

    def test_get_by_grade_level_infantil(self):
        """Test subjects for Educação Infantil."""
        subjects = Subject.get_by_grade_level("pre_escola_4")

        assert len(subjects) == 5
        assert Subject.INFANTIL_SELF_OTHERS in subjects
        assert Subject.INFANTIL_BODY_MOVEMENT in subjects

    def test_get_by_grade_level_fundamental_1(self):
        """Test subjects for Fundamental I."""
        subjects = Subject.get_by_grade_level("fundamental_1_3ano")

        assert len(subjects) >= 7
        assert Subject.MATEMATICA in subjects
        assert Subject.PORTUGUES in subjects
        assert Subject.INGLES not in subjects  # Inglês só no Fundamental II

    def test_get_by_grade_level_fundamental_2(self):
        """Test subjects for Fundamental II."""
        subjects = Subject.get_by_grade_level("fundamental_2_6ano")

        assert len(subjects) >= 8
        assert Subject.MATEMATICA in subjects
        assert Subject.INGLES in subjects  # Inglês a partir do 6º ano

    def test_get_by_grade_level_medio(self):
        """Test subjects for Ensino Médio."""
        subjects = Subject.get_by_grade_level("medio_1_ano")

        assert len(subjects) >= 12
        assert Subject.BIOLOGIA in subjects
        assert Subject.FISICA in subjects
        assert Subject.QUIMICA in subjects


class TestGradeLevelEnum:
    """Test GradeLevel enum."""

    def test_grade_level_enum_values(self):
        """Test that all expected grade levels are defined."""
        expected_levels = [
            "creche_0_1",
            "pre_escola_4",
            "fundamental_1_ano",
            "fundamental_2_ano",
            "fundamental_9_ano",
            "medio_1_ano",
            "medio_3_ano",
        ]

        for level_code in expected_levels:
            assert any(l.value == level_code for l in GradeLevel)

    def test_get_age_range_infantil(self):
        """Test age range for Educação Infantil."""
        age_range = GradeLevel.get_age_range(GradeLevel.PRE_ESCOLA_4)
        assert age_range == (4, 4)

    def test_get_age_range_fundamental_1(self):
        """Test age range for Fundamental I."""
        age_range = GradeLevel.get_age_range(GradeLevel.FUNDAMENTAL_3_ANO)
        assert age_range == (8, 8)

    def test_get_age_range_medio(self):
        """Test age range for Ensino Médio."""
        age_range = GradeLevel.get_age_range(GradeLevel.MEDIO_1_ANO)
        assert age_range == (15, 15)

    def test_get_education_level_infantil(self):
        """Test education level for Infantil."""
        level = GradeLevel.get_education_level(GradeLevel.CRECHE_0_1)
        assert level == "Educação Infantil"

    def test_get_education_level_fundamental_1(self):
        """Test education level for Fundamental I."""
        level = GradeLevel.get_education_level(GradeLevel.FUNDAMENTAL_3_ANO)
        assert level == "Ensino Fundamental I"

    def test_get_education_level_fundamental_2(self):
        """Test education level for Fundamental II."""
        level = GradeLevel.get_education_level(GradeLevel.FUNDAMENTAL_7_ANO)
        assert level == "Ensino Fundamental II"

    def test_get_education_level_medio(self):
        """Test education level for Médio."""
        level = GradeLevel.get_education_level(GradeLevel.MEDIO_2_ANO)
        assert level == "Ensino Médio"
```

### 7.2. Testes Unitários - Activity Model

**Arquivo**: `backend/tests/unit/test_activity_model_v3.py`

```python
"""
Unit tests for Activity model (v3.0).
"""

import pytest

from app.models.activity import Activity
from app.utils.constants import Subject, GradeLevel, ActivityType, DifficultyLevel


class TestActivityModelV3:
    """Test Activity model multidisciplinary fields."""

    def test_activity_with_subject_and_grade_level(self, db_session):
        """Test creating activity with subject and grade level."""
        activity = Activity(
            title="Adição com Dinossauros",
            description="Atividade de matemática",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            subject=Subject.MATEMATICA,  # NOVO v3.0
            grade_level=GradeLevel.FUNDAMENTAL_3_ANO,  # NOVO v3.0
            objectives=["Aprender adição"],
            materials=["Dinossauros de plástico"],
            instructions=["Passo 1", "Passo 2"],
            student_id="uuid-here",
        )

        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)

        assert activity.subject == Subject.MATEMATICA
        assert activity.grade_level == GradeLevel.FUNDAMENTAL_3_ANO

    def test_activity_with_bncc_competencies(self, db_session):
        """Test creating activity with BNCC alignment."""
        activity = Activity(
            title="Leitura e Interpretação",
            description="Atividade de português",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.MEDIUM,
            duration_minutes=45,
            subject=Subject.PORTUGUES,
            grade_level=GradeLevel.FUNDAMENTAL_4_ANO,
            bncc_competencies=["EF04LP01", "EF04LP02"],  # NOVO v3.0
            bncc_skills=["EF04LP03"],  # NOVO v3.0
            knowledge_objects=["Leitura", "Interpretação"],  # NOVO v3.0
            objectives=["Compreender texto"],
            materials=["Livro"],
            instructions=["Ler", "Responder"],
            student_id="uuid-here",
        )

        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)

        assert activity.bncc_competencies == ["EF04LP01", "EF04LP02"]
        assert activity.bncc_skills == ["EF04LP03"]
        assert activity.knowledge_objects == ["Leitura", "Interpretação"]

    def test_activity_subject_name_property(self, db_session):
        """Test subject_name property."""
        activity = Activity(
            title="Test",
            description="Test",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            subject=Subject.MATEMATICA,
            objectives=["Test"],
            materials=["Test"],
            instructions=["Test"],
            student_id="uuid-here",
        )

        assert activity.subject_name == "Matemática"

    def test_activity_grade_level_name_property(self, db_session):
        """Test grade_level_name property."""
        activity = Activity(
            title="Test",
            description="Test",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            grade_level=GradeLevel.FUNDAMENTAL_3_ANO,
            objectives=["Test"],
            materials=["Test"],
            instructions=["Test"],
            student_id="uuid-here",
        )

        assert activity.grade_level_name == "3º ano Fundamental"

    def test_is_aligned_with_bncc_true(self, db_session):
        """Test is_aligned_with_bncc returns True."""
        activity = Activity(
            title="Test",
            description="Test",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            bncc_competencies=["EF01MA01"],
            objectives=["Test"],
            materials=["Test"],
            instructions=["Test"],
            student_id="uuid-here",
        )

        assert activity.is_aligned_with_bncc() is True

    def test_is_aligned_with_bncc_false(self, db_session):
        """Test is_aligned_with_bncc returns False."""
        activity = Activity(
            title="Test",
            description="Test",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            objectives=["Test"],
            materials=["Test"],
            instructions=["Test"],
            student_id="uuid-here",
        )

        assert activity.is_aligned_with_bncc() is False

    def test_to_dict_includes_multidisciplinary_fields(self, db_session):
        """Test to_dict includes multidisciplinary fields."""
        activity = Activity(
            title="Test",
            description="Test",
            activity_type=ActivityType.COGNITIVE,
            difficulty=DifficultyLevel.EASY,
            duration_minutes=30,
            subject=Subject.CIENCIAS,
            grade_level=GradeLevel.FUNDAMENTAL_5_ANO,
            bncc_competencies=["EF05CI01"],
            objectives=["Test"],
            materials=["Test"],
            instructions=["Test"],
            theme="Planetas",
            student_id="uuid-here",
        )

        activity_dict = activity.to_dict()

        assert activity_dict["subject"] == "ciencias"
        assert activity_dict["grade_level"] == "fundamental_5_ano"
        assert activity_dict["bncc_competencies"] == ["EF05CI01"]
```

### 7.3. Testes de Integração - API Endpoints

**Arquivo**: `backend/tests/integration/test_activities_api_v3.py`

```python
"""
Integration tests for activities API endpoints (v3.0).
"""

import pytest

from app.utils.constants import Subject, GradeLevel


class TestActivitiesAPIMultidisciplinary:
    """Test multidisciplinary activity endpoints."""

    def test_generate_multidisciplinary_activity_matematica(
        self, client, auth_headers, sample_student
    ):
        """Test generating Matemática activity."""
        response = client.post(
            "/api/v1/activities/generate-multidisciplinary",
            json={
                "student_id": str(sample_student.id),
                "subject": "matematica",
                "grade_level": "fundamental_3_ano",
                "activity_type": "cognitive",
                "difficulty": "easy",
                "duration_minutes": 30,
                "theme": "dinossauros",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["subject"] == "matematica"
        assert data["grade_level"] == "fundamental_3_ano"
        assert data["subject_name"] is not None
        assert data["generated_by_ai"] is True

    def test_generate_multidisciplinary_activity_with_bncc(
        self, client, auth_headers, sample_student
    ):
        """Test generating activity with BNCC code."""
        response = client.post(
            "/api/v1/activities/generate-multidisciplinary",
            json={
                "student_id": str(sample_student.id),
                "subject": "portugues",
                "grade_level": "fundamental_4_ano",
                "activity_type": "cognitive",
                "difficulty": "medium",
                "duration_minutes": 45,
                "bncc_code": "EF04LP01",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["subject"] == "portugues"
        assert data["is_bncc_aligned"] is True
        assert "EF04LP01" in data.get("bncc_competencies", [])

    def test_list_activities_filter_by_subject(
        self, client, auth_headers, sample_activities_v3
    ):
        """Test filtering activities by subject."""
        response = client.get(
            "/api/v1/activities/?subject=matematica",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] > 0
        for activity in data["items"]:
            assert activity["subject"] == "matematica"

    def test_list_activities_filter_by_grade_level(
        self, client, auth_headers, sample_activities_v3
    ):
        """Test filtering activities by grade level."""
        response = client.get(
            "/api/v1/activities/?grade_level=fundamental_3_ano",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] > 0
        for activity in data["items"]:
            assert activity["grade_level"] == "fundamental_3_ano"

    def test_list_activities_filter_by_has_bncc(
        self, client, auth_headers, sample_activities_v3
    ):
        """Test filtering activities with BNCC alignment."""
        response = client.get(
            "/api/v1/activities/?has_bncc=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] > 0
        for activity in data["items"]:
            assert activity["is_bncc_aligned"] is True

    def test_search_activities_by_bncc_code(
        self, client, auth_headers, sample_activities_v3
    ):
        """Test searching activities by BNCC code."""
        response = client.get(
            "/api/v1/activities/search/bncc/EF03MA06",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 0
        for activity in data["items"]:
            assert (
                "EF03MA06" in activity.get("bncc_competencies", [])
                or "EF03MA06" in activity.get("bncc_skills", [])
            )

    def test_get_available_subjects(self, client):
        """Test getting list of available subjects."""
        response = client.get("/api/v1/activities/meta/subjects")

        assert response.status_code == 200
        subjects = response.json()

        assert len(subjects) > 0
        assert any(s["code"] == "matematica" for s in subjects)
        assert any(s["code"] == "portugues" for s in subjects)

    def test_get_available_grade_levels(self, client):
        """Test getting list of available grade levels."""
        response = client.get("/api/v1/activities/meta/grade-levels")

        assert response.status_code == 200
        levels = response.json()

        assert len(levels) > 0
        assert any(l["code"] == "fundamental_3_ano" for l in levels)
        assert all("age_range" in l for l in levels)
        assert all("education_level" in l for l in levels)
```

**Checklist Sprint 7:**
- [ ] Executar todos os testes: `pytest tests/ -v`
- [ ] Verificar coverage: `pytest --cov=app --cov-report=html`
- [ ] Coverage >= 85%?
- [ ] Todos os testes passando?
- [ ] Commitar: `git commit -m "test: adicionar testes para MVP 3.0 multidisciplinar"`

---

## 📚 SPRINT 8: Documentação Completa (2 dias)

### Objetivo
Atualizar toda a documentação para refletir as mudanças do MVP 3.0.

### 8.1. Atualizar CLAUDE.md

**Seções a atualizar:**
- Adicionar Subject e GradeLevel enums
- Exemplos de uso multidisciplinar
- Comandos de teste atualizados

### 8.2. Criar Guia de Uso Multidisciplinar

**Arquivo**: `backend/docs/MULTIDISCIPLINARY_USAGE_GUIDE.md`

```markdown
# 📚 Guia de Uso: Plataforma Multidisciplinar

## Visão Geral

O EduAutismo IA v3.0 permite criar atividades para TODAS as disciplinas curriculares,
alinhadas à BNCC e personalizadas para alunos com TEA.

## Disciplinas Disponíveis

### Educação Infantil (Campos de Experiência BNCC)
- O eu, o outro e o nós
- Corpo, gestos e movimentos
- Traços, sons, cores e formas
- Escuta, fala, pensamento e imaginação
- Espaços, tempos, quantidades

### Ensino Fundamental I e II
- Matemática
- Língua Portuguesa
- Ciências
- História
- Geografia
- Arte
- Educação Física
- Língua Inglesa (a partir do 6º ano)

### Ensino Médio
- Matemática
- Língua Portuguesa
- Biologia
- Física
- Química
- História
- Geografia
- Filosofia
- Sociologia
- Arte
- Educação Física
- Inglês
- Literatura
- Redação

## Exemplos de Uso

### 1. Atividade de Matemática (3º ano)

```python
POST /api/v1/activities/generate-multidisciplinary

{
  "student_id": "uuid-here",
  "subject": "matematica",
  "grade_level": "fundamental_3_ano",
  "activity_type": "cognitive",
  "difficulty": "easy",
  "duration_minutes": 30,
  "theme": "dinossauros",
  "bncc_code": "EF03MA06"  // Resolver e elaborar problemas de adição e subtração
}
```

**Resposta esperada:**
- Atividade com problemas de adição usando dinossauros
- Alinhada com EF03MA06 da BNCC
- Adaptada para perfil TEA do aluno
- Com apoios visuais e instruções claras

### 2. Atividade de Português (4º ano)

```python
POST /api/v1/activities/generate-multidisciplinary

{
  "student_id": "uuid-here",
  "subject": "portugues",
  "grade_level": "fundamental_4_ano",
  "activity_type": "cognitive",
  "difficulty": "medium",
  "duration_minutes": 45,
  "theme": "astronomia",
  "bncc_code": "EF04LP03"  // Localizar palavras no dicionário
}
```

### 3. Filtrar Atividades por Disciplina

```python
GET /api/v1/activities/?subject=ciencias&grade_level=fundamental_5_ano

# Retorna todas as atividades de Ciências do 5º ano
```

### 4. Buscar por Código BNCC

```python
GET /api/v1/activities/search/bncc/EF03MA06

# Retorna todas as atividades alinhadas com EF03MA06
```

## Alinhamento BNCC

### O que é a BNCC?

A Base Nacional Comum Curricular (BNCC) define as aprendizagens essenciais
que todos os alunos brasileiros devem desenvolver.

### Como funciona o alinhamento?

1. **Códigos BNCC**: Cada competência/habilidade tem um código único
   - Formato: `[EI/EF/EM][ano][disciplina][número]`
   - Exemplo: `EF03MA06` = Ensino Fundamental, 3º ano, Matemática, habilidade 06

2. **No EduAutismo IA**:
   - Você pode informar um código BNCC ao gerar atividade
   - A IA alinhará a atividade com essa competência
   - A atividade será marcada com os códigos BNCC correspondentes

3. **Busca por BNCC**:
   - Encontre atividades alinhadas com competências específicas
   - Reutilize atividades para outros alunos
   - Mantenha biblioteca organizada por objetivos de aprendizagem

## Boas Práticas

### ✅ DO

- Especifique subject e grade_level sempre que possível
- Use códigos BNCC para garantir alinhamento curricular
- Incorpore interesses especiais do aluno no theme
- Revise e personalize atividades geradas pela IA
- Reutilize atividades bem-sucedidas

### ❌ DON'T

- Não gere atividades sem contexto do perfil do aluno
- Não ignore adaptações sugeridas
- Não espere que a IA seja perfeita (sempre revise!)
- Não use atividades de série muito acima/abaixo do nível do aluno

## Dúvidas Frequentes

**Q: Posso usar atividades sem especificar disciplina?**
A: Sim, os campos subject e grade_level são opcionais. Mas especificá-los
melhora significativamente a qualidade da atividade gerada.

**Q: O código BNCC é obrigatório?**
A: Não, é opcional. Se não informado, a IA sugerirá competências adequadas.

**Q: Posso criar atividades interdisciplinares?**
A: Atualmente, cada atividade tem uma disciplina principal. Mas você pode
mencionar conexões interdisciplinares no campo "theme".

**Q: Como sei qual código BNCC usar?**
A: Consulte a documentação oficial da BNCC ou use nosso endpoint
`/api/v1/bncc/search` (disponível em MVP 4.0).

## Próximos Passos

- MVP 4.0: Busca de códigos BNCC integrada
- MVP 4.0: Sugestão automática de competências
- MVP 5.0: Atividades interdisciplinares
- MVP 5.0: Sequências didáticas completas
```

### 8.3. Atualizar API Docs (Swagger)

Os docstrings dos endpoints já estão atualizados, então o Swagger será
automaticamente atualizado.

**Validação:**
- Acessar http://localhost:8000/docs
- Verificar novos endpoints
- Testar via Swagger UI

**Checklist Sprint 8:**
- [ ] Atualizar CLAUDE.md com novos enums
- [ ] Criar MULTIDISCIPLINARY_USAGE_GUIDE.md
- [ ] Validar Swagger docs
- [ ] Adicionar exemplos no README
- [ ] Commitar: `git commit -m "docs: adicionar documentação completa MVP 3.0"`

---

## ✅ CHECKLIST FINAL MVP 3.0

### Código

- [ ] Sprint 1: Enums e Constants
- [ ] Sprint 2: Models (SQLAlchemy)
- [ ] Sprint 3: Database Migration
- [ ] Sprint 4: Schemas (Pydantic)
- [ ] Sprint 5: NLP Service
- [ ] Sprint 6: API Endpoints
- [ ] Sprint 7: Testes (85%+ coverage)
- [ ] Sprint 8: Documentação

### Qualidade

- [ ] Todos os testes passando
- [ ] Coverage >= 85%
- [ ] Black formatado
- [ ] Flake8 sem erros
- [ ] MyPy validado
- [ ] Sem regressões

### Deployment

- [ ] Migration executada em dev
- [ ] Validação manual via Swagger
- [ ] Teste de carga básico
- [ ] Logs estruturados funcionando
- [ ] Pronto para merge

---

## 🎉 CONCLUSÃO

Com a conclusão do MVP 3.0, o EduAutismo IA será transformado em uma
**Plataforma Multidisciplinar Inteligente** completa:

✅ **25 disciplinas** disponíveis
✅ **18 níveis escolares** suportados
✅ **Alinhamento BNCC** automático
✅ **IA contextualizada** por disciplina
✅ **Filtros avançados** para busca
✅ **100% backwards-compatible**

**Tempo total estimado**: ~33 horas (~1 semana de desenvolvimento)

**Próximo passo**: MVP 4.0 - Analytics & Insights com BNCC avançado

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

