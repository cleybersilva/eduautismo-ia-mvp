#!/usr/bin/env python3
"""
EduAutismo IA - Seed Notifications
==================================

Script para popular banco de dados com notificações de teste.

Cria exemplos de todos os tipos e prioridades de notificações
para facilitar desenvolvimento e testes.

Uso: python scripts/seed_notifications.py [--count N]

Autor: Claude Code
Data: 2025-11-24
"""

import argparse
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.database import get_db
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

# Cores para output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_info(message: str):
    """Imprime mensagem informativa."""
    print(f"{BLUE}[INFO]{RESET} {message}")


def print_success(message: str):
    """Imprime mensagem de sucesso."""
    print(f"{GREEN}[SUCCESS]{RESET} {message}")


def print_warning(message: str):
    """Imprime mensagem de aviso."""
    print(f"{YELLOW}[WARNING]{RESET} {message}")


def create_sample_notifications(count: int = 20) -> int:
    """
    Cria notificações de exemplo.

    Args:
        count: Número de notificações a criar

    Returns:
        Número de notificações criadas
    """
    db = next(get_db())
    service = NotificationService(db)

    # IDs de usuários de teste (você pode ajustar estes)
    test_user_ids = [uuid4() for _ in range(3)]

    # Templates de notificações por tipo
    templates = {
        NotificationType.REVIEW_OVERDUE: {
            "title": "Revisão de Plano Atrasada",
            "message": "O plano de intervenção está {days} dias atrasado para revisão.",
            "priority": NotificationPriority.URGENT,
        },
        NotificationType.REVIEW_DUE_SOON: {
            "title": "Revisão de Plano em Breve",
            "message": "O plano de intervenção precisa de revisão em {days} dias.",
            "priority": NotificationPriority.HIGH,
        },
        NotificationType.PLAN_CREATED: {
            "title": "Novo Plano de Intervenção",
            "message": "Um novo plano de intervenção foi criado para o aluno.",
            "priority": NotificationPriority.MEDIUM,
        },
        NotificationType.PLAN_UPDATED: {
            "title": "Plano de Intervenção Atualizado",
            "message": "O plano de intervenção foi atualizado recentemente.",
            "priority": NotificationPriority.MEDIUM,
        },
        NotificationType.PLAN_REVIEWED: {
            "title": "Plano Revisado",
            "message": "O plano de intervenção foi revisado com sucesso.",
            "priority": NotificationPriority.LOW,
        },
        NotificationType.HIGH_PRIORITY: {
            "title": "Ação Urgente Necessária",
            "message": "Um plano de alta prioridade requer sua atenção imediata.",
            "priority": NotificationPriority.URGENT,
        },
        NotificationType.SYSTEM: {
            "title": "Notificação do Sistema",
            "message": "Atualização importante do sistema EduAutismo IA.",
            "priority": NotificationPriority.LOW,
        },
    }

    created = 0

    print_info(f"Criando {count} notificações de exemplo...")

    for i in range(count):
        # Selecionar tipo de notificação (ciclando através dos tipos)
        notification_types = list(NotificationType)
        notification_type = notification_types[i % len(notification_types)]

        # Selecionar usuário (ciclando através dos usuários de teste)
        user_id = test_user_ids[i % len(test_user_ids)]

        # Obter template
        template = templates[notification_type]

        # Personalizar mensagem
        days = (i % 10) + 1
        message = template["message"].format(days=days)

        # Criar notificação
        notification_data = NotificationCreate(
            user_id=user_id,
            type=notification_type,
            priority=template["priority"],
            title=template["title"],
            message=message,
            action_url=f"/intervention-plans/{uuid4()}" if i % 3 == 0 else None,
        )

        notification = service.create_notification(notification_data)

        # Marcar algumas como lidas
        if i % 4 == 0:
            service.mark_as_read(notification.id, user_id)

        # Definir expiração para algumas
        if i % 5 == 0:
            notification.expires_at = datetime.utcnow() + timedelta(days=7)
            db.commit()

        created += 1

        if (i + 1) % 5 == 0:
            print_info(f"Criadas {i + 1}/{count} notificações...")

    db.close()

    return created


