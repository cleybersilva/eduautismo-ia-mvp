"""
Extensão do Serviço de Planos de Intervenção com Cache
=======================================================

Adiciona funcionalidades de cache Redis ao serviço de planos de intervenção
para melhorar performance de consultas frequentes.

Autor: Claude Code
Data: 2025-11-24
"""

import logging
from typing import Optional
from uuid import UUID

from app.core.cache import cache_manager
from app.services.intervention_plan_service import InterventionPlanService

logger = logging.getLogger(__name__)


class CachedInterventionPlanService(InterventionPlanService):
    """
    Extensão do serviço de planos de intervenção com cache Redis.

    Adiciona cache em métodos de leitura frequentes para reduzir carga no banco.
    """

    CACHE_PREFIX = "intervention_plans"
    PENDING_REVIEW_CACHE_TTL = 300  # 5 minutos

    async def get_pending_review_plans_cached(
        self,
        skip: int = 0,
        limit: int = 50,
        priority_filter: Optional[str] = None,
        professional_id: Optional[UUID] = None,
        use_cache: bool = True,
    ) -> dict:
        """
        Versão cacheada de get_pending_review_plans.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            priority_filter: Filtrar por prioridade (high/medium/low)
            professional_id: Filtrar por profissional envolvido
            use_cache: Se True, usa cache (default: True)

        Returns:
            Dict com items, total e contagens por prioridade
        """
        if not use_cache:
            return self.get_pending_review_plans(
                skip=skip,
                limit=limit,
                priority_filter=priority_filter,
                professional_id=professional_id,
            )

        # Gerar chave de cache baseada nos parâmetros
        cache_key = f"pending_review:{skip}:{limit}:{priority_filter}:{professional_id}"

        # Tentar obter do cache
        cached_result = await cache_manager.get(cache_key, prefix=self.CACHE_PREFIX)

        if cached_result is not None:
            logger.debug(
                f"Cache hit for pending review plans",
                extra={
                    "skip": skip,
                    "limit": limit,
                    "priority_filter": priority_filter,
                    "professional_id": str(professional_id) if professional_id else None,
                },
            )
            return cached_result

        # Cache miss - buscar do banco
        logger.debug(
            f"Cache miss for pending review plans",
            extra={
                "skip": skip,
                "limit": limit,
                "priority_filter": priority_filter,
                "professional_id": str(professional_id) if professional_id else None,
            },
        )

        result = self.get_pending_review_plans(
            skip=skip,
            limit=limit,
            priority_filter=priority_filter,
            professional_id=professional_id,
        )

        # Serializar result para cache (converter objetos SQLAlchemy)
        serializable_result = self._serialize_pending_review_result(result)

        # Armazenar no cache
        await cache_manager.set(
            cache_key,
            serializable_result,
            ttl=self.PENDING_REVIEW_CACHE_TTL,
            prefix=self.CACHE_PREFIX,
        )

        return result

    def _serialize_pending_review_result(self, result: dict) -> dict:
        """
        Serializa resultado de pending_review para cache.

        Converte objetos SQLAlchemy para dicionários serializáveis.
        """
        serialized_items = []

        for item in result["items"]:
            plan = item["plan"]
            student = item["student"]

            serialized_item = {
                "plan": {
                    "id": str(plan.id),
                    "title": plan.title,
                    "description": plan.description,
                    "status": plan.status.value if hasattr(plan.status, "value") else plan.status,
                    "review_frequency": (
                        plan.review_frequency.value
                        if hasattr(plan.review_frequency, "value")
                        else plan.review_frequency
                    ),
                    "needs_review": plan.needs_review,
                    "last_reviewed_at": (
                        plan.last_reviewed_at.isoformat() if plan.last_reviewed_at else None
                    ),
                    "created_at": plan.created_at.isoformat() if plan.created_at else None,
                    "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
                    "student_id": str(plan.student_id),
                },
                "student": {
                    "id": str(student.id),
                    "name": student.name if hasattr(student, "name") else None,
                    "age": student.age if hasattr(student, "age") else None,
                },
                "days_since_review": item["days_since_review"],
                "priority": item["priority"],
            }

            serialized_items.append(serialized_item)

        return {
            "items": serialized_items,
            "total": result["total"],
            "high_priority": result["high_priority"],
            "medium_priority": result["medium_priority"],
            "low_priority": result["low_priority"],
        }

    async def invalidate_pending_review_cache(self):
        """
        Invalida todo cache de pending_review.

        Deve ser chamado quando:
        - Um plano é criado
        - Um plano é atualizado
        - Um plano é revisado
        - Status de plano é alterado
        """
        count = await cache_manager.delete_pattern(
            "pending_review:*", prefix=self.CACHE_PREFIX
        )

        logger.info(
            f"Invalidated pending review cache",
            extra={"keys_deleted": count},
        )

        return count

    async def invalidate_plan_cache(self, plan_id: UUID):
        """
        Invalida cache de um plano específico.

        Args:
            plan_id: ID do plano
        """
        cache_key = f"plan:{plan_id}"
        deleted = await cache_manager.delete(cache_key, prefix=self.CACHE_PREFIX)

        if deleted:
            logger.debug(f"Invalidated cache for plan {plan_id}")

        # Também invalida pending_review pois pode estar afetado
        await self.invalidate_pending_review_cache()

        return deleted


# Métodos helper para integração com rotas

async def get_cached_pending_review_plans(
    db,
    skip: int = 0,
    limit: int = 50,
    priority_filter: Optional[str] = None,
    professional_id: Optional[UUID] = None,
    use_cache: bool = True,
) -> dict:
    """
    Helper function para usar service cacheado em rotas.

    Args:
        db: Database session
        skip: Offset
        limit: Limit
        priority_filter: Priority filter
        professional_id: Professional ID filter
        use_cache: Use cache (default: True)

    Returns:
        Pending review plans result
    """
    service = CachedInterventionPlanService(db)
    return await service.get_pending_review_plans_cached(
        skip=skip,
        limit=limit,
        priority_filter=priority_filter,
        professional_id=professional_id,
        use_cache=use_cache,
    )


async def invalidate_intervention_plan_caches(db):
    """
    Helper function para invalidar caches de planos.

    Args:
        db: Database session
    """
    service = CachedInterventionPlanService(db)
    return await service.invalidate_pending_review_cache()
