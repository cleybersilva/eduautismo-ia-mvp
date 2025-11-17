"""
Social Emotional Indicator Pydantic schemas - DTOs para indicadores socioemocionais.

Schemas de validação e serialização para indicadores socioemocionais.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.socioemotional_indicator import IndicatorType, MeasurementContext


# ============================================================================
# CREATE SCHEMAS
# ============================================================================


class SocialEmotionalIndicatorCreate(BaseModel):
    """Schema para criação de indicador socioemocional."""

    student_id: UUID = Field(..., description="ID do estudante")
    indicator_type: IndicatorType = Field(..., description="Tipo de indicador")
    context: MeasurementContext = Field(..., description="Contexto da medição")
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Pontuação: 1 (muito baixo) a 10 (muito alto)",
    )
    observations: Optional[str] = Field(None, description="Observações qualitativas")
    specific_behaviors: Optional[str] = Field(
        None, description="Comportamentos específicos observados"
    )
    environmental_factors: Optional[str] = Field(
        None, description="Fatores ambientais que influenciaram"
    )
    triggers: Optional[str] = Field(None, description="Gatilhos identificados")
    supports_used: Optional[str] = Field(None, description="Suportes/estratégias utilizados")
    measured_at: datetime = Field(..., description="Data/hora da medição")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "indicator_type": "emotional_regulation",
                "context": "classroom",
                "score": 6,
                "observations": "Estudante conseguiu se acalmar após frustração com atividade de matemática. Usou estratégia de respiração ensinada pela psicóloga.",
                "specific_behaviors": "Respiração profunda, pediu para beber água, voltou para atividade após 3 minutos",
                "environmental_factors": "Sala silenciosa, apenas 8 alunos presentes",
                "triggers": "Dificuldade em resolver problema matemático",
                "supports_used": "Técnica de respiração, pausa estruturada, encorajamento verbal",
                "measured_at": "2025-01-17T14:30:00Z",
            }
        }


class SocialEmotionalIndicatorUpdate(BaseModel):
    """Schema para atualização de indicador socioemocional."""

    indicator_type: Optional[IndicatorType] = None
    context: Optional[MeasurementContext] = None
    score: Optional[int] = Field(None, ge=1, le=10)
    observations: Optional[str] = None
    specific_behaviors: Optional[str] = None
    environmental_factors: Optional[str] = None
    triggers: Optional[str] = None
    supports_used: Optional[str] = None
    measured_at: Optional[datetime] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class SocialEmotionalIndicatorResponse(BaseModel):
    """Schema de resposta para indicador socioemocional."""

    id: UUID
    student_id: UUID
    professional_id: UUID
    indicator_type: IndicatorType
    context: MeasurementContext
    score: int
    observations: Optional[str]
    specific_behaviors: Optional[str]
    environmental_factors: Optional[str]
    triggers: Optional[str]
    supports_used: Optional[str]
    measured_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    score_level: str
    is_concerning: bool
    indicator_display_name: str

    class Config:
        from_attributes = True


class SocialEmotionalIndicatorWithDetails(SocialEmotionalIndicatorResponse):
    """Schema de resposta com detalhes de relacionamentos."""

    student_name: Optional[str] = None
    professional_name: Optional[str] = None
    professional_role: Optional[str] = None


class SocialEmotionalIndicatorListResponse(BaseModel):
    """Schema para lista paginada de indicadores."""

    indicators: list[SocialEmotionalIndicatorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# FILTER/QUERY SCHEMAS
# ============================================================================


class IndicatorFilter(BaseModel):
    """Schema para filtros de busca de indicadores."""

    student_id: Optional[UUID] = None
    professional_id: Optional[UUID] = None
    indicator_type: Optional[IndicatorType] = None
    context: Optional[MeasurementContext] = None
    score_min: Optional[int] = Field(None, ge=1, le=10)
    score_max: Optional[int] = Field(None, ge=1, le=10)
    is_concerning: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = Field(None, description="Busca em observações")


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class IndicatorTrend(BaseModel):
    """Tendência de um indicador ao longo do tempo."""

    indicator_type: IndicatorType
    indicator_display_name: str
    measurements: list[dict[str, any]]
    average_score: float
    trend_direction: str  # "improving", "stable", "declining"
    latest_score: int
    earliest_score: int
    measurement_count: int


class SocialEmotionalProfile(BaseModel):
    """Perfil socioemocional completo de um estudante."""

    student_id: UUID
    student_name: Optional[str] = None
    total_measurements: int
    last_measured_at: Optional[datetime]
    indicators_summary: dict[str, dict[str, any]]
    concerning_indicators: list[str]
    strengths: list[str]
    areas_for_development: list[str]
    trends: list[IndicatorTrend]


class IndicatorComparison(BaseModel):
    """Comparação de indicadores entre períodos."""

    student_id: UUID
    indicator_type: IndicatorType
    period1_start: datetime
    period1_end: datetime
    period1_average: float
    period2_start: datetime
    period2_end: datetime
    period2_average: float
    change_percentage: float
    change_direction: str  # "improved", "stable", "declined"
    statistical_significance: bool


class IndicatorCorrelation(BaseModel):
    """Correlação entre indicadores diferentes."""

    indicator1_type: IndicatorType
    indicator2_type: IndicatorType
    correlation_coefficient: float
    correlation_strength: str  # "strong", "moderate", "weak", "none"
    sample_size: int
    insights: str


# ============================================================================
# BULK OPERATIONS
# ============================================================================


class BulkIndicatorCreate(BaseModel):
    """Schema para criar múltiplos indicadores de uma vez."""

    student_id: UUID
    measured_at: datetime
    indicators: list[dict[str, any]] = Field(
        ...,
        description="Lista de indicadores com type, context, score, etc.",
    )


class BulkIndicatorResponse(BaseModel):
    """Resposta para criação em massa de indicadores."""

    created_count: int
    failed_count: int
    created_ids: list[UUID]
    errors: Optional[list[str]]
