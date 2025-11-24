"""
Testes Unitários - Notification Service
========================================

Testa funcionalidades do serviço de notificações.

Autor: Claude Code
Data: 2025-11-24
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.notification import Notification, NotificationPriority, NotificationType
from app.models.intervention_plan import InterventionPlan, PlanStatus, ReviewFrequency
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService


@pytest.fixture(scope="function")
def db_session():
    """Cria sessão de banco de dados em memória para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def notification_service(db_session):
    """Fixture do serviço de notificações."""
    return NotificationService(db_session)


@pytest.fixture
def sample_user_id():
    """UUID de usuário para testes."""
    return uuid4()


@pytest.fixture
def sample_plan_id():
    """UUID de plano para testes."""
    return uuid4()


class TestNotificationServiceCreate:
    """Testes de criação de notificações."""

    def test_create_notification_success(self, notification_service, sample_user_id, sample_plan_id):
        """Testa criação bem-sucedida de notificação."""
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.REVIEW_OVERDUE,
            priority=NotificationPriority.HIGH,
            title="Test Notification",
            message="This is a test message",
            intervention_plan_id=sample_plan_id,
            action_url="/test/url",
        )

        notification = notification_service.create_notification(notification_data)

        assert notification.id is not None
        assert notification.user_id == sample_user_id
        assert notification.type == NotificationType.REVIEW_OVERDUE
        assert notification.priority == NotificationPriority.HIGH
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test message"
        assert notification.intervention_plan_id == sample_plan_id
        assert notification.action_url == "/test/url"
        assert notification.is_read is False
        assert notification.read_at is None

    def test_create_notification_without_plan(self, notification_service, sample_user_id):
        """Testa criação de notificação sem plano associado."""
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="System Message",
            message="System notification",
        )

        notification = notification_service.create_notification(notification_data)

        assert notification.intervention_plan_id is None
        assert notification.action_url is None

    def test_create_notification_with_expiration(self, notification_service, sample_user_id):
        """Testa criação de notificação com data de expiração."""
        expires_at = datetime.utcnow() + timedelta(days=7)

        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.REVIEW_DUE_SOON,
            priority=NotificationPriority.MEDIUM,
            title="Expiring Notification",
            message="This will expire",
            expires_at=expires_at,
        )

        notification = notification_service.create_notification(notification_data)

        assert notification.expires_at is not None
        assert (notification.expires_at - expires_at).total_seconds() < 1


class TestNotificationServiceList:
    """Testes de listagem de notificações."""

    @pytest.fixture(autouse=True)
    def setup_notifications(self, notification_service, sample_user_id):
        """Cria notificações de teste."""
        # Criar 5 notificações de teste
        for i in range(5):
            is_read = i < 2  # Primeiras 2 lidas, outras 3 não lidas
            priority = NotificationPriority.HIGH if i < 2 else NotificationPriority.MEDIUM

            notification_data = NotificationCreate(
                user_id=sample_user_id,
                type=NotificationType.REVIEW_OVERDUE,
                priority=priority,
                title=f"Notification {i}",
                message=f"Message {i}",
            )

            notification = notification_service.create_notification(notification_data)

            if is_read:
                notification.mark_as_read()
                notification_service.db.commit()

    def test_list_all_notifications(self, notification_service, sample_user_id):
        """Testa listagem de todas as notificações."""
        notifications, total = notification_service.get_user_notifications(sample_user_id)

        assert total == 5
        assert len(notifications) == 5

    def test_list_unread_only(self, notification_service, sample_user_id):
        """Testa listagem apenas de não lidas."""
        notifications, total = notification_service.get_user_notifications(
            sample_user_id, unread_only=True
        )

        assert total == 3
        assert len(notifications) == 3
        assert all(not n.is_read for n in notifications)

    def test_list_with_pagination(self, notification_service, sample_user_id):
        """Testa listagem com paginação."""
        # Primeira página
        page1, total1 = notification_service.get_user_notifications(
            sample_user_id, skip=0, limit=2
        )

        assert total1 == 5
        assert len(page1) == 2

        # Segunda página
        page2, total2 = notification_service.get_user_notifications(
            sample_user_id, skip=2, limit=2
        )

        assert total2 == 5
        assert len(page2) == 2

        # IDs diferentes
        assert page1[0].id != page2[0].id

    def test_list_filter_by_type(self, notification_service, sample_user_id):
        """Testa filtro por tipo."""
        # Criar notificação de tipo diferente
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.HIGH_PRIORITY,
            priority=NotificationPriority.URGENT,
            title="High Priority",
            message="Urgent notification",
        )
        notification_service.create_notification(notification_data)

        # Buscar apenas HIGH_PRIORITY
        notifications, total = notification_service.get_user_notifications(
            sample_user_id, type_filter=NotificationType.HIGH_PRIORITY
        )

        assert total == 1
        assert notifications[0].type == NotificationType.HIGH_PRIORITY

    def test_list_filter_by_priority(self, notification_service, sample_user_id):
        """Testa filtro por prioridade."""
        notifications, total = notification_service.get_user_notifications(
            sample_user_id, priority_filter=NotificationPriority.HIGH
        )

        assert total == 2
        assert all(n.priority == NotificationPriority.HIGH for n in notifications)

    def test_list_excludes_expired(self, notification_service, sample_user_id):
        """Testa que notificações expiradas são excluídas."""
        # Criar notificação expirada
        expired_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Expired",
            message="Expired notification",
            expires_at=datetime.utcnow() - timedelta(days=1),  # Expirada ontem
        )
        notification_service.create_notification(expired_data)

        # Listar notificações
        notifications, total = notification_service.get_user_notifications(sample_user_id)

        # Notificação expirada não deve aparecer
        assert total == 5  # Apenas as 5 originais
        assert all(not n.is_expired for n in notifications)


