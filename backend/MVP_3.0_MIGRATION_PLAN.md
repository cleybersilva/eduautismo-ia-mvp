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

## 🚀 CONTINUAÇÃO NO PRÓXIMO COMMIT

Este plano será expandido nos próximos passos com:
- Sprint 5: Atualizar NLP Service (prompts IA)
- Sprint 6: Atualizar API Endpoints
- Sprint 7: Testes completos
- Sprint 8: Documentação

**Status atual**: ✅ Estrutura base do plano de migração criada

---

**Próximo passo**: Quer que eu continue com os sprints restantes (5-8)?

