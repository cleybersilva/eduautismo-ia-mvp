"""
Módulo de Cache Redis
=====================

Fornece funcionalidades de cache com Redis para otimizar performance
de queries frequentes e reduzir carga no banco de dados.

Uso:
    from app.core.cache import cache_manager

    # Obter do cache
    data = await cache_manager.get("key")

    # Definir no cache
    await cache_manager.set("key", data, ttl=300)

    # Invalidar cache
    await cache_manager.delete("key")

Autor: Claude Code
Data: 2025-11-24
"""

import json
import logging
from typing import Any, Optional, Union
from functools import wraps
import hashlib

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerenciador de cache Redis com suporte assíncrono.

    Fornece interface simples para operações de cache com:
    - Serialização automática JSON
    - TTL configurável
    - Invalidação por padrão
    - Fallback graceful se Redis não disponível
    """

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.enabled = REDIS_AVAILABLE and settings.ENVIRONMENT != "test"
        self._connected = False

    async def connect(self):
        """Conecta ao Redis."""
        if not self.enabled:
            logger.info("Redis cache disabled (not available or test environment)")
            return

        if self._connected:
            return

        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Testar conexão
            await self.redis.ping()
            self._connected = True
            logger.info(f"Redis cache connected: {settings.REDIS_URL}")

        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache disabled.")
            self.enabled = False
            self.redis = None

    async def disconnect(self):
        """Desconecta do Redis."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("Redis cache disconnected")

    def _serialize(self, value: Any) -> str:
        """Serializa valor para JSON."""
        return json.dumps(value, default=str)

    def _deserialize(self, value: str) -> Any:
        """Deserializa JSON para valor."""
        return json.loads(value)

    def _generate_key(self, key: str, prefix: str = "eduautismo") -> str:
        """
        Gera chave de cache com namespace.

        Args:
            key: Chave base
            prefix: Prefixo/namespace (default: eduautismo)

        Returns:
            Chave completa no formato: prefix:key
        """
        return f"{prefix}:{key}"

    async def get(self, key: str, prefix: str = "eduautismo") -> Optional[Any]:
        """
        Obtém valor do cache.

        Args:
            key: Chave do cache
            prefix: Prefixo/namespace

        Returns:
            Valor deserializado ou None se não encontrado
        """
        if not self.enabled or not self._connected:
            return None

        try:
            full_key = self._generate_key(key, prefix)
            value = await self.redis.get(full_key)

            if value is None:
                logger.debug(f"Cache miss: {full_key}")
                return None

            logger.debug(f"Cache hit: {full_key}")
            return self._deserialize(value)

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        prefix: str = "eduautismo"
    ) -> bool:
        """
        Define valor no cache.

        Args:
            key: Chave do cache
            value: Valor a ser armazenado (será serializado)
            ttl: Tempo de vida em segundos (default: REDIS_CACHE_TTL)
            prefix: Prefixo/namespace

        Returns:
            True se sucesso, False caso contrário
        """
        if not self.enabled or not self._connected:
            return False

        try:
            full_key = self._generate_key(key, prefix)
            serialized = self._serialize(value)
            ttl = ttl or settings.REDIS_CACHE_TTL

            await self.redis.setex(full_key, ttl, serialized)
            logger.debug(f"Cache set: {full_key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str, prefix: str = "eduautismo") -> bool:
        """
        Remove valor do cache.

        Args:
            key: Chave do cache
            prefix: Prefixo/namespace

        Returns:
            True se removido, False caso contrário
        """
        if not self.enabled or not self._connected:
            return False

        try:
            full_key = self._generate_key(key, prefix)
            deleted = await self.redis.delete(full_key)

            if deleted:
                logger.debug(f"Cache deleted: {full_key}")

            return bool(deleted)

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str, prefix: str = "eduautismo") -> int:
        """
        Remove múltiplas chaves por padrão.

        Args:
            pattern: Padrão de busca (ex: "pending_review:*")
            prefix: Prefixo/namespace

        Returns:
            Número de chaves deletadas
        """
        if not self.enabled or not self._connected:
            return 0

        try:
            full_pattern = self._generate_key(pattern, prefix)
            keys = []

            # Usar scan ao invés de keys() para não bloquear
            async for key in self.redis.scan_iter(match=full_pattern, count=100):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cache pattern deleted: {full_pattern} ({deleted} keys)")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str, prefix: str = "eduautismo") -> bool:
        """
        Verifica se chave existe no cache.

        Args:
            key: Chave do cache
            prefix: Prefixo/namespace

        Returns:
            True se existe, False caso contrário
        """
        if not self.enabled or not self._connected:
            return False

        try:
            full_key = self._generate_key(key, prefix)
            return bool(await self.redis.exists(full_key))

        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def ttl(self, key: str, prefix: str = "eduautismo") -> int:
        """
        Retorna tempo de vida restante da chave.

        Args:
            key: Chave do cache
            prefix: Prefixo/namespace

        Returns:
            Segundos restantes ou -1 se não existe
        """
        if not self.enabled or not self._connected:
            return -1

        try:
            full_key = self._generate_key(key, prefix)
            return await self.redis.ttl(full_key)

        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1

    async def increment(self, key: str, amount: int = 1, prefix: str = "eduautismo") -> int:
        """
        Incrementa valor numérico no cache.

        Args:
            key: Chave do cache
            amount: Quantidade a incrementar
            prefix: Prefixo/namespace

        Returns:
            Novo valor após incremento
        """
        if not self.enabled or not self._connected:
            return 0

        try:
            full_key = self._generate_key(key, prefix)
            return await self.redis.incrby(full_key, amount)

        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    def generate_cache_key(self, *args, **kwargs) -> str:
        """
        Gera chave de cache baseada em argumentos.

        Útil para criar chaves únicas para funções com parâmetros.

        Args:
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados

        Returns:
            Hash MD5 dos argumentos
        """
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Singleton instance
cache_manager = CacheManager()


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "cached",
    key_builder: Optional[callable] = None
):
    """
    Decorator para cachear resultados de funções assíncronas.

    Args:
        ttl: Tempo de vida do cache em segundos
        key_prefix: Prefixo da chave de cache
        key_builder: Função customizada para gerar chave (recebe args e kwargs)

    Uso:
        @cached(ttl=300, key_prefix="pending_review")
        async def get_pending_review_plans(skip, limit):
            # ... query database
            return results
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave de cache
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_manager.generate_cache_key(*args, **kwargs)}"

            # Tentar obter do cache
            cached_value = await cache_manager.get(cache_key, prefix=key_prefix)
            if cached_value is not None:
                logger.debug(f"Returning cached result for {func.__name__}")
                return cached_value

            # Executar função
            result = await func(*args, **kwargs)

            # Armazenar no cache
            await cache_manager.set(cache_key, result, ttl=ttl, prefix=key_prefix)

            return result

        return wrapper
    return decorator
