"""
Rotas de Exportação
===================

Endpoints REST para exportação de dados em CSV e Excel.

Autor: Claude Code
Data: 2025-11-24
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.services.export_service import ExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/pending-review/summary", response_model=dict, status_code=status.HTTP_200_OK)
async def get_export_summary(
    priority: Optional[str] = Query(None, description="Filtrar por prioridade (high/medium/low)"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por ID do profissional"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna resumo dos dados que serão exportados.

    Útil para mostrar ao usuário quantos registros serão exportados
    antes de realizar a exportação completa.

    **Returns:**
    - total: Total de planos que serão exportados
    - high_priority: Planos de alta prioridade
    - medium_priority: Planos de média prioridade
    - low_priority: Planos de baixa prioridade
    - excel_available: Se exportação Excel está disponível
    """
    logger.info(
        "Fetching export summary",
        extra={
            "user_id": current_user.get("user_id"),
            "priority_filter": priority,
            "professional_id": str(professional_id) if professional_id else None,
        },
    )

    service = ExportService(db)
    summary = service.get_export_summary(
        priority_filter=priority, professional_id=professional_id
    )

    return summary


@router.get("/pending-review/csv", status_code=status.HTTP_200_OK)
async def export_pending_review_csv(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(1000, ge=1, le=1000, description="Limite de registros (máximo 1000)"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridade (high/medium/low)"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por ID do profissional"),
    include_student: bool = Query(False, description="Incluir dados do aluno"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Exporta planos pendentes de revisão para CSV.

    **Formato:**
    - CSV com cabeçalhos em português
    - Encoding UTF-8 com BOM (para Excel)
    - Campos separados por vírgula
    - Valores entre aspas

    **Filtros:**
    - priority: Filtrar por prioridade
    - professional_id: Filtrar por profissional
    - include_student: Incluir dados do aluno (nome, idade, etc)

    **Limites:**
    - Máximo 1000 registros por exportação
    - Para mais registros, usar paginação com skip

    **Download:**
    O arquivo será baixado automaticamente com nome:
    `planos_pendentes_YYYYMMDD_HHMMSS.csv`
    """
    logger.info(
        "Exporting pending review plans to CSV",
        extra={
            "user_id": current_user.get("user_id"),
            "skip": skip,
            "limit": limit,
            "priority_filter": priority,
            "professional_id": str(professional_id) if professional_id else None,
            "include_student": include_student,
        },
    )

    service = ExportService(db)

    csv_data = service.export_to_csv(
        skip=skip,
        limit=limit,
        priority_filter=priority,
        professional_id=professional_id,
        include_student=include_student,
    )

    if not csv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plans found to export",
        )

    # Adicionar BOM para UTF-8 (Excel compatibility)
    csv_with_bom = "\ufeff" + csv_data

    # Nome do arquivo com timestamp
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"planos_pendentes_{timestamp}.csv"

    logger.info(
        f"CSV export completed",
        extra={"filename": filename, "size_bytes": len(csv_with_bom)},
    )

    return Response(
        content=csv_with_bom.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get("/pending-review/excel", status_code=status.HTTP_200_OK)
async def export_pending_review_excel(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(1000, ge=1, le=1000, description="Limite de registros (máximo 1000)"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridade (high/medium/low)"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por ID do profissional"),
    include_student: bool = Query(False, description="Incluir dados do aluno"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Exporta planos pendentes de revisão para Excel (.xlsx).

    **Formato:**
    - Arquivo Excel (.xlsx) com formatação
    - Cabeçalhos em negrito com cor de fundo azul
    - Células de prioridade coloridas:
      - Alta: Vermelho claro
      - Média: Amarelo claro
      - Baixa: Verde claro
    - Aba adicional com resumo da exportação

    **Filtros:**
    - priority: Filtrar por prioridade
    - professional_id: Filtrar por profissional
    - include_student: Incluir dados do aluno

    **Requisitos:**
    - Requer biblioteca openpyxl instalada
    - Se não disponível, usar endpoint CSV

    **Download:**
    O arquivo será baixado automaticamente com nome:
    `planos_pendentes_YYYYMMDD_HHMMSS.xlsx`
    """
    logger.info(
        "Exporting pending review plans to Excel",
        extra={
            "user_id": current_user.get("user_id"),
            "skip": skip,
            "limit": limit,
            "priority_filter": priority,
            "professional_id": str(professional_id) if professional_id else None,
            "include_student": include_student,
        },
    )

    service = ExportService(db)

    excel_data = service.export_to_excel(
        skip=skip,
        limit=limit,
        priority_filter=priority,
        professional_id=professional_id,
        include_student=include_student,
    )

    if excel_data is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Excel export not available. Install openpyxl package or use CSV export.",
        )

    if not excel_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plans found to export",
        )

    # Nome do arquivo com timestamp
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"planos_pendentes_{timestamp}.xlsx"

    logger.info(
        f"Excel export completed",
        extra={"filename": filename, "size_bytes": len(excel_data)},
    )

    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
