"""
Testes de Integração - API de Notificações
===========================================

Testa endpoints REST de notificações.

Autor: Claude Code
Data: 2025-11-24
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import status

from app.models.notification import NotificationType, NotificationPriority


class TestNotificationsAPI:
    """Testes dos endpoints de notificações."""

    @pytest.fixture(autouse=True)
    def setup_notifications(self, client, auth_headers, db_session):
        """Cria notificações de teste."""
        from app.services.notification_service import NotificationService
        from app.schemas.notification import NotificationCreate

        service = NotificationService(db_session)
        user_id = uuid4()  # Mock user ID

        # Criar 5 notificações de teste
        for i in range(5):
            is_urgent = i < 2

            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationType.REVIEW_OVERDUE if is_urgent else NotificationType.REVIEW_DUE_SOON,
                priority=NotificationPriority.URGENT if is_urgent else NotificationPriority.MEDIUM,
                title=f"Notification {i}",
                message=f"Test message {i}",
            )

            service.create_notification(notification_data)

    def test_list_notifications_success(self, client, auth_headers):
        """Testa listagem de notificações."""
        response = client.get("/api/v1/notifications", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "unread_count" in data
        assert "has_more" in data

    def test_list_notifications_pagination(self, client, auth_headers):
        """Testa paginação."""
        # Primeira página
        response1 = client.get(
            "/api/v1/notifications?skip=0&limit=2",
            headers=auth_headers
        )

        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["items"]) <= 2

        # Segunda página
        response2 = client.get(
            "/api/v1/notifications?skip=2&limit=2",
            headers=auth_headers
        )

        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()

        # IDs devem ser diferentes
        if data1["items"] and data2["items"]:
            assert data1["items"][0]["id"] != data2["items"][0]["id"]

    def test_list_notifications_filter_unread(self, client, auth_headers):
        """Testa filtro de não lidas."""
        response = client.get(
            "/api/v1/notifications?unread_only=true",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Todas devem ser não lidas
        assert all(not item["is_read"] for item in data["items"])

    def test_list_notifications_filter_by_type(self, client, auth_headers):
        """Testa filtro por tipo."""
        response = client.get(
            f"/api/v1/notifications?type={NotificationType.REVIEW_OVERDUE.value}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Todas devem ser do tipo especificado
        assert all(
            item["type"] == NotificationType.REVIEW_OVERDUE.value
            for item in data["items"]
        )

    def test_list_notifications_filter_by_priority(self, client, auth_headers):
        """Testa filtro por prioridade."""
        response = client.get(
            f"/api/v1/notifications?priority={NotificationPriority.URGENT.value}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Todas devem ter a prioridade especificada
        assert all(
            item["priority"] == NotificationPriority.URGENT.value
            for item in data["items"]
        )

    def test_list_notifications_unauthorized(self, client):
        """Testa que requer autenticação."""
        response = client.get("/api/v1/notifications")

        # HTTPBearer returns 403 when no credentials are provided
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_unread_count_success(self, client, auth_headers):
        """Testa contagem de não lidas."""
        response = client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)
        assert data["unread_count"] >= 0

    def test_get_notification_stats_success(self, client, auth_headers):
        """Testa obtenção de estatísticas."""
        response = client.get(
            "/api/v1/notifications/stats",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "total" in data
        assert "unread" in data
        assert "by_type" in data
        assert "by_priority" in data
        assert "urgent_count" in data

    def test_mark_as_read_success(self, client, auth_headers, db_session, test_user):
        """Testa marcar notificação como lida."""
        from app.services.notification_service import NotificationService
        from app.schemas.notification import NotificationCreate

        # Criar notificação
        service = NotificationService(db_session)
        notification = service.create_notification(
            NotificationCreate(
                user_id=test_user.id,
                type=NotificationType.SYSTEM,
                priority=NotificationPriority.LOW,
                title="Test",
                message="Test message",
            )
        )

        # Marcar como lida
        response = client.patch(
            f"/api/v1/notifications/{notification.id}",
            headers=auth_headers,
            json={"is_read": True}
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_read"] is True
        assert data["read_at"] is not None

    def test_mark_as_read_not_found(self, client, auth_headers):
        """Testa marcar notificação inexistente."""
        fake_id = uuid4()

        response = client.patch(
            f"/api/v1/notifications/{fake_id}",
            headers=auth_headers,
            json={"is_read": True}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_all_as_read_success(self, client, auth_headers):
        """Testa marcar todas como lidas."""
        response = client.post(
            "/api/v1/notifications/mark-all-read",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "updated_count" in data
        assert "message" in data
        assert isinstance(data["updated_count"], int)

    def test_delete_notification_success(self, client, auth_headers, db_session, test_user):
        """Testa exclusão de notificação."""
        from app.services.notification_service import NotificationService
        from app.schemas.notification import NotificationCreate

        # Criar notificação
        service = NotificationService(db_session)
        notification = service.create_notification(
            NotificationCreate(
                user_id=test_user.id,
                type=NotificationType.SYSTEM,
                priority=NotificationPriority.LOW,
                title="To Delete",
                message="Will be deleted",
            )
        )

        # Deletar
        response = client.delete(
            f"/api/v1/notifications/{notification.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_notification_not_found(self, client, auth_headers):
        """Testa exclusão de notificação inexistente."""
        fake_id = uuid4()

        response = client.delete(
            f"/api/v1/notifications/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestNotificationsAPIValidation:
    """Testes de validação da API."""

    def test_list_notifications_invalid_skip(self, client, auth_headers):
        """Testa skip inválido."""
        response = client.get(
            "/api/v1/notifications?skip=-1",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_notifications_invalid_limit(self, client, auth_headers):
        """Testa limit inválido."""
        response = client.get(
            "/api/v1/notifications?limit=0",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_notifications_limit_too_high(self, client, auth_headers):
        """Testa limit muito alto."""
        response = client.get(
            "/api/v1/notifications?limit=200",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_mark_as_read_invalid_uuid(self, client, auth_headers):
        """Testa UUID inválido."""
        response = client.patch(
            "/api/v1/notifications/invalid-uuid",
            headers=auth_headers,
            json={"is_read": True}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_mark_as_read_empty_body(self, client, auth_headers):
        """Testa body vazio."""
        notification_id = uuid4()

        response = client.patch(
            f"/api/v1/notifications/{notification_id}",
            headers=auth_headers,
            json={}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestNotificationsAPIResponse:
    """Testes de estrutura de resposta."""

    def test_notification_response_structure(self, client, auth_headers, db_session):
        """Testa estrutura de resposta de notificação."""
        from app.services.notification_service import NotificationService
        from app.schemas.notification import NotificationCreate

        # Criar notificação
        service = NotificationService(db_session)
        notification = service.create_notification(
            NotificationCreate(
                user_id=uuid4(),
                type=NotificationType.REVIEW_OVERDUE,
                priority=NotificationPriority.HIGH,
                title="Test Notification",
                message="Test message",
                action_url="/test/url",
            )
        )

        # Buscar notificação
        response = client.get("/api/v1/notifications", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        if data["items"]:
            item = data["items"][0]

            # Verificar campos obrigatórios
            assert "id" in item
            assert "type" in item
            assert "priority" in item
            assert "title" in item
            assert "message" in item
            assert "is_read" in item
            assert "created_at" in item

            # Verificar tipos
            assert isinstance(item["id"], str)
            assert isinstance(item["is_read"], bool)

    def test_list_response_structure(self, client, auth_headers):
        """Testa estrutura de resposta de listagem."""
        response = client.get("/api/v1/notifications", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verificar campos obrigatórios
        required_fields = ["items", "total", "unread_count", "has_more"]
        for field in required_fields:
            assert field in data

        # Verificar tipos
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["unread_count"], int)
        assert isinstance(data["has_more"], bool)

    def test_stats_response_structure(self, client, auth_headers):
        """Testa estrutura de resposta de estatísticas."""
        response = client.get("/api/v1/notifications/stats", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verificar campos
        required_fields = ["total", "unread", "by_type", "by_priority", "urgent_count"]
        for field in required_fields:
            assert field in data

        # Verificar tipos
        assert isinstance(data["total"], int)
        assert isinstance(data["unread"], int)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_priority"], dict)
        assert isinstance(data["urgent_count"], int)