def create_notification_examples():
    """
    Cria exemplos específicos de cada tipo de notificação.

    Para documentação e demonstração.
    """
    db = next(get_db())
    service = NotificationService(db)

    demo_user_id = uuid4()

    examples = [
        # Exemplo: Revisão urgente atrasada
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.REVIEW_OVERDUE,
            priority=NotificationPriority.URGENT,
            title="⚠️ Revisão Crítica Atrasada",
            message="O plano de intervenção do aluno João Silva está 15 dias atrasado. "
            "Revisão imediata necessária para manter a qualidade do atendimento.",
            action_url="/intervention-plans/urgent-review",
        ),
        # Exemplo: Revisão próxima
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.REVIEW_DUE_SOON,
            priority=NotificationPriority.HIGH,
            title="📅 Revisão Programada em Breve",
            message="O plano de intervenção da aluna Maria Santos precisa de revisão "
            "nos próximos 3 dias. Por favor, agende a avaliação.",
            action_url="/intervention-plans/upcoming-reviews",
        ),
        # Exemplo: Novo plano criado
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.PLAN_CREATED,
            priority=NotificationPriority.MEDIUM,
            title="✨ Novo Plano Disponível",
            message="Um novo plano de intervenção foi criado para o aluno Pedro Costa. "
            "Revise as estratégias e objetivos propostos.",
            action_url="/intervention-plans/new",
        ),
        # Exemplo: Plano atualizado
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.PLAN_UPDATED,
            priority=NotificationPriority.MEDIUM,
            title="📝 Plano Atualizado",
            message="O plano de intervenção foi atualizado com novas estratégias "
            "baseadas nos resultados recentes das avaliações.",
        ),
        # Exemplo: Plano revisado
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.PLAN_REVIEWED,
            priority=NotificationPriority.LOW,
            title="✅ Revisão Concluída",
            message="A revisão do plano de intervenção foi concluída com sucesso. "
            "Todas as metas foram atualizadas.",
        ),
        # Exemplo: Alta prioridade
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.HIGH_PRIORITY,
            priority=NotificationPriority.URGENT,
            title="🚨 Atenção Imediata Requerida",
            message="Um plano de alta prioridade identificou necessidade de intervenção "
            "urgente. Por favor, revise imediatamente.",
            action_url="/intervention-plans/high-priority",
        ),
        # Exemplo: Sistema
        NotificationCreate(
            user_id=demo_user_id,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="ℹ️ Atualização do Sistema",
            message="O sistema EduAutismo IA foi atualizado com novas funcionalidades de "
            "notificações e exportação de dados.",
        ),
    ]

    print_info("Criando notificações de exemplo detalhadas...")

    for notification_data in examples:
        service.create_notification(notification_data)

    db.close()

    return len(examples)


def main():
    """Executa seed de notificações."""
    parser = argparse.ArgumentParser(
        description="Seed notifications for EduAutismo IA"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of random notifications to create (default: 20)",
    )
    parser.add_argument(
        "--examples-only",
        action="store_true",
        help="Only create detailed examples (7 notifications)",
    )

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("  EduAutismo IA - Seed Notifications")
    print("=" * 70)
    print()

    try:
        if args.examples_only:
            count = create_notification_examples()
            print_success(f"Criadas {count} notificações de exemplo")
        else:
            # Criar exemplos detalhados
            examples_count = create_notification_examples()
            print_success(f"Criadas {examples_count} notificações de exemplo")

            # Criar notificações aleatórias
            random_count = create_sample_notifications(args.count)
            print_success(f"Criadas {random_count} notificações aleatórias")

            total = examples_count + random_count
            print()
            print_success(f"Total: {total} notificações criadas!")

        print()
        print("✅ Seed concluído com sucesso!")
        print()
        print("Você pode visualizar as notificações em:")
        print("  - http://localhost:8000/docs")
        print("  - GET /api/v1/notifications")
        print()

    except Exception as e:
        print()
        print(f"{YELLOW}[ERROR]{RESET} Erro ao criar notificações: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
