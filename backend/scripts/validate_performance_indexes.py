#!/usr/bin/env python3
"""
Script de Validação de Índices de Performance
==============================================

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


def validate_indexes():
    """Valida se os índices de performance foram criados."""
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DE ÍNDICES DE PERFORMANCE")
    print("=" * 70 + "\n")

    # Conectar ao banco
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)

    # Obter índices da tabela intervention_plans
    indexes = inspector.get_indexes("intervention_plans")

    print(f"✓ Conectado ao banco: {engine.url.database}")
    print(f"✓ Total de índices na tabela 'intervention_plans': {len(indexes)}\n")

    # Validar cada índice esperado
    all_valid = True
    for index_name, expected_columns in EXPECTED_INDEXES.items():
        print(f"Validando: {index_name}")

        # Procurar índice
        found = False
        for idx in indexes:
            if idx["name"] == index_name:
                found = True
                actual_columns = idx["column_names"]

                # Validar colunas
                if set(actual_columns) == set(expected_columns):
                    print(f"  ✓ Índice encontrado")
                    print(f"  ✓ Colunas corretas: {actual_columns}")
                else:
                    print(f"  ✗ ERRO: Colunas incorretas")
                    print(f"    Esperado: {expected_columns}")
                    print(f"    Encontrado: {actual_columns}")
                    all_valid = False
                break

        if not found:
            print(f"  ✗ ERRO: Índice não encontrado!")
            all_valid = False

        print()

    return all_valid


def test_index_usage():
    """Testa se os índices estão sendo utilizados nas queries."""
    print("=" * 70)
    print("TESTE DE USO DE ÍNDICES")
    print("=" * 70 + "\n")

    engine = create_engine(str(settings.DATABASE_URL))

    # Query que deve usar o índice composto
    test_query = """
    SELECT id, student_id, status, needs_review
    FROM intervention_plans
    WHERE status = 'active' AND needs_review = true
    LIMIT 10
    """

    print("Query de teste:")
    print(test_query)
    print("\nPlano de execução:")
    print("-" * 70)

    with engine.connect() as conn:
        # Usar EXPLAIN (formato varia por banco)
        if "postgresql" in str(engine.url):
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {test_query}"
        else:  # SQLite
            explain_query = f"EXPLAIN QUERY PLAN {test_query}"

        try:
            result = conn.execute(text(explain_query))
            for row in result:
                print(row)

            print("\n✓ Consulte o plano acima para verificar se o índice está sendo usado")
            print("  Procure por: 'ix_intervention_plans_status_needs_review'")

        except Exception as e:
            print(f"✗ Erro ao executar EXPLAIN: {e}")
            return False

    print()
    return True


def get_table_stats():
    """Obtém estatísticas da tabela intervention_plans."""
    print("=" * 70)
    print("ESTATÍSTICAS DA TABELA")
    print("=" * 70 + "\n")

    engine = create_engine(str(settings.DATABASE_URL))

    queries = {
        "Total de planos": "SELECT COUNT(*) as total FROM intervention_plans",
        "Planos ativos": "SELECT COUNT(*) as total FROM intervention_plans WHERE status = 'active'",
        "Planos que precisam revisão": """
            SELECT COUNT(*) as total FROM intervention_plans
            WHERE status = 'active' AND needs_review = true
        """,
        "Distribuição por frequência": """
            SELECT review_frequency, COUNT(*) as total
            FROM intervention_plans
            GROUP BY review_frequency
            ORDER BY total DESC
        """,
    }

    with engine.connect() as conn:
        for label, query in queries.items():
            print(f"{label}:")
            try:
                result = conn.execute(text(query))
                for row in result:
                    print(f"  {dict(row)}")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
            print()


def main():
    """Função principal."""
    print("\n🔍 Iniciando validação de índices de performance...\n")

    try:
        # 1. Validar índices
        indexes_valid = validate_indexes()

        # 2. Testar uso de índices
        usage_tested = test_index_usage()

        # 3. Obter estatísticas
        get_table_stats()

        # Resultado final
        print("=" * 70)
        print("RESULTADO FINAL")
        print("=" * 70)

        if indexes_valid:
            print("\n✓ SUCESSO: Todos os índices foram criados corretamente!")
            print("✓ Verifique o plano de execução acima para confirmar o uso dos índices.")
            return 0
        else:
            print("\n✗ FALHA: Alguns índices não foram criados corretamente.")
            print("✗ Execute a migration novamente: alembic upgrade head")
            return 1

    except Exception as e:
        print(f"\n✗ ERRO FATAL: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
