"""
Intervention Plan Pydantic schemas - DTOs para planos de intervenção.

Schemas de validação e serialização para planos de intervenção multiprofissionais.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.intervention_plan import PlanStatus, ReviewFrequency


# ============================================================================
# CREATE SCHEMAS
# ============================================================================


class InterventionPlanCreate(BaseModel):
    """Schema para criação de plano de intervenção."""

    student_id: UUID = Field(..., description="ID do estudante")
    title: str = Field(..., min_length=5, max_length=500, description="Título do plano")
    objective: str = Field(..., min_length=20, description="Objetivo principal do plano")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    strategies: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Estratégias a serem implementadas",
    )
    target_behaviors: list[str] = Field(
        ...,
        min_length=1,
        description="Comportamentos-alvo",
    )
    success_criteria: dict[str, Any] = Field(
        ..., description="Critérios mensuráveis de sucesso"
    )
    professionals_involved_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs dos profissionais envolvidos",
    )
    start_date: date = Field(..., description="Data de início")
    end_date: date = Field(..., description="Data de término")
    review_frequency: ReviewFrequency = Field(
        default=ReviewFrequency.WEEKLY,
        description="Frequência de revisão",
    )
    required_materials: Optional[list[str]] = Field(None, description="Materiais necessários")
    resources: Optional[dict[str, Any]] = Field(None, description="Recursos adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Desenvolvimento de Habilidades de Comunicação Social",
                "objective": "Aumentar iniciativa de comunicação espontânea em 50% em contextos sociais",
                "description": "Plano integrado envolvendo professor, fonoaudióloga e psicóloga para desenvolvimento de comunicação funcional",
                "strategies": [
                    {
                        "name": "Modelagem de Comunicação",
                        "description": "Adulto modela frases simples em contextos naturais",
                        "frequency": "5x por dia",
                        "responsible": "Professor",
                    },
                    {
                        "name": "Reforço Positivo",
                        "description": "Reforçar tentativas de comunicação espontânea",
                        "frequency": "Contínuo",
                        "responsible": "Equipe",
                    },
                ],
                "target_behaviors": [
                    "Iniciar comunicação para pedir ajuda",
                    "Fazer comentários sobre atividades",
                    "Responder perguntas sociais",
                ],
                "success_criteria": {
                    "baseline": "2 iniciativas espontâneas por dia",
                    "goal": "10 iniciativas espontâneas por dia",
                    "measurement": "Registro diário por professora",
                    "timeline": "12 semanas",
                },
                "start_date": "2025-02-01",
                "end_date": "2025-04-30",
                "review_frequency": "weekly",
                "required_materials": ["Cartões de comunicação", "Registro de observação"],
            }
        }


class InterventionPlanUpdate(BaseModel):
    """Schema para atualização de plano de intervenção."""

    title: Optional[str] = Field(None, min_length=5, max_length=500)
    objective: Optional[str] = Field(None, min_length=20)
    description: Optional[str] = None
    strategies: Optional[list[dict[str, Any]]] = None
    target_behaviors: Optional[list[str]] = None
    success_criteria: Optional[dict[str, Any]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    review_frequency: Optional[ReviewFrequency] = None
    status: Optional[PlanStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    required_materials: Optional[list[str]] = None
    resources: Optional[dict[str, Any]] = None


class ProgressNoteCreate(BaseModel):
    """Schema para adicionar nota de progresso ao plano."""

    content: str = Field(..., min_length=10, description="Conteúdo da nota de progresso")
    progress_percentage: Optional[int] = Field(
        None, ge=0, le=100, description="Atualização do percentual de progresso"
    )
    challenges: Optional[str] = Field(None, description="Desafios encontrados")
    successes: Optional[str] = Field(None, description="Sucessos alcançados")
    next_steps: Optional[str] = Field(None, description="Próximos passos")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class InterventionPlanResponse(BaseModel):
    """Schema de resposta para plano de intervenção."""

    id: UUID
    student_id: UUID
    created_by_id: UUID
    title: str
    objective: str
    description: Optional[str]
    strategies: list[dict[str, Any]]
    target_behaviors: list[str]
    success_criteria: dict[str, Any]
    start_date: date
    end_date: date
    review_frequency: ReviewFrequency
    status: PlanStatus
    progress_percentage: int
    progress_notes: Optional[list[dict[str, Any]]]
    required_materials: Optional[list[str]]
    resources: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    last_reviewed_at: Optional[datetime]
    is_active: bool
    days_remaining: int
    needs_review: bool

    class Config:
        from_attributes = True


class InterventionPlanWithDetails(InterventionPlanResponse):
    """Schema de resposta com detalhes de relacionamentos."""

    student_name: Optional[str] = None
    created_by_name: Optional[str] = None
    professionals_involved: Optional[list[dict[str, Any]]] = None


class InterventionPlanListResponse(BaseModel):
    """Schema para lista paginada de planos de intervenção."""

    plans: list[InterventionPlanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InterventionPlanSummary(BaseModel):
    """Schema resumido de plano (para listas e dashboards)."""

    id: UUID
    student_id: UUID
    title: str
    status: PlanStatus
    progress_percentage: int
    start_date: date
    end_date: date
    days_remaining: int
    needs_review: bool

    class Config:
        from_attributes = True


# ============================================================================
# FILTER/QUERY SCHEMAS
# ============================================================================


class InterventionPlanFilter(BaseModel):
    """Schema para filtros de busca de planos."""

    student_id: Optional[UUID] = None
    created_by_id: Optional[UUID] = None
    professional_id: Optional[UUID] = Field(
        None, description="Filtrar por profissional envolvido"
    )
    status: Optional[PlanStatus] = None
    review_frequency: Optional[ReviewFrequency] = None
    needs_review: Optional[bool] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    progress_min: Optional[int] = Field(None, ge=0, le=100)
    progress_max: Optional[int] = Field(None, ge=0, le=100)
    search: Optional[str] = Field(None, description="Busca em título e objetivo")


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class InterventionPlanStatistics(BaseModel):
    """Estatísticas de planos de intervenção."""

    total_plans: int
    active_plans: int
    completed_plans: int
    by_status: dict[str, int]
    average_progress: float
    needs_review_count: int
    by_student: dict[str, int]
    average_duration_days: float


class InterventionPlanEffectiveness(BaseModel):
    """Análise de efetividade de planos de intervenção."""

    plan_id: UUID
    success_rate: float
    completed_on_time: bool
    average_progress_per_week: float
    challenges_count: int
    successes_count: int
    recommendation: str
