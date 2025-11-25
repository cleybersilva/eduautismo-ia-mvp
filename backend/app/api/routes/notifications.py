"""
Rotas de Notificações
======================

Endpoints REST para gerenciamento de notificações.

Autor: Claude Code
Data: 2025-11-24
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.notification import NotificationPriority, NotificationType
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationStats,
    NotificationUpdate,
)
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def list_notifications(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    unread_only: bool = Query(False, description="Retornar apenas não lidas"),
    type: Optional[NotificationType] = Query(None, description="Filtrar por tipo"),
    priority: Optional[NotificationPriority] = Query(None, description="Filtrar por prioridade"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista notificações do usuário autenticado.

    **Filtros disponíveis:**
    - unread_only: Apenas notificações não lidas
    - type: Tipo de notificação
    - priority: Prioridade da notificação

    **Paginação:**
    - skip: Offset
    - limit: Limite de resultados (máximo 100)

    **Ordenação:**
    - Por prioridade (decrescente)
    - Por data de criação (mais recentes primeiro)
    """
    user_id = UUID(current_user.get("user_id"))

    logger.info(
        "Listing notifications",
        extra={
            "user_id": str(user_id),
            "skip": skip,
            "limit": limit,
            "unread_only": unread_only,
            "type_filter": type.value if type else None,
            "priority_filter": priority.value if priority else None,
        },
    )

    service = NotificationService(db)

    # Obter notificações
    notifications, total = service.get_user_notifications(
        user_id=user_id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        type_filter=type,
        priority_filter=priority,
    )

    # Contar não lidas
    unread_count = service.get_unread_count(user_id)

    # Converter para response
    items = [NotificationResponse.model_validate(n) for n in notifications]

    return NotificationListResponse(
        items=items, total=total, unread_count=unread_count, has_more=(skip + len(items)) < total
    )


@router.get("/unread-count", response_model=dict, status_code=status.HTTP_200_OK)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna número de notificações não lidas.

    Útil para exibir badge de notificações pendentes.
    """
    user_id = UUID(current_user.get("user_id"))

    service = NotificationService(db)
    count = service.get_unread_count(user_id)

    return {"unread_count": count}


@router.get("/stats", response_model=NotificationStats, status_code=status.HTTP_200_OK)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retorna estatísticas de notificações do usuário.

    Inclui:
    - Total de notificações
    - Não lidas
    - Distribuição por tipo
    - Distribuição por prioridade
    - Urgentes não lidas
    """
    user_id = UUID(current_user.get("user_id"))

    logger.info(f"Fetching notification stats for user {user_id}")

    service = NotificationService(db)
    stats = service.get_notification_stats(user_id)

    return stats


@router.patch("/{notification_id}", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def update_notification(
    notification_id: UUID,
    update_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Atualiza notificação (marcar como lida/não lida).

    Args:
        notification_id: ID da notificação
        update_data: Dados para atualização

    Returns:
        Notificação atualizada
    """
    user_id = UUID(current_user.get("user_id"))

    logger.info(
        f"Updating notification {notification_id}",
        extra={"user_id": str(user_id), "is_read": update_data.is_read},
    )

    service = NotificationService(db)

    # Atualizar
    if update_data.is_read is not None:
        notification = service.mark_as_read(notification_id, user_id)

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or unauthorized",
            )

        return NotificationResponse.model_validate(notification)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No valid update fields provided",
    )


@router.post("/mark-all-read", response_model=dict, status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Marca todas notificações do usuário como lidas.

    Returns:
        Número de notificações atualizadas
    """
    user_id = UUID(current_user.get("user_id"))

    logger.info(f"Marking all notifications as read for user {user_id}")

    service = NotificationService(db)
    count = service.mark_all_as_read(user_id)

    return {"updated_count": count, "message": f"{count} notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Deleta notificação.

    Args:
        notification_id: ID da notificação

    Returns:
        204 No Content se deletada com sucesso
    """
    user_id = UUID(current_user.get("user_id"))

    logger.info(f"Deleting notification {notification_id} for user {user_id}")

    service = NotificationService(db)
    deleted = service.delete_notification(notification_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or unauthorized",
        )

    return None
