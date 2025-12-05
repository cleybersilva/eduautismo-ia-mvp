"""
Background Tasks - EduAutismo IA
================================

Sistema de tarefas em background para:
- Criar notificações automáticas
- Limpar notificações expiradas
- Verificar planos pendentes de revisão
- Invalidar caches expirados

Autor: Claude Code
Data: 2025-11-24
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.core.database import get_db
from app.models.intervention_plan import InterventionPlan, ReviewFrequency
from app.models.notification import NotificationType, NotificationPriority
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


# =============================================================================
# Background Task Functions
# =============================================================================


async def check_and_notify_overdue_reviews(db: Session) -> int:
    """
    Verifica planos com revisão atrasada e cria notificações.

    Args:
        db: Database session

    Returns:
        Número de notificações criadas
    """
    logger.info("Checking for overdue intervention plan reviews...")

    notification_service = NotificationService(db)
    notifications_created = 0

    try:
        # Buscar planos que precisam revisão
        now = datetime.utcnow()

        overdue_plans = (
            db.query(InterventionPlan)
            .filter(
                InterventionPlan.needs_review == True,
                InterventionPlan.last_reviewed_at.isnot(None),
            )
            .all()
        )

        for plan in overdue_plans:
            # Calcular dias desde última revisão
            days_since_review = (now - plan.last_reviewed_at).days

            # Obter frequência de revisão
            frequency_days = {
                ReviewFrequency.WEEKLY: 7,
                ReviewFrequency.BIWEEKLY: 14,
                ReviewFrequency.MONTHLY: 30,
                ReviewFrequency.QUARTERLY: 90,
            }.get(plan.review_frequency, 30)

            # Se está atrasado
            if days_since_review > frequency_days:
                days_overdue = days_since_review - frequency_days

                # Verificar se já existe notificação recente para este plano
                existing = (
                    db.query(
                        db.query(
                            db.query(
                                db.query(NotificationService).exists()
                            ).filter_by(
                                intervention_plan_id=plan.id,
                                type=NotificationType.REVIEW_OVERDUE,
                                created_at
                                >= now
                                - timedelta(days=1),  # Última 24h
                            )
                        )
                    )
                    .scalar()
                )

                if not existing:
                    # Criar notificação
                    notification_service.notify_review_overdue(
                        user_id=plan.professional_id,
                        plan=plan,
                        days_overdue=days_overdue,
                    )

                    notifications_created += 1
                    logger.info(
                        f"Created overdue notification for plan {plan.id} "
                        f"({days_overdue} days overdue)"
                    )

        logger.info(f"Created {notifications_created} overdue review notifications")
        return notifications_created

    except Exception as e:
        logger.error(f"Error checking overdue reviews: {e}")
        return notifications_created


async def check_and_notify_upcoming_reviews(db: Session, days_ahead: int = 3) -> int:
    """
    Verifica planos com revisão próxima e cria notificações.

    Args:
        db: Database session
        days_ahead: Quantos dias de antecedência notificar

    Returns:
        Número de notificações criadas
    """
    logger.info(f"Checking for reviews due in next {days_ahead} days...")

    notification_service = NotificationService(db)
    notifications_created = 0

    try:
        now = datetime.utcnow()

        # Buscar planos que precisarão revisão em breve
        upcoming_plans = (
            db.query(InterventionPlan)
            .filter(
                InterventionPlan.needs_review == False,
                InterventionPlan.last_reviewed_at.isnot(None),
            )
            .all()
        )

        for plan in upcoming_plans:
            # Calcular próxima data de revisão
            frequency_days = {
                ReviewFrequency.WEEKLY: 7,
                ReviewFrequency.BIWEEKLY: 14,
                ReviewFrequency.MONTHLY: 30,
                ReviewFrequency.QUARTERLY: 90,
            }.get(plan.review_frequency, 30)

            next_review_date = plan.last_reviewed_at + timedelta(days=frequency_days)
            days_until_review = (next_review_date - now).days

            # Se está próximo
            if 0 < days_until_review <= days_ahead:
                # Verificar se já existe notificação
                existing = (
                    db.query(NotificationService)
                    .filter_by(
                        intervention_plan_id=plan.id,
                        type=NotificationType.REVIEW_DUE_SOON,
                        created_at >= now - timedelta(days=2),
                    )
                    .first()
                )

                if not existing:
                    # Criar notificação
                    notification_service.notify_review_due_soon(
                        user_id=plan.professional_id,
                        plan=plan,
                        days_until_review=days_until_review,
                    )

                    notifications_created += 1
                    logger.info(
                        f"Created upcoming review notification for plan {plan.id} "
                        f"({days_until_review} days until review)"
                    )

        logger.info(f"Created {notifications_created} upcoming review notifications")
        return notifications_created

    except Exception as e:
        logger.error(f"Error checking upcoming reviews: {e}")
        return notifications_created


async def cleanup_expired_notifications(db: Session) -> int:
    """
    Remove notificações expiradas do banco de dados.

    Args:
        db: Database session

    Returns:
        Número de notificações removidas
    """
    logger.info("Cleaning up expired notifications...")

    notification_service = NotificationService(db)

    try:
        deleted_count = notification_service.cleanup_expired_notifications()
        logger.info(f"Deleted {deleted_count} expired notifications")
        return deleted_count

    except Exception as e:
        logger.error(f"Error cleaning up notifications: {e}")
        return 0


async def invalidate_expired_cache() -> int:
    """
    Invalida entradas expiradas do cache.

    Returns:
        Número de chaves invalidadas
    """
    logger.info("Invalidating expired cache entries...")

    try:
        # O Redis já lida com expiração automaticamente via TTL
        # Mas podemos fazer uma limpeza manual de chaves específicas se necessário

        # Exemplo: invalidar caches de planos pendentes após 1 hora
        pattern = "intervention_plans:pending_review:*"
        invalidated = await cache_manager.invalidate_pattern(pattern)

        logger.info(f"Invalidated {invalidated} cache entries")
        return invalidated

    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return 0


async def run_periodic_tasks() -> dict:
    """
    Executa todas as tarefas periódicas.

    Returns:
        Dicionário com resultados de cada tarefa
    """
    logger.info("Running periodic background tasks...")

    results = {
        "overdue_notifications": 0,
        "upcoming_notifications": 0,
        "expired_notifications_cleaned": 0,
        "cache_entries_invalidated": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }

    db = next(get_db())

    try:
        # 1. Verificar revisões atrasadas
        results["overdue_notifications"] = await check_and_notify_overdue_reviews(db)

        # 2. Verificar revisões próximas
        results["upcoming_notifications"] = await check_and_notify_upcoming_reviews(
            db, days_ahead=3
        )

        # 3. Limpar notificações expiradas
        results["expired_notifications_cleaned"] = await cleanup_expired_notifications(
            db
        )

        # 4. Invalidar cache expirado
        results["cache_entries_invalidated"] = await invalidate_expired_cache()

        logger.info(f"Periodic tasks completed: {results}")

    except Exception as e:
        logger.error(f"Error in periodic tasks: {e}")

    finally:
        db.close()

    return results


# =============================================================================
# FastAPI Background Task Helpers
# =============================================================================


def notify_plan_created_background(plan_id: UUID, user_id: UUID):
    """
    Tarefa em background para notificar criação de plano.

    Uso com FastAPI:
        @router.post("/")
        async def create_plan(
            background_tasks: BackgroundTasks,
            ...
        ):
            plan = service.create(...)
            background_tasks.add_task(
                notify_plan_created_background,
                plan.id,
                current_user["sub"]
            )
    """
    db = next(get_db())

    try:
        notification_service = NotificationService(db)
        plan = db.query(InterventionPlan).filter_by(id=plan_id).first()

        if plan:
            notification_service.notify_plan_created(user_id, plan)
            logger.info(f"Background notification sent for plan creation: {plan_id}")

    except Exception as e:
        logger.error(f"Error in background notification: {e}")

    finally:
        db.close()


def notify_plan_updated_background(plan_id: UUID, user_id: UUID):
    """Tarefa em background para notificar atualização de plano."""
    db = next(get_db())

    try:
        notification_service = NotificationService(db)
        plan = db.query(InterventionPlan).filter_by(id=plan_id).first()

        if plan:
            notification_service.notify_plan_updated(user_id, plan)
            logger.info(f"Background notification sent for plan update: {plan_id}")

    except Exception as e:
        logger.error(f"Error in background notification: {e}")

    finally:
        db.close()


def notify_plan_reviewed_background(plan_id: UUID, user_id: UUID):
    """Tarefa em background para notificar revisão de plano."""
    db = next(get_db())

    try:
        notification_service = NotificationService(db)
        plan = db.query(InterventionPlan).filter_by(id=plan_id).first()

        if plan:
            notification_service.notify_plan_reviewed(user_id, plan)
            logger.info(f"Background notification sent for plan review: {plan_id}")

    except Exception as e:
        logger.error(f"Error in background notification: {e}")

    finally:
        db.close()


# =============================================================================
# Scheduler (Optional - requires APScheduler)
# =============================================================================


class BackgroundTaskScheduler:
    """
    Agendador de tarefas em background.

    Requer: pip install apscheduler

    Uso:
        scheduler = BackgroundTaskScheduler()
        await scheduler.start()
    """

    def __init__(self):
        self.scheduler = None
        self._running = False

    async def start(self):
        """Inicia o agendador de tarefas."""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler

            self.scheduler = AsyncIOScheduler()

            # Agendar tarefas periódicas
            # Verificar revisões atrasadas: a cada hora
            self.scheduler.add_job(
                run_periodic_tasks,
                "interval",
                hours=1,
                id="periodic_tasks",
                replace_existing=True,
            )

            # Limpar notificações expiradas: todo dia às 3h
            self.scheduler.add_job(
                cleanup_expired_notifications,
                "cron",
                hour=3,
                minute=0,
                id="cleanup_notifications",
                replace_existing=True,
            )

            self.scheduler.start()
            self._running = True

            logger.info("Background task scheduler started")

        except ImportError:
            logger.warning(
                "APScheduler not installed. "
                "Install with: pip install apscheduler"
            )

    async def stop(self):
        """Para o agendador de tarefas."""
        if self.scheduler and self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Background task scheduler stopped")

    @property
    def is_running(self) -> bool:
        """Verifica se o agendador está rodando."""
        return self._running


# Instância global do scheduler
background_scheduler = BackgroundTaskScheduler()
