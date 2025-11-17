"""
Professional API endpoints - Gestão de profissionais do sistema multiprofissional.

Endpoints para CRUD e gerenciamento de profissionais.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalFilter,
    ProfessionalListResponse,
    ProfessionalResponse,
    ProfessionalStatistics,
    ProfessionalUpdate,
)
from app.services.professional_service import ProfessionalService

router = APIRouter(prefix="/api/v1/professionals", tags=["professionals"])


@router.post("/", response_model=ProfessionalResponse, status_code=status.HTTP_201_CREATED)
def create_professional(
    professional: ProfessionalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria novo profissional no sistema.

    **Permissões**: Requer autenticação.

    **Validações**:
    - Email deve ser único no sistema
    - Todos os campos obrigatórios devem ser fornecidos

    **Retorna**:
    - Profissional criado com ID gerado
    """
    try:
        service = ProfessionalService(db)
        return service.create(professional)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{professional_id}", response_model=ProfessionalResponse)
def get_professional(
    professional_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Busca profissional por ID.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Dados completos do profissional

    **Erros**:
    - 404: Profissional não encontrado
    """
    try:
        service = ProfessionalService(db)
        return service.get_by_id(professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(
    professional_id: UUID,
    professional_update: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Atualiza dados do profissional.

    **Permissões**: Requer autenticação.

    **Validações**:
    - Email deve ser único (se atualizado)

    **Retorna**:
    - Profissional atualizado

    **Erros**:
    - 404: Profissional não encontrado
    - 400: Email já existe (se alterado)
    """
    try:
        service = ProfessionalService(db)
        return service.update(professional_id, professional_update)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional(
    professional_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Remove profissional (soft delete - marca como inativo).

    **Permissões**: Requer autenticação.

    **Nota**: Esta é uma operação de soft delete. O profissional não é
    removido do banco, apenas marcado como inativo.

    **Erros**:
    - 404: Profissional não encontrado
    """
    try:
        service = ProfessionalService(db)
        service.delete(professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=ProfessionalListResponse)
def list_professionals(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    role: Optional[str] = Query(None, description="Filtrar por função"),
    organization: Optional[str] = Query(None, description="Filtrar por organização"),
    is_active: Optional[bool] = Query(True, description="Filtrar por status"),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    is_education: Optional[bool] = Query(None, description="Apenas profissionais de educação"),
    is_health: Optional[bool] = Query(None, description="Apenas profissionais de saúde"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista profissionais com filtros e paginação.

    **Permissões**: Requer autenticação.

    **Filtros Disponíveis**:
    - `role`: Função do profissional (teacher, psychologist, etc.)
    - `organization`: Nome da organização (busca parcial)
    - `is_active`: Apenas ativos (true) ou inativos (false)
    - `search`: Busca por nome ou email (busca parcial)
    - `is_education`: Apenas profissionais de educação
    - `is_health`: Apenas profissionais de saúde

    **Paginação**:
    - `skip`: Número de registros para pular (padrão: 0)
    - `limit`: Número máximo de registros (padrão: 100, máximo: 1000)

    **Retorna**:
    - Lista paginada de profissionais
    - Total de registros
    - Informações de paginação
    """
    filters = ProfessionalFilter(
        role=role,
        organization=organization,
        is_active=is_active,
        search=search,
        is_education=is_education,
        is_health=is_health,
    )

    service = ProfessionalService(db)
    professionals, total = service.list(skip=skip, limit=limit, filters=filters)

    total_pages = (total + limit - 1) // limit

    return ProfessionalListResponse(
        professionals=professionals,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/statistics/overview", response_model=ProfessionalStatistics)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtém estatísticas agregadas de profissionais.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Total de profissionais
    - Total de ativos/inativos
    - Distribuição por função
    - Profissionais de educação vs saúde
    - Número de organizações
    """
    service = ProfessionalService(db)
    return service.get_statistics()
