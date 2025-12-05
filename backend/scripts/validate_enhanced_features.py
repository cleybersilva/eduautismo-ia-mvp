#!/usr/bin/env python3
"""
EduAutismo IA - Validate Enhanced Features
==========================================

Script para validar que todas as funcionalidades avançadas estão funcionando:
- Cache Redis conectado
- Tabela de notificações criada
- Serviços operacionais
- Endpoints acessíveis

Uso: python scripts/validate_enhanced_features.py

Autor: Claude Code
Data: 2025-11-24
"""

import sys
from typing import List, Tuple

# Cores ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_test(name: str, passed: bool, message: str = ""):
    """Imprime resultado de teste."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"[{status}] {name}")
    if message:
        print(f"        {YELLOW}{message}{RESET}")


def test_imports() -> Tuple[bool, str]:
    """Testa imports de módulos."""
    try:
        from app.core.cache import cache_manager
        from app.models.notification import Notification, NotificationType, NotificationPriority
        from app.services.notification_service import NotificationService
        from app.services.export_service import ExportService
        from app.api.routes import notifications, export

        return True, "Todos os módulos importados com sucesso"
    except ImportError as e:
        return False, f"Erro de import: {e}"


def test_redis_connection() -> Tuple[bool, str]:
    """Testa conexão Redis."""
    try:
        import redis
        from app.core.config import settings

        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        client.close()

        return True, f"Redis conectado em {settings.REDIS_URL}"
    except Exception as e:
        return False, f"Erro ao conectar Redis: {e}"


def test_database_connection() -> Tuple[bool, str]:
    """Testa conexão com banco de dados."""
    try:
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "PostgreSQL conectado"
    except Exception as e:
        return False, f"Erro ao conectar PostgreSQL: {e}"


def test_notifications_table() -> Tuple[bool, str]:
    """Verifica se tabela de notificações existe."""
    try:
        from app.core.database import engine
        from sqlalchemy import text, inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "notifications" in tables:
            # Verificar colunas
            columns = [col["name"] for col in inspector.get_columns("notifications")]
            required_columns = [
                "id",
                "user_id",
                "type",
                "priority",
                "title",
                "message",
                "is_read",
                "created_at",
            ]

            missing = [col for col in required_columns if col not in columns]

            if missing:
                return False, f"Colunas faltando: {', '.join(missing)}"

            # Verificar índices
            indexes = inspector.get_indexes("notifications")
            if len(indexes) < 6:
                return (
                    False,
                    f"Esperado pelo menos 6 índices, encontrado {len(indexes)}",
                )

            return (
                True,
                f"Tabela notifications OK ({len(columns)} colunas, {len(indexes)} índices)",
            )
        else:
            return False, "Tabela notifications não encontrada"
    except Exception as e:
        return False, f"Erro ao verificar tabela: {e}"


def test_cache_manager() -> Tuple[bool, str]:
    """Testa funcionalidades do CacheManager."""
    try:
        from app.core.cache import cache_manager
        import asyncio

        async def test():
            # Conectar
            await cache_manager.connect()

            # Testar set/get
            await cache_manager.set("test_key", {"data": "test"}, ttl=60)
            value = await cache_manager.get("test_key")

            if value != {"data": "test"}:
                return False, "Valor recuperado incorreto"

            # Testar delete
            await cache_manager.delete("test_key")
            value = await cache_manager.get("test_key")

            if value is not None:
                return False, "Delete não funcionou"

            await cache_manager.disconnect()
            return True, "Operações de cache funcionando"

        return asyncio.run(test())
    except Exception as e:
        return False, f"Erro no cache manager: {e}"


def test_notification_service() -> Tuple[bool, str]:
    """Testa serviço de notificações."""
    try:
        from app.services.notification_service import NotificationService
        from app.schemas.notification import NotificationCreate
        from app.models.notification import NotificationType, NotificationPriority
        from app.core.database import get_db
        from uuid import uuid4

        db = next(get_db())

        service = NotificationService(db)

        # Criar notificação de teste
        notification_data = NotificationCreate(
            user_id=uuid4(),
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Teste de Validação",
            message="Notificação criada pelo script de validação",
        )

        notification = service.create_notification(notification_data)

        # Verificar se foi criada
        if notification.id is None:
            return False, "ID da notificação é None"

        # Buscar notificação
        found = service.get_notification(notification.id)
        if found is None:
            return False, "Notificação não encontrada após criação"

        # Deletar notificação de teste
        service.delete_notification(notification.id)

        db.close()

        return True, "Serviço de notificações funcionando"
    except Exception as e:
        return False, f"Erro no serviço: {e}"


def test_export_service() -> Tuple[bool, str]:
    """Testa serviço de exportação."""
    try:
        from app.services.export_service import ExportService
        from app.core.database import get_db

        db = next(get_db())
        service = ExportService(db)

        # Testar summary (não precisa de dados)
        summary = service.get_export_summary()

        if "total" not in summary:
            return False, "Summary não tem campo 'total'"

        if "excel_available" not in summary:
            return False, "Summary não tem campo 'excel_available'"

        db.close()

        return True, "Serviço de exportação funcionando"
    except Exception as e:
        return False, f"Erro no serviço de exportação: {e}"


def test_api_endpoints() -> Tuple[bool, str]:
    """Testa se API está rodando e endpoints estão disponíveis."""
    try:
        import requests

        base_url = "http://localhost:8000"

        # Testar health
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code != 200:
            return False, f"Health check retornou {response.status_code}"

        # Testar OpenAPI docs (não precisa auth)
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code != 200:
            return False, "OpenAPI docs não disponíveis"

        openapi = response.json()

        # Verificar se novos endpoints estão documentados
        paths = openapi.get("paths", {})

        required_endpoints = [
            "/api/v1/notifications",
            "/api/v1/export/pending-review/csv",
            "/api/v1/export/pending-review/excel",
        ]

        missing = [ep for ep in required_endpoints if ep not in paths]

        if missing:
            return (
                False,
                f"Endpoints não encontrados na OpenAPI: {', '.join(missing)}",
            )

        return True, f"API rodando, {len(paths)} endpoints documentados"
    except requests.exceptions.ConnectionError:
        return False, "API não está rodando em http://localhost:8000"
    except Exception as e:
        return False, f"Erro ao testar API: {e}"


def main():
    """Executa todos os testes de validação."""
    print_header("EduAutismo IA - Enhanced Features Validation")

    tests = [
        ("Imports de Módulos", test_imports),
        ("Conexão PostgreSQL", test_database_connection),
        ("Conexão Redis", test_redis_connection),
        ("Tabela de Notificações", test_notifications_table),
        ("Cache Manager", test_cache_manager),
        ("Serviço de Notificações", test_notification_service),
        ("Serviço de Exportação", test_export_service),
        ("API Endpoints", test_api_endpoints),
    ]

    results: List[Tuple[str, bool, str]] = []

    print(f"{BLUE}Executando {len(tests)} testes...{RESET}\n")

    for name, test_func in tests:
        try:
            passed, message = test_func()
            results.append((name, passed, message))
            print_test(name, passed, message)
        except Exception as e:
            results.append((name, False, f"Exceção: {e}"))
            print_test(name, False, f"Exceção: {e}")

    # Resumo
    print_header("Resumo")

    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count

    print(f"Total de testes: {len(results)}")
    print(f"{GREEN}Passaram: {passed_count}{RESET}")
    print(f"{RED}Falharam: {failed_count}{RESET}")

    if failed_count > 0:
        print(f"\n{RED}⚠️  Alguns testes falharam!{RESET}")
        print("\nTestes com falha:")
        for name, passed, message in results:
            if not passed:
                print(f"  - {name}: {message}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}✅ Todas as validações passaram!{RESET}")
        print("\nSistema pronto para uso!")
        sys.exit(0)


if __name__ == "__main__":
    main()
