"""
Modelo de Notificação
=====================

Define estrutura de notificações para alertar profissionais sobre
eventos importantes relacionados a planos de intervenção.

Autor: Claude Code
Data: 2025-11-24
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.types import GUID


class NotificationType(str, Enum):
    """Tipos de notificação."""

    REVIEW_OVERDUE = "review_overdue"  # Revisão atrasada
    REVIEW_DUE_SOON = "review_due_soon"  # Revisão próxima do vencimento
    PLAN_CREATED = "plan_created"  # Novo plano criado
    PLAN_UPDATED = "plan_updated"  # Plano atualizado
    PLAN_REVIEWED = "plan_reviewed"  # Plano revisado
    HIGH_PRIORITY = "high_priority"  # Plano de alta prioridade
    SYSTEM = "system"  # Notificação do sistema


class NotificationPriority(str, Enum):
    """Prioridade da notificação."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Modelo de notificação.

    Representa notificações enviadas aos profissionais sobre
    eventos relacionados a planos de intervenção.
    """

    __tablename__ = "notifications"

    id = Column(GUID, primary_key=True, default=func.uuid_generate_v4())

    # Destinatário
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e prioridade
    type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
    )

    priority = Column(
        SQLEnum(NotificationPriority),
        nullable=False,
        default=NotificationPriority.MEDIUM,
        index=True,
    )

    # Conteúdo
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Relacionamento com plano (opcional)
    intervention_plan_id = Column(
        GUID,
        ForeignKey("intervention_plans.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Estado
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Ação (link ou comando)
    action_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
    intervention_plan = relationship("InterventionPlan", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id}, is_read={self.is_read})>"

    def mark_as_read(self):
        """Marca notificação como lida."""
        self.is_read = True
        self.read_at = datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Verifica se notificação expirou."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "intervention_plan_id": str(self.intervention_plan_id) if self.intervention_plan_id else None,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "action_url": self.action_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired,
        }
