#!/usr/bin/env python3
"""

Valida se os índices de performance foram criados corretamente
no banco de dados após deploy da migration.

Uso:
    python scripts/validate_performance_indexes.py

Autor: Claude Code
Data: 2025-11-24
"""

import sys
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

# Índices esperados
EXPECTED_INDEXES = {
    "ix_intervention_plans_status_needs_review": ["status", "needs_review"],
    "ix_intervention_plans_last_reviewed_at": ["last_reviewed_at"],
    "ix_intervention_plans_review_frequency": ["review_frequency"],
    "ix_intervention_plans_created_by_id": ["created_by_id"],
}
Script de validação de índices de performance.

Valida se os índices criados pela migration estão presentes e sendo utilizados.

Usage:
    python scripts/validate_performance_indexes.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from app.core.database import engine
from app.core.config import settings


def validate_indexes():
    """Valida se os índices de performance foram criados."""
    print("🔍 Validando índices de performance...")
    print(f"📊 Database: {settings.DATABASE_URL}\n")

    inspector = inspect(engine)
    table_name = "intervention_plans"

    # Índices esperados
    expected_indexes = {
        "ix_intervention_plans_status_needs_review": ["status", "needs_review"],
        "ix_intervention_plans_last_reviewed_at": ["last_reviewed_at"],
        "ix_intervention_plans_review_frequency": ["review_frequency"],
        "ix_intervention_plans_created_by_id": ["created_by_id"],
    }

    # Obter índices existentes
    existing_indexes = inspector.get_indexes(table_name)

    print(f"✅ Tabela: {table_name}")
    print(f"📋 Índices encontrados: {len(existing_indexes)}\n")

    all_valid = True
    for expected_name, expected_columns in expected_indexes.items():
        found = False
        for idx in existing_indexes:
            if idx["name"] == expected_name:
                found = True
                # Verificar se as colunas estão corretas
                idx_columns = [col for col in idx["column_names"]]
                if idx_columns == expected_columns:
                    print(f"  ✅ {expected_name}")
                    print(f"     Colunas: {', '.join(expected_columns)}")
                else:
                    print(f"  ⚠️  {expected_name}")
                    print(f"     Esperado: {', '.join(expected_columns)}")
                    print(f"     Encontrado: {', '.join(idx_columns)}")
                    all_valid = False
                break

        if not found:
            print(f"  ❌ {expected_name} - NÃO ENCONTRADO")
            all_valid = False

    print()

    if all_valid:
        print("✅ Todos os índices estão corretos!")
        return True
    else:
        print("❌ Alguns índices estão faltando ou incorretos.")
        return False


def test_index_usage():
    """Testa se os índices estão sendo utilizados nas queries."""
    print("\n🔬 Testando uso de índices...\n")

    test_queries = [
        {
            "name": "Query pending_review",
            "sql": """
                SELECT id, title, status, needs_review
                FROM intervention_plans
                WHERE status = 'active' AND needs_review = true
                LIMIT 10
            """,
            "expected_index": "ix_intervention_plans_status_needs_review",
        },
        {
            "name": "Query by created_by",
            "sql": """
                SELECT id, title, created_by_id
                FROM intervention_plans
                WHERE created_by_id = '00000000-0000-0000-0000-000000000000'
                LIMIT 10
            """,
            "expected_index": "ix_intervention_plans_created_by_id",
        },
    ]

    with engine.connect() as conn:
        for test in test_queries:
            print(f"  📝 {test['name']}")

            # Para SQLite, usar EXPLAIN QUERY PLAN
            if "sqlite" in str(engine.url):
                explain_sql = f"EXPLAIN QUERY PLAN {test['sql']}"
                result = conn.execute(text(explain_sql))
                plan = [row for row in result]

                # Verificar se está usando índice
                plan_str = str(plan)
                if "ix_intervention_plans" in plan_str.lower() or "index" in plan_str.lower():
                    print(f"     ✅ Usando índice")
                else:
                    print(f"     ⚠️  Possível SCAN completo")

            # Para PostgreSQL, usar EXPLAIN
            elif "postgresql" in str(engine.url):
                explain_sql = f"EXPLAIN {test['sql']}"
                result = conn.execute(text(explain_sql))
                plan = [row[0] for row in result]

                # Verificar se está usando índice
                plan_str = "\n".join(plan)
                if "Index Scan" in plan_str or test["expected_index"] in plan_str:
                    print(f"     ✅ Index Scan detectado")
                else:
                    print(f"     ⚠️  Seq Scan (pode não estar usando índice)")

    print()


def get_table_stats():
    """Obtém estatísticas da tabela intervention_plans."""
    print("📊 Estatísticas da tabela intervention_plans:\n")

    with engine.connect() as conn:
        # Contar registros
        result = conn.execute(text("SELECT COUNT(*) FROM intervention_plans"))
        total = result.scalar()
        print(f"  Total de registros: {total}")

        # Contar por status
        result = conn.execute(
            text(
                """
            SELECT status, COUNT(*) as count
            FROM intervention_plans
            GROUP BY status
            ORDER BY count DESC
        """
            )
        )
        print(f"\n  Por status:")
        for row in result:
            print(f"    {row[0]}: {row[1]}")

        # Contar needs_review
        result = conn.execute(
            text(
                """
            SELECT needs_review, COUNT(*) as count
            FROM intervention_plans
            GROUP BY needs_review
        """
            )
        )
        print(f"\n  Needs review:")
        for row in result:
            status = "Sim" if row[0] else "Não"
            print(f"    {status}: {row[1]}")

    print()


def main():
    """Executa todas as validações."""
    print("=" * 70)
    print("  VALIDAÇÃO DE ÍNDICES DE PERFORMANCE")
    print("=" * 70)
    print()

    try:
        # 1. Validar índices
        indexes_valid = validate_indexes()

        # 2. Testar uso de índices
        test_index_usage()

        # 3. Estatísticas
        get_table_stats()

        # Resultado final
        print("=" * 70)
        if indexes_valid:
            print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO")
            print("=" * 70)
            return 0
        else:
            print("⚠️  VALIDAÇÃO CONCLUÍDA COM AVISOS")
            print("=" * 70)
            return 1

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print("=" * 70)
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
