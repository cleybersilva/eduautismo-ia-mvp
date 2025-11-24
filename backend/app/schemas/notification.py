"""
Schemas de Notificação
======================

Define schemas Pydantic para validação de dados de notificações.

Autor: Claude Code
Data: 2025-11-24
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.notification import NotificationPriority, NotificationType


class NotificationBase(BaseModel):
    """Schema base de notificação."""

    type: NotificationType = Field(..., description="Tipo da notificação")
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM, description="Prioridade da notificação"
    )
    title: str = Field(..., min_length=1, max_length=255, description="Título da notificação")
    message: str = Field(..., min_length=1, description="Mensagem da notificação")
    intervention_plan_id: Optional[UUID] = Field(None, description="ID do plano relacionado")
    action_url: Optional[str] = Field(None, max_length=500, description="URL de ação")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")


class NotificationCreate(NotificationBase):
    """Schema para criar notificação."""

    user_id: UUID = Field(..., description="ID do usuário destinatário")


class NotificationUpdate(BaseModel):
    """Schema para atualizar notificação."""

    is_read: Optional[bool] = Field(None, description="Marca como lida/não lida")


class NotificationResponse(NotificationBase):
    """Schema de resposta de notificação."""

    id: UUID
    user_id: UUID
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    is_expired: bool

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema de resposta para lista de notificações."""

    items: list[NotificationResponse]
    total: int
    unread_count: int
    has_more: bool


class NotificationStats(BaseModel):
    """Estatísticas de notificações."""

    total: int
    unread: int
    by_type: dict[str, int]
    by_priority: dict[str, int]
    urgent_count: int