class TestNotificationServiceMarkAsRead:
    """Testes de marcar como lida."""

    def test_mark_as_read_success(self, notification_service, sample_user_id):
        """Testa marcação bem-sucedida como lida."""
        # Criar notificação
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.REVIEW_DUE_SOON,
            priority=NotificationPriority.MEDIUM,
            title="Test",
            message="Test message",
        )
        notification = notification_service.create_notification(notification_data)

        assert notification.is_read is False

        # Marcar como lida
        updated = notification_service.mark_as_read(notification.id, sample_user_id)

        assert updated is not None
        assert updated.is_read is True
        assert updated.read_at is not None

    def test_mark_as_read_unauthorized(self, notification_service, sample_user_id):
        """Testa que não pode marcar notificação de outro usuário."""
        # Criar notificação
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Test",
            message="Test",
        )
        notification = notification_service.create_notification(notification_data)

        # Tentar marcar com outro user_id
        other_user_id = uuid4()
        result = notification_service.mark_as_read(notification.id, other_user_id)

        assert result is None

    def test_mark_as_read_nonexistent(self, notification_service, sample_user_id):
        """Testa marcar notificação inexistente."""
        fake_id = uuid4()

        result = notification_service.mark_as_read(fake_id, sample_user_id)

        assert result is None

    def test_mark_all_as_read(self, notification_service, sample_user_id):
        """Testa marcar todas como lidas."""
        # Criar 3 notificações não lidas
        for i in range(3):
            notification_data = NotificationCreate(
                user_id=sample_user_id,
                type=NotificationType.REVIEW_OVERDUE,
                priority=NotificationPriority.HIGH,
                title=f"Notification {i}",
                message=f"Message {i}",
            )
            notification_service.create_notification(notification_data)

        # Marcar todas como lidas
        count = notification_service.mark_all_as_read(sample_user_id)

        assert count == 3

        # Verificar que todas foram marcadas
        notifications, _ = notification_service.get_user_notifications(sample_user_id)
        assert all(n.is_read for n in notifications)


class TestNotificationServiceDelete:
    """Testes de exclusão de notificações."""

    def test_delete_notification_success(self, notification_service, sample_user_id):
        """Testa exclusão bem-sucedida."""
        # Criar notificação
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="To Delete",
            message="Will be deleted",
        )
        notification = notification_service.create_notification(notification_data)

        # Deletar
        result = notification_service.delete_notification(notification.id, sample_user_id)

        assert result is True

        # Verificar que foi deletada
        notifications, total = notification_service.get_user_notifications(sample_user_id)
        assert total == 0

    def test_delete_notification_unauthorized(self, notification_service, sample_user_id):
        """Testa que não pode deletar notificação de outro usuário."""
        # Criar notificação
        notification_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Test",
            message="Test",
        )
        notification = notification_service.create_notification(notification_data)

        # Tentar deletar com outro user_id
        other_user_id = uuid4()
        result = notification_service.delete_notification(notification.id, other_user_id)

        assert result is False


