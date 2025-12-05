"""
Testes Unitários - Cache Manager
=================================

Testa funcionalidades do gerenciador de cache Redis.

Autor: Claude Code
Data: 2025-11-24
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.cache import CacheManager, cached


@pytest.fixture
def cache_manager():
    """Fixture de cache manager."""
    manager = CacheManager()
    manager.enabled = True
    manager._connected = True
    return manager


@pytest.fixture
def mock_redis():
    """Mock do cliente Redis."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=True)
    redis_mock.ttl = AsyncMock(return_value=3600)
    redis_mock.incrby = AsyncMock(return_value=1)
    redis_mock.scan_iter = AsyncMock(return_value=iter([]))
    redis_mock.close = AsyncMock()
    return redis_mock


class TestCacheManager:
    """Testes do CacheManager."""

    @pytest.mark.asyncio
    async def test_connect_success(self, cache_manager, mock_redis):
        """Testa conexão bem-sucedida ao Redis."""
        cache_manager._connected = False

        with patch("app.core.cache.aioredis.from_url", return_value=mock_redis):
            await cache_manager.connect()

            assert cache_manager._connected is True
            assert cache_manager.redis is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure_disables_cache(self, cache_manager):
        """Testa que falha na conexão desabilita cache."""
        cache_manager._connected = False

        with patch("app.core.cache.aioredis.from_url", side_effect=Exception("Connection failed")):
            await cache_manager.connect()

            assert cache_manager.enabled is False
            assert cache_manager.redis is None

    @pytest.mark.asyncio
    async def test_disconnect(self, cache_manager, mock_redis):
        """Testa desconexão do Redis."""
        cache_manager.redis = mock_redis

        await cache_manager.disconnect()

        mock_redis.close.assert_called_once()
        assert cache_manager._connected is False

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, cache_manager, mock_redis):
        """Testa obtenção de valor do cache (hit)."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = '{"key": "value"}'

        result = await cache_manager.get("test_key")

        assert result == {"key": "value"}
        mock_redis.get.assert_called_once_with("eduautismo:test_key")

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_manager, mock_redis):
        """Testa obtenção de valor do cache (miss)."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = None

        result = await cache_manager.get("test_key")

        assert result is None
        mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_when_disabled(self, cache_manager):
        """Testa get quando cache está desabilitado."""
        cache_manager.enabled = False

        result = await cache_manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_success(self, cache_manager, mock_redis):
        """Testa definição de valor no cache."""
        cache_manager.redis = mock_redis
        test_value = {"key": "value"}

        result = await cache_manager.set("test_key", test_value, ttl=300)

        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_when_disabled(self, cache_manager):
        """Testa set quando cache está desabilitado."""
        cache_manager.enabled = False

        result = await cache_manager.set("test_key", {"data": "value"})

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self, cache_manager, mock_redis):
        """Testa remoção de valor do cache."""
        cache_manager.redis = mock_redis
        mock_redis.delete.return_value = 1

        result = await cache_manager.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("eduautismo:test_key")

    @pytest.mark.asyncio
    async def test_delete_when_not_exists(self, cache_manager, mock_redis):
        """Testa delete quando chave não existe."""
        cache_manager.redis = mock_redis
        mock_redis.delete.return_value = 0

        result = await cache_manager.delete("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_pattern(self, cache_manager, mock_redis):
        """Testa remoção por padrão."""
        cache_manager.redis = mock_redis
        keys = ["eduautismo:key1", "eduautismo:key2", "eduautismo:key3"]

        async def mock_scan():
            for key in keys:
                yield key

        mock_redis.scan_iter.return_value = mock_scan()
        mock_redis.delete.return_value = 3

        result = await cache_manager.delete_pattern("key*")

        assert result == 3
        mock_redis.delete.assert_called_once_with(*keys)

    @pytest.mark.asyncio
    async def test_exists(self, cache_manager, mock_redis):
        """Testa verificação de existência de chave."""
        cache_manager.redis = mock_redis
        mock_redis.exists.return_value = True

        result = await cache_manager.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("eduautismo:test_key")

    @pytest.mark.asyncio
    async def test_ttl(self, cache_manager, mock_redis):
        """Testa obtenção de TTL."""
        cache_manager.redis = mock_redis
        mock_redis.ttl.return_value = 1800

        result = await cache_manager.ttl("test_key")

        assert result == 1800
        mock_redis.ttl.assert_called_once_with("eduautismo:test_key")

    @pytest.mark.asyncio
    async def test_increment(self, cache_manager, mock_redis):
        """Testa incremento de valor."""
        cache_manager.redis = mock_redis
        mock_redis.incrby.return_value = 5

        result = await cache_manager.increment("counter", amount=2)

        assert result == 5
        mock_redis.incrby.assert_called_once_with("eduautismo:counter", 2)

    def test_generate_cache_key(self, cache_manager):
        """Testa geração de chave de cache."""
        key1 = cache_manager.generate_cache_key("arg1", "arg2", param1="value1")
        key2 = cache_manager.generate_cache_key("arg1", "arg2", param1="value1")
        key3 = cache_manager.generate_cache_key("arg1", "arg3", param1="value1")

        # Mesmos argumentos devem gerar mesma chave
        assert key1 == key2

        # Argumentos diferentes devem gerar chaves diferentes
        assert key1 != key3

        # Chave deve ser MD5 hash
        assert len(key1) == 32

    def test_serialize_deserialize(self, cache_manager):
        """Testa serialização e deserialização."""
        original = {"key": "value", "number": 123, "list": [1, 2, 3]}

        serialized = cache_manager._serialize(original)
        deserialized = cache_manager._deserialize(serialized)

        assert deserialized == original

    def test_generate_key_with_prefix(self, cache_manager):
        """Testa geração de chave com prefixo."""
        key = cache_manager._generate_key("test", prefix="custom")

        assert key == "custom:test"


class TestCachedDecorator:
    """Testes do decorator @cached."""

    @pytest.mark.asyncio
    async def test_cached_decorator_cache_miss(self, cache_manager, mock_redis):
        """Testa decorator quando não há valor cacheado."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = None

        call_count = 0

        @cached(ttl=300, key_prefix="test")
        async def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # Substituir cache_manager global
        with patch("app.core.cache.cache_manager", cache_manager):
            result = await expensive_function(2, 3)

            assert result == 5
            assert call_count == 1
            mock_redis.get.assert_called_once()
            mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cached_decorator_cache_hit(self, cache_manager, mock_redis):
        """Testa decorator quando há valor cacheado."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = '5'

        call_count = 0

        @cached(ttl=300, key_prefix="test")
        async def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        with patch("app.core.cache.cache_manager", cache_manager):
            result = await expensive_function(2, 3)

            assert result == 5
            assert call_count == 0  # Função não foi executada
            mock_redis.get.assert_called_once()
            mock_redis.setex.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_decorator_custom_key_builder(self, cache_manager, mock_redis):
        """Testa decorator com key builder customizado."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = None

        def custom_key_builder(x, y):
            return f"custom_{x}_{y}"

        @cached(ttl=300, key_prefix="test", key_builder=custom_key_builder)
        async def expensive_function(x, y):
            return x + y

        with patch("app.core.cache.cache_manager", cache_manager):
            await expensive_function(2, 3)

            # Verificar que chave customizada foi usada
            calls = mock_redis.get.call_args_list
            assert "custom_2_3" in str(calls[0])

    @pytest.mark.asyncio
    async def test_cached_decorator_different_args(self, cache_manager, mock_redis):
        """Testa que argumentos diferentes geram chaves diferentes."""
        cache_manager.redis = mock_redis
        mock_redis.get.return_value = None

        @cached(ttl=300, key_prefix="test")
        async def expensive_function(x, y):
            return x + y

        with patch("app.core.cache.cache_manager", cache_manager):
            await expensive_function(2, 3)
            await expensive_function(4, 5)

            # Deve ter feito 2 chamadas GET com chaves diferentes
            assert mock_redis.get.call_count == 2
            assert mock_redis.setex.call_count == 2


class TestCacheManagerEdgeCases:
    """Testes de casos extremos."""

    @pytest.mark.asyncio
    async def test_handle_redis_error_gracefully(self, cache_manager, mock_redis):
        """Testa tratamento gracioso de erros do Redis."""
        cache_manager.redis = mock_redis
        mock_redis.get.side_effect = Exception("Redis error")

        result = await cache_manager.get("test_key")

        assert result is None  # Deve retornar None em caso de erro

    @pytest.mark.asyncio
    async def test_serialize_with_datetime(self, cache_manager):
        """Testa serialização com datetime."""
        from datetime import datetime

        data = {"timestamp": datetime(2025, 11, 24, 10, 30, 0)}

        serialized = cache_manager._serialize(data)
        deserialized = cache_manager._deserialize(serialized)

        # Datetime deve ser convertido para string
        assert isinstance(deserialized["timestamp"], str)
        assert "2025-11-24" in deserialized["timestamp"]

    @pytest.mark.asyncio
    async def test_empty_pattern_delete(self, cache_manager, mock_redis):
        """Testa delete pattern quando nenhuma chave corresponde."""
        cache_manager.redis = mock_redis

        async def mock_scan():
            return
            yield  # Generator vazio

        mock_redis.scan_iter.return_value = mock_scan()

        result = await cache_manager.delete_pattern("nonexistent*")

        assert result == 0
        mock_redis.delete.assert_not_called()
