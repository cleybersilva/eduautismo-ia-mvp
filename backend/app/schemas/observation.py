"""
Professional Observation Pydantic schemas - DTOs para observações profissionais.

Schemas de validação e serialização para observações multiprofissionais.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.observation import ObservationContext, ObservationType


# ============================================================================
# CREATE SCHEMAS
# ============================================================================


class ProfessionalObservationCreate(BaseModel):
    """Schema para criação de observação profissional."""

    student_id: UUID = Field(..., description="ID do estudante observado")
    observation_type: ObservationType = Field(..., description="Tipo de observação")
    context: ObservationContext = Field(..., description="Contexto da observação")
    content: str = Field(..., min_length=10, description="Conteúdo da observação")
    behavioral_indicators: Optional[dict[str, Any]] = Field(
        None, description="Indicadores comportamentais estruturados"
    )
    socioemotional_indicators: Optional[dict[str, Any]] = Field(
        None, description="Indicadores socioemocionais estruturados"
    )
    severity_level: int = Field(
        default=1, ge=1, le=5, description="Nível de severidade/urgência (1-5)"
    )
    requires_intervention: bool = Field(
        default=False, description="Requer intervenção imediata"
    )
    is_private: bool = Field(
        default=False,
        description="Visível apenas para profissionais de saúde autorizados",
    )
    tags: Optional[list[str]] = Field(None, description="Tags para categorização")
    attachments: Optional[list[dict[str, str]]] = Field(
        None, description="Anexos (URLs de fotos, vídeos, documentos)"
    )
    observed_at: datetime = Field(..., description="Data/hora da observação")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "observation_type": "behavioral",
                "context": "classroom",
                "content": "Estudante demonstrou dificuldade em manter atenção durante atividade de leitura. Após 10 minutos, começou a balançar as mãos e olhar para a janela.",
                "behavioral_indicators": {
                    "attention_span": "10 minutos",
                    "self_stimulation": "balançar mãos",
                    "distraction_triggers": "barulho externo",
                },
                "socioemotional_indicators": {
                    "frustration_level": "baixo",
                    "social_engagement": "não iniciou interação",
                },
                "severity_level": 2,
                "requires_intervention": False,
                "is_private": False,
                "tags": ["atenção", "sensorial", "sala_de_aula"],
                "observed_at": "2025-01-17T10:30:00Z",
            }
        }


class ProfessionalObservationUpdate(BaseModel):
    """Schema para atualização de observação profissional."""

    observation_type: Optional[ObservationType] = None
    context: Optional[ObservationContext] = None
    content: Optional[str] = Field(None, min_length=10)
    behavioral_indicators: Optional[dict[str, Any]] = None
    socioemotional_indicators: Optional[dict[str, Any]] = None
    severity_level: Optional[int] = Field(None, ge=1, le=5)
    requires_intervention: Optional[bool] = None
    is_private: Optional[bool] = None
    tags: Optional[list[str]] = None
    attachments: Optional[list[dict[str, str]]] = None
    observed_at: Optional[datetime] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class ProfessionalObservationResponse(BaseModel):
    """Schema de resposta para observação profissional."""

    id: UUID
    student_id: UUID
    professional_id: UUID
    observation_type: ObservationType
    context: ObservationContext
    content: str
    behavioral_indicators: Optional[dict[str, Any]]
    socioemotional_indicators: Optional[dict[str, Any]]
    severity_level: int
    requires_intervention: bool
    is_private: bool
    tags: Optional[list[str]]
    attachments: Optional[list[dict[str, str]]]
    observed_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    requires_immediate_attention: bool
    is_accessible_by_education_only: bool

    class Config:
        from_attributes = True


class ProfessionalObservationWithDetails(ProfessionalObservationResponse):
    """Schema de resposta com detalhes de relacionamentos."""

    student_name: Optional[str] = None
    professional_name: Optional[str] = None
    professional_role: Optional[str] = None


class ProfessionalObservationListResponse(BaseModel):
    """Schema para lista paginada de observações."""

    observations: list[ProfessionalObservationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# FILTER/QUERY SCHEMAS
# ============================================================================


class ObservationFilter(BaseModel):
    """Schema para filtros de busca de observações."""

    student_id: Optional[UUID] = None
    professional_id: Optional[UUID] = None
    observation_type: Optional[ObservationType] = None
    context: Optional[ObservationContext] = None
    severity_level_min: Optional[int] = Field(None, ge=1, le=5)
    severity_level_max: Optional[int] = Field(None, ge=1, le=5)
    requires_intervention: Optional[bool] = None
    is_private: Optional[bool] = None
    tags: Optional[list[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = Field(None, description="Busca em conteúdo")


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class ObservationSummary(BaseModel):
    """Resumo de observações para um estudante."""

    student_id: UUID
    total_observations: int
    by_type: dict[str, int]
    by_severity: dict[int, int]
    requires_intervention_count: int
    most_common_contexts: list[dict[str, Any]]
    most_common_tags: list[dict[str, Any]]
    recent_observations: list[ProfessionalObservationResponse]


class ObservationTimeline(BaseModel):
    """Timeline de observações para visualização."""

    student_id: UUID
    period_start: datetime
    period_end: datetime
    observations: list[ProfessionalObservationResponse]
    severity_trend: list[dict[str, Any]]
    intervention_needed_dates: list[datetime]