class TestNotificationServiceStats:
    """Testes de estatísticas."""

    @pytest.fixture(autouse=True)
    def setup_mixed_notifications(self, notification_service, sample_user_id):
        """Cria mix de notificações para testes."""
        notifications_data = [
            (NotificationType.REVIEW_OVERDUE, NotificationPriority.URGENT, False),
            (NotificationType.REVIEW_OVERDUE, NotificationPriority.HIGH, False),
            (NotificationType.REVIEW_DUE_SOON, NotificationPriority.MEDIUM, False),
            (NotificationType.HIGH_PRIORITY, NotificationPriority.URGENT, False),
            (NotificationType.PLAN_CREATED, NotificationPriority.LOW, True),
        ]

        for type_, priority, is_read in notifications_data:
            notification_data = NotificationCreate(
                user_id=sample_user_id,
                type=type_,
                priority=priority,
                title="Test",
                message="Test message",
            )
            notification = notification_service.create_notification(notification_data)

            if is_read:
                notification.mark_as_read()
                notification_service.db.commit()

    def test_get_unread_count(self, notification_service, sample_user_id):
        """Testa contagem de não lidas."""
        count = notification_service.get_unread_count(sample_user_id)

        assert count == 4  # 5 total - 1 lida

    def test_get_notification_stats(self, notification_service, sample_user_id):
        """Testa obtenção de estatísticas."""
        stats = notification_service.get_notification_stats(sample_user_id)

        assert stats.total == 5
        assert stats.unread == 4
        assert stats.urgent_count == 2

        # Verificar contagens por tipo
        assert "review_overdue" in stats.by_type
        assert stats.by_type["review_overdue"] == 2

        # Verificar contagens por prioridade
        assert "urgent" in stats.by_priority
        assert stats.by_priority["urgent"] == 2


class TestNotificationServiceHelpers:
    """Testes de métodos helper."""

    def test_notify_review_overdue(self, notification_service, sample_user_id):
        """Testa criação de notificação de revisão atrasada."""
        # Criar mock de plano
        plan = MagicMock()
        plan.id = uuid4()

        notification = notification_service.notify_review_overdue(
            user_id=sample_user_id, plan=plan, days_overdue=5
        )

        assert notification.type == NotificationType.REVIEW_OVERDUE
        assert notification.priority == NotificationPriority.HIGH
        assert "5 dias" in notification.title
        assert notification.intervention_plan_id == plan.id

    def test_notify_review_due_soon(self, notification_service, sample_user_id):
        """Testa criação de notificação de revisão próxima."""
        plan = MagicMock()
        plan.id = uuid4()

        notification = notification_service.notify_review_due_soon(
            user_id=sample_user_id, plan=plan, days_until_due=3
        )

        assert notification.type == NotificationType.REVIEW_DUE_SOON
        assert notification.priority == NotificationPriority.MEDIUM
        assert "3 dias" in notification.title

    def test_notify_high_priority_plan(self, notification_service, sample_user_id):
        """Testa criação de notificação de alta prioridade."""
        plan = MagicMock()
        plan.id = uuid4()

        notification = notification_service.notify_high_priority_plan(
            user_id=sample_user_id, plan=plan
        )

        assert notification.type == NotificationType.HIGH_PRIORITY
        assert notification.priority == NotificationPriority.URGENT


class TestNotificationServiceCleanup:
    """Testes de limpeza."""

    def test_cleanup_expired_notifications(self, notification_service, sample_user_id):
        """Testa limpeza de notificações expiradas antigas."""
        # Criar notificação expirada há 40 dias
        old_expired_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Old Expired",
            message="Very old",
            expires_at=datetime.utcnow() - timedelta(days=40),
        )
        notification_service.create_notification(old_expired_data)

        # Criar notificação expirada há 10 dias
        recent_expired_data = NotificationCreate(
            user_id=sample_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Recent Expired",
            message="Recently expired",
            expires_at=datetime.utcnow() - timedelta(days=10),
        )
        notification_service.create_notification(recent_expired_data)

        # Limpar notificações expiradas há mais de 30 dias
        count = notification_service.cleanup_expired_notifications(days_to_keep=30)

        assert count == 1  # Apenas a expirada há 40 dias
