"""
Serviço de Notificações
========================

Gerencia criação, envio e listagem de notificações para profissionais.

Autor: Claude Code
Data: 2025-11-24
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.intervention_plan import InterventionPlan
from app.models.notification import Notification, NotificationPriority, NotificationType
from app.schemas.notification import NotificationCreate, NotificationStats

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço para gerenciamento de notificações."""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """
        Cria nova notificação.

        Args:
            notification_data: Dados da notificação

        Returns:
            Notificação criada
        """
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            priority=notification_data.priority,
            title=notification_data.title,
            message=notification_data.message,
            intervention_plan_id=notification_data.intervention_plan_id,
            action_url=notification_data.action_url,
            expires_at=notification_data.expires_at,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        logger.info(
            "Notification created",
            extra={
                "notification_id": str(notification.id),
                "user_id": str(notification.user_id),
                "type": notification.type.value,
                "priority": notification.priority.value,
            },
        )

        return notification

    def get_user_notifications(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        type_filter: Optional[NotificationType] = None,
        priority_filter: Optional[NotificationPriority] = None,
    ) -> tuple[List[Notification], int]:
        """
        Lista notificações do usuário.

        Args:
            user_id: ID do usuário
            skip: Offset para paginação
            limit: Limite de resultados
            unread_only: Se True, retorna apenas não lidas
            type_filter: Filtrar por tipo
            priority_filter: Filtrar por prioridade

        Returns:
            (lista de notificações, total)
        """
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        # Aplicar filtros
        if unread_only:
            query = query.filter(Notification.is_read == False)

        if type_filter:
            query = query.filter(Notification.type == type_filter)

        if priority_filter:
            query = query.filter(Notification.priority == priority_filter)

        # Excluir notificações expiradas
        query = query.filter(
            or_(Notification.expires_at.is_(None), Notification.expires_at > datetime.utcnow())
        )

        # Total
        total = query.count()

        # Ordenar por prioridade e data
        notifications = (
            query.order_by(
                Notification.priority.desc(), Notification.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.info(
            "Fetched user notifications",
            extra={
                "user_id": str(user_id),
                "total": total,
                "returned": len(notifications),
                "unread_only": unread_only,
            },
        )

        return notifications, total

    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        """
        Marca notificação como lida.

        Args:
            notification_id: ID da notificação
            user_id: ID do usuário (validação)

        Returns:
            Notificação atualizada ou None
        """
        notification = (
            self.db.query(Notification)
            .filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            )
            .first()
        )

        if not notification:
            logger.warning(
                f"Notification not found or unauthorized: {notification_id} for user {user_id}"
            )
            return None

        notification.mark_as_read()
        self.db.commit()
        self.db.refresh(notification)

        logger.info(f"Notification marked as read: {notification_id}")
        return notification

    def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas notificações do usuário como lidas.

        Args:
            user_id: ID do usuário

        Returns:
            Número de notificações atualizadas
        """
        count = (
            self.db.query(Notification)
            .filter(and_(Notification.user_id == user_id, Notification.is_read == False))
            .update({"is_read": True, "read_at": datetime.utcnow()})
        )

        self.db.commit()

        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    def delete_notification(self, notification_id: UUID, user_id: UUID) -> bool:
        """
        Deleta notificação.

        Args:
            notification_id: ID da notificação
            user_id: ID do usuário (validação)

        Returns:
            True se deletada, False caso contrário
        """
        notification = (
            self.db.query(Notification)
            .filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            )
            .first()
        )

        if not notification:
            return False

        self.db.delete(notification)
        self.db.commit()

        logger.info(f"Notification deleted: {notification_id}")
        return True

    def get_unread_count(self, user_id: UUID) -> int:
        """
        Conta notificações não lidas do usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Número de notificações não lidas
        """
        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow(),
                    ),
                )
            )
            .count()
        )

        return count

    def get_notification_stats(self, user_id: UUID) -> NotificationStats:
        """
        Obtém estatísticas de notificações do usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Estatísticas de notificações
        """
        # Total
        total = self.db.query(Notification).filter(Notification.user_id == user_id).count()

        # Não lidas
        unread = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow(),
                    ),
                )
            )
            .count()
        )

        # Por tipo
        by_type_query = (
            self.db.query(Notification.type, func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .group_by(Notification.type)
            .all()
        )
        by_type = {str(type_val.value): count for type_val, count in by_type_query}

        # Por prioridade
        by_priority_query = (
            self.db.query(Notification.priority, func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .group_by(Notification.priority)
            .all()
        )
        by_priority = {
            str(priority_val.value): count for priority_val, count in by_priority_query
        }

        # Urgentes não lidas
        urgent_count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.priority == NotificationPriority.URGENT,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow(),
                    ),
                )
            )
            .count()
        )

        return NotificationStats(
            total=total,
            unread=unread,
            by_type=by_type,
            by_priority=by_priority,
            urgent_count=urgent_count,
        )

    def cleanup_expired_notifications(self, days_to_keep: int = 30) -> int:
        """
        Remove notificações expiradas antigas.

        Args:
            days_to_keep: Dias para manter notificações expiradas

        Returns:
            Número de notificações removidas
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.expires_at.isnot(None),
                    Notification.expires_at < cutoff_date,
                )
            )
            .delete()
        )

        self.db.commit()

        logger.info(f"Cleaned up {count} expired notifications older than {days_to_keep} days")
        return count

    # ===== Métodos de Criação de Notificações Específicas =====

    def notify_review_overdue(
        self, user_id: UUID, plan: InterventionPlan, days_overdue: int
    ) -> Notification:
        """Cria notificação de revisão atrasada."""
        return self.create_notification(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.REVIEW_OVERDUE,
                priority=NotificationPriority.HIGH,
                title=f"Revisão Atrasada: {days_overdue} dias",
                message=f"O plano de intervenção do aluno requer revisão urgente. "
                f"Está {days_overdue} dias atrasado.",
                intervention_plan_id=plan.id,
                action_url=f"/intervention-plans/{plan.id}",
                expires_at=datetime.utcnow() + timedelta(days=7),
            )
        )

    def notify_review_due_soon(
        self, user_id: UUID, plan: InterventionPlan, days_until_due: int
    ) -> Notification:
        """Cria notificação de revisão próxima."""
        return self.create_notification(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.REVIEW_DUE_SOON,
                priority=NotificationPriority.MEDIUM,
                title=f"Revisão em {days_until_due} dias",
                message=f"O plano de intervenção do aluno deve ser revisado em breve.",
                intervention_plan_id=plan.id,
                action_url=f"/intervention-plans/{plan.id}",
                expires_at=datetime.utcnow() + timedelta(days=7),
            )
        )

    def notify_high_priority_plan(self, user_id: UUID, plan: InterventionPlan) -> Notification:
        """Cria notificação de plano de alta prioridade."""
        return self.create_notification(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.HIGH_PRIORITY,
                priority=NotificationPriority.URGENT,
                title="Plano de Alta Prioridade",
                message="Um plano de intervenção requer atenção imediata.",
                intervention_plan_id=plan.id,
                action_url=f"/intervention-plans/{plan.id}",
                expires_at=datetime.utcnow() + timedelta(days=3),
            )
        )
