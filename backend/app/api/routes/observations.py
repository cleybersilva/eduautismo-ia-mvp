"""
Observation API endpoints - Gestão de observações profissionais.

Endpoints para registro e consulta de observações multiprofissionais sobre estudantes.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, NotFoundException
from app.schemas.observation import (
    ObservationFilter,
    ObservationSummary,
    ProfessionalObservationCreate,
    ProfessionalObservationListResponse,
    ProfessionalObservationResponse,
    ProfessionalObservationUpdate,
)
from app.services.observation_service import ObservationService

router = APIRouter(prefix="/api/v1/observations", tags=["observations"])


@router.post("/", response_model=ProfessionalObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(
    observation: ProfessionalObservationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria nova observação profissional sobre estudante.

    **Permissões**: Requer autenticação. Profissional autenticado será registrado como autor.

    **Tipos de Observação**:
    - behavioral: Comportamental
    - academic: Acadêmica/Pedagógica
    - social: Interação Social
    - emotional: Socioemocional
    - sensory: Sensorial
    - communication: Comunicação
    - motor: Motor/Físico
    - clinical: Clínica (apenas profissionais de saúde)
    - general: Observação Geral

    **Níveis de Severidade**:
    - 1: Muito baixo
    - 2: Baixo
    - 3: Moderado
    - 4: Alto
    - 5: Crítico

    **Privacidade**:
    - `is_private=true`: Visível apenas para profissionais de saúde
    - `is_private=false`: Visível para todos os profissionais autorizados

    **Retorna**:
    - Observação criada com ID gerado

    **Erros**:
    - 404: Estudante não encontrado
    """
    try:
        service = ObservationService(db)
        professional_id = UUID(current_user["user_id"])
        return service.create(observation, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{observation_id}", response_model=ProfessionalObservationResponse)
def get_observation(
    observation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Busca observação por ID.

    **Permissões**: Requer autenticação.
    - Observações privadas: apenas profissionais de saúde
    - Observações públicas: todos os profissionais autenticados

    **Retorna**:
    - Dados completos da observação

    **Erros**:
    - 404: Observação não encontrada
    - 403: Sem permissão para acessar observação privada
    """
    try:
        service = ObservationService(db)
        professional_id = UUID(current_user["user_id"])
        return service.get_by_id(observation_id, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{observation_id}", response_model=ProfessionalObservationResponse)
def update_observation(
    observation_id: UUID,
    observation_update: ProfessionalObservationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Atualiza observação existente.

    **Permissões**: Apenas o profissional que criou a observação pode editá-la.

    **Retorna**:
    - Observação atualizada

    **Erros**:
    - 404: Observação não encontrada
    - 403: Sem permissão (não é o autor)
    """
    try:
        service = ObservationService(db)
        professional_id = UUID(current_user["user_id"])
        return service.update(observation_id, observation_update, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_observation(
    observation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Remove observação.

    **Permissões**: Apenas o profissional que criou a observação pode removê-la.

    **Erros**:
    - 404: Observação não encontrada
    - 403: Sem permissão (não é o autor)
    """
    try:
        service = ObservationService(db)
        professional_id = UUID(current_user["user_id"])
        service.delete(observation_id, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/", response_model=ProfessionalObservationListResponse)
def list_observations(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    student_id: Optional[UUID] = Query(None, description="Filtrar por estudante"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por profissional"),
    observation_type: Optional[str] = Query(None, description="Filtrar por tipo de observação"),
    context: Optional[str] = Query(None, description="Filtrar por contexto"),
    severity_min: Optional[int] = Query(None, ge=1, le=5, description="Severidade mínima"),
    severity_max: Optional[int] = Query(None, ge=1, le=5, description="Severidade máxima"),
    requires_intervention: Optional[bool] = Query(None, description="Requer intervenção"),
    search: Optional[str] = Query(None, description="Buscar no conteúdo"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista observações com filtros e paginação.

    **Permissões**: Requer autenticação.
    - Profissionais de educação: veem apenas observações não privadas
    - Profissionais de saúde: veem todas as observações

    **Filtros Disponíveis**:
    - `student_id`: ID do estudante
    - `professional_id`: ID do profissional que criou
    - `observation_type`: Tipo de observação
    - `context`: Contexto da observação
    - `severity_min/max`: Range de severidade
    - `requires_intervention`: Observações que requerem intervenção
    - `search`: Busca no conteúdo da observação

    **Paginação**:
    - `skip`: Número de registros para pular
    - `limit`: Número máximo de registros (máximo: 1000)

    **Ordenação**: Mais recentes primeiro (por `observed_at`)

    **Retorna**:
    - Lista paginada de observações
    - Total de registros
    - Informações de paginação
    """
    filters = ObservationFilter(
        student_id=student_id,
        professional_id=professional_id,
        observation_type=observation_type,
        context=context,
        severity_level_min=severity_min,
        severity_level_max=severity_max,
        requires_intervention=requires_intervention,
        search=search,
    )

    service = ObservationService(db)
    requesting_professional_id = UUID(current_user["user_id"])
    observations, total = service.list(
        skip=skip,
        limit=limit,
        filters=filters,
        requesting_professional_id=requesting_professional_id,
    )

    total_pages = (total + limit - 1) // limit

    return ProfessionalObservationListResponse(
        observations=observations,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/student/{student_id}/list", response_model=ProfessionalObservationListResponse)
def list_observations_by_student(
    student_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista todas as observações de um estudante específico.

    **Permissões**: Requer autenticação.
    - Respeita controle de privacidade (profissionais de educação não veem observações privadas)

    **Retorna**:
    - Lista paginada de observações do estudante
    - Ordenadas por data (mais recentes primeiro)
    """
    service = ObservationService(db)
    requesting_professional_id = UUID(current_user["user_id"])
    observations, total = service.get_by_student(
        student_id=student_id,
        skip=skip,
        limit=limit,
        requesting_professional_id=requesting_professional_id,
    )

    total_pages = (total + limit - 1) // limit

    return ProfessionalObservationListResponse(
        observations=observations,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/student/{student_id}/summary", response_model=ObservationSummary)
def get_student_observation_summary(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Gera resumo analítico de observações de um estudante.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Total de observações
    - Distribuição por tipo
    - Distribuição por severidade
    - Observações que requerem intervenção
    - Contextos mais comuns (top 5)
    - Tags mais comuns (top 10)
    - Últimas 10 observações

    **Útil para**:
    - Dashboards
    - Relatórios
    - Identificação de padrões
    """
    try:
        service = ObservationService(db)
        requesting_professional_id = UUID(current_user["user_id"])
        return service.get_summary_by_student(student_id, requesting_professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/requiring-intervention/list", response_model=ProfessionalObservationListResponse)
def list_observations_requiring_intervention(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista observações que requerem intervenção imediata.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Observações marcadas como `requires_intervention=true`
    - Ordenadas por severidade (mais graves primeiro)

    **Útil para**:
    - Alertas e notificações
    - Priorização de ações
    - Dashboard de urgências
    """
    service = ObservationService(db)
    observations, total = service.get_requiring_intervention(skip=skip, limit=limit)

    total_pages = (total + limit - 1) // limit

    return ProfessionalObservationListResponse(
        observations=observations,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )
