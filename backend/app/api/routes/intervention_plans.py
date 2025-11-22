"""
Intervention Plan API endpoints - Gestão de planos de intervenção multiprofissionais.

Endpoints para criação e gerenciamento colaborativo de planos de intervenção.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, get_professional_id
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.schemas.intervention_plan import (
    InterventionPlanCreate,
    InterventionPlanFilter,
    InterventionPlanListResponse,
    InterventionPlanResponse,
    InterventionPlanStatistics,
    InterventionPlanUpdate,
    ProgressNoteCreate,
)
from app.services.intervention_plan_service import InterventionPlanService

router = APIRouter(prefix="/intervention-plans", tags=["intervention-plans"])


@router.post("/", response_model=InterventionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_intervention_plan(
    plan: InterventionPlanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Cria novo plano de intervenção multiprofissional.

    **Permissões**: Requer autenticação. Profissional autenticado será registrado como criador.

    **Componentes do Plano**:
    - Título e objetivo
    - Estratégias estruturadas
    - Comportamentos-alvo
    - Critérios mensuráveis de sucesso
    - Período (datas início e fim)
    - Frequência de revisão
    - Profissionais envolvidos
    - Materiais necessários

    **Status Inicial**: `draft` (rascunho)

    **Validações**:
    - Data de término > Data de início
    - Pelo menos 1 estratégia
    - Pelo menos 1 comportamento-alvo
    - Critérios de sucesso definidos

    **Retorna**:
    - Plano de intervenção criado

    **Erros**:
    - 404: Estudante ou profissional não encontrado
    - 400: Dados inválidos (datas, etc.)
    """
    try:
        service = InterventionPlanService(db)
        # Use professional_id from header if provided, otherwise fallback to user_id from JWT
        created_by_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.create(plan, created_by_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{plan_id}", response_model=InterventionPlanResponse)
def get_intervention_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Busca plano de intervenção por ID.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Dados completos do plano
    - Lista de profissionais envolvidos
    - Notas de progresso
    - Propriedades calculadas (is_active, days_remaining, needs_review)

    **Erros**:
    - 404: Plano não encontrado
    """
    try:
        service = InterventionPlanService(db)
        return service.get_by_id(plan_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{plan_id}", response_model=InterventionPlanResponse)
def update_intervention_plan(
    plan_id: UUID,
    plan_update: InterventionPlanUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Atualiza plano de intervenção.

    **Permissões**: Apenas profissionais envolvidos no plano podem editá-lo.

    **Campos Atualizáveis**:
    - Título, objetivo, descrição
    - Estratégias, comportamentos-alvo
    - Critérios de sucesso
    - Datas, frequência de revisão
    - Status, percentual de progresso
    - Materiais e recursos

    **Validações**:
    - Profissional deve estar envolvido no plano
    - Data fim > Data início

    **Retorna**:
    - Plano atualizado

    **Erros**:
    - 404: Plano não encontrado
    - 403: Profissional não está envolvido
    - 400: Dados inválidos
    """
    try:
        service = InterventionPlanService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.update(plan_id, plan_update, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intervention_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Remove plano de intervenção.

    **Permissões**: Apenas o profissional que criou o plano pode removê-lo.

    **Erros**:
    - 404: Plano não encontrado
    - 403: Profissional não é o criador
    """
    try:
        service = InterventionPlanService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        service.delete(plan_id, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{plan_id}/progress-notes", response_model=InterventionPlanResponse)
def add_progress_note(
    plan_id: UUID,
    note: ProgressNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Adiciona nota de progresso ao plano.

    **Permissões**: Apenas profissionais envolvidos podem adicionar notas.

    **Nota de Progresso Contém**:
    - Conteúdo (obrigatório)
    - Desafios encontrados
    - Sucessos alcançados
    - Próximos passos
    - Atualização de percentual de progresso (opcional)

    **Efeitos**:
    - Adiciona nota à lista de notas de progresso
    - Atualiza `last_reviewed_at` para agora
    - Atualiza `progress_percentage` se fornecido

    **Retorna**:
    - Plano atualizado com nova nota

    **Erros**:
    - 404: Plano não encontrado
    - 403: Profissional não está envolvido
    """
    try:
        service = InterventionPlanService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.add_progress_note(plan_id, note, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{plan_id}/status", response_model=InterventionPlanResponse)
def change_plan_status(
    plan_id: UUID,
    new_status: str = Query(..., description="Novo status: draft, active, paused, completed, cancelled"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Altera status do plano de intervenção.

    **Permissões**: Apenas profissionais envolvidos podem alterar status.

    **Status Disponíveis**:
    - `draft`: Rascunho (em construção)
    - `active`: Ativo (em execução)
    - `paused`: Pausado temporariamente
    - `completed`: Concluído com sucesso
    - `cancelled`: Cancelado

    **Retorna**:
    - Plano com status atualizado

    **Erros**:
    - 404: Plano não encontrado
    - 403: Profissional não está envolvido
    """
    try:
        from app.models.intervention_plan import PlanStatus

        service = InterventionPlanService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.change_status(plan_id, PlanStatus(new_status), professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido")


@router.post("/{plan_id}/professionals/{professional_id}", response_model=InterventionPlanResponse)
def add_professional_to_plan(
    plan_id: UUID,
    professional_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Adiciona profissional ao plano de intervenção.

    **Permissões**: Apenas o criador do plano pode adicionar profissionais.

    **Retorna**:
    - Plano atualizado com novo profissional

    **Erros**:
    - 404: Plano ou profissional não encontrado
    - 403: Usuário não é o criador do plano
    - 400: Profissional já está envolvido
    """
    try:
        service = InterventionPlanService(db)
        requesting_professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.add_professional(plan_id, professional_id, requesting_professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{plan_id}/professionals/{professional_id}", response_model=InterventionPlanResponse)
def remove_professional_from_plan(
    plan_id: UUID,
    professional_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Remove profissional do plano de intervenção.

    **Permissões**: Apenas o criador do plano pode remover profissionais.

    **Retorna**:
    - Plano atualizado

    **Erros**:
    - 404: Plano não encontrado ou profissional não está envolvido
    - 403: Usuário não é o criador do plano
    """
    try:
        service = InterventionPlanService(db)
        requesting_professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.remove_professional(plan_id, professional_id, requesting_professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/", response_model=InterventionPlanListResponse)
def list_intervention_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[UUID] = Query(None, description="Filtrar por estudante"),
    created_by_id: Optional[UUID] = Query(None, description="Filtrar por criador"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por profissional envolvido"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    search: Optional[str] = Query(None, description="Buscar em título e objetivo"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Lista planos de intervenção com filtros e paginação.

    **Permissões**: Requer autenticação.

    **Filtros Disponíveis**:
    - `student_id`: Planos de um estudante específico
    - `created_by_id`: Planos criados por profissional específico
    - `professional_id`: Planos em que profissional está envolvido
    - `status`: Status do plano (draft, active, etc.)
    - `search`: Busca no título e objetivo

    **Ordenação**: Mais recentes primeiro

    **Retorna**:
    - Lista paginada de planos
    - Total de registros
    - Informações de paginação
    """
    filters = InterventionPlanFilter(
        student_id=student_id,
        created_by_id=created_by_id,
        professional_id=professional_id,
        status=status,
        search=search,
    )

    service = InterventionPlanService(db)
    plans, total = service.list(skip=skip, limit=limit, filters=filters)

    total_pages = (total + limit - 1) // limit

    return InterventionPlanListResponse(
        plans=plans,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/student/{student_id}/list", response_model=InterventionPlanListResponse)
def list_plans_by_student(
    student_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Lista todos os planos de um estudante específico.

    **Retorna**:
    - Todos os planos (ativos, concluídos, cancelados, etc.)
    - Ordenados por data de criação
    """
    service = InterventionPlanService(db)
    plans, total = service.get_by_student(student_id, skip=skip, limit=limit)

    total_pages = (total + limit - 1) // limit

    return InterventionPlanListResponse(
        plans=plans,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/active/list", response_model=InterventionPlanListResponse)
def list_active_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Lista apenas planos ativos.

    **Útil para**:
    - Dashboard de planos em execução
    - Acompanhamento de intervenções em andamento

    **Retorna**:
    - Apenas planos com status `active`
    """
    service = InterventionPlanService(db)
    plans, total = service.get_active_plans(skip=skip, limit=limit)

    total_pages = (total + limit - 1) // limit

    return InterventionPlanListResponse(
        plans=plans,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/statistics/overview", response_model=InterventionPlanStatistics)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Obtém estatísticas agregadas de planos de intervenção.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Total de planos
    - Planos ativos e concluídos
    - Distribuição por status
    - Progresso médio
    - Planos que precisam revisão
    - Distribuição por estudante
    - Duração média (dias)

    **Útil para**:
    - Dashboards administrativos
    - Relatórios gerenciais
    - Análise de efetividade
    """
    service = InterventionPlanService(db)
    return service.get_statistics()
