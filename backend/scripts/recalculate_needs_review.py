#!/usr/bin/env python3
"""
Script de manutenção para recalcular needs_review em todos os planos de intervenção.

Uso:
    python scripts/recalculate_needs_review.py [--dry-run] [--status STATUS]

Exemplos:
    # Recalcular todos os planos (dry-run)
    python scripts/recalculate_needs_review.py --dry-run

    # Recalcular e aplicar mudanças
    python scripts/recalculate_needs_review.py

    # Recalcular apenas planos ativos
    python scripts/recalculate_needs_review.py --status active
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.intervention_plan import InterventionPlan, PlanStatus


def recalculate_needs_review(
    dry_run: bool = False,
    status_filter: str = None,
) -> dict:
    """
    Recalcula needs_review para todos os planos de intervenção.

    Args:
        dry_run: Se True, não persiste mudanças no banco
        status_filter: Filtrar por status específico (active, draft, etc.)

    Returns:
        Dict com estatísticas da operação
    """
    # Criar engine e session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Query base
        query = db.query(InterventionPlan)

        # Aplicar filtro de status se especificado
        if status_filter:
            try:
                status = PlanStatus(status_filter.lower())
                query = query.filter(InterventionPlan.status == status)
            except ValueError:
                print(f"❌ Status inválido: {status_filter}")
                print(f"   Valores válidos: {[s.value for s in PlanStatus]}")
                return {"error": "invalid_status"}

        # Buscar todos os planos
        plans = query.all()

        print(f"\n{'=' * 80}")
        print(f"RECÁLCULO DE needs_review - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 80}\n")

        print(f"Modo: {'DRY RUN (sem persistir)' if dry_run else 'APLICAR MUDANÇAS'}")
        print(f"Filtro de status: {status_filter or 'Todos'}")
        print(f"Total de planos: {len(plans)}")
        print()

        # Estatísticas
        stats = {
            "total": len(plans),
            "changed": 0,
            "unchanged": 0,
            "true_to_false": 0,
            "false_to_true": 0,
            "already_true": 0,
            "already_false": 0,
            "by_status": {},
        }

        # Processar cada plano
        for i, plan in enumerate(plans, 1):
            old_value = plan.needs_review
            new_value = plan.calculate_needs_review()

            # Atualizar estatísticas
            status_key = plan.status.value
            if status_key not in stats["by_status"]:
                stats["by_status"][status_key] = {
                    "total": 0,
                    "changed": 0,
                    "needs_review_true": 0,
                }

            stats["by_status"][status_key]["total"] += 1

            if new_value:
                stats["by_status"][status_key]["needs_review_true"] += 1

            if old_value != new_value:
                stats["changed"] += 1
                stats["by_status"][status_key]["changed"] += 1

                if old_value and not new_value:
                    stats["true_to_false"] += 1
                    change_symbol = "✓→✗"
                else:
                    stats["false_to_true"] += 1
                    change_symbol = "✗→✓"

                print(
                    f"  [{i:3d}/{len(plans)}] {change_symbol} "
                    f"{plan.title[:50]:50s} "
                    f"({old_value} → {new_value})"
                )

                # Atualizar campo se não for dry-run
                if not dry_run:
                    plan.needs_review = new_value

            else:
                stats["unchanged"] += 1

                if new_value:
                    stats["already_true"] += 1
                else:
                    stats["already_false"] += 1

        # Commit se não for dry-run
        if not dry_run and stats["changed"] > 0:
            db.commit()
            print(f"\n✅ Mudanças persistidas no banco de dados!")
        elif dry_run and stats["changed"] > 0:
            db.rollback()
            print(f"\n⚠️  DRY RUN: Mudanças NÃO foram persistidas")
        else:
            print(f"\n✓ Nenhuma mudança necessária")

        # Imprimir estatísticas
        print(f"\n{'=' * 80}")
        print("ESTATÍSTICAS")
        print(f"{'=' * 80}\n")

        print(f"Total de planos processados: {stats['total']}")
        print(f"  • Mudanças necessárias:     {stats['changed']}")
        print(f"  • Sem mudanças:             {stats['unchanged']}")
        print()

        if stats["changed"] > 0:
            print("Tipos de mudança:")
            print(f"  • True → False:             {stats['true_to_false']}")
            print(f"  • False → True:             {stats['false_to_true']}")
            print()

        if stats["unchanged"] > 0:
            print("Planos sem mudança:")
            print(f"  • Já com True:              {stats['already_true']}")
            print(f"  • Já com False:             {stats['already_false']}")
            print()

        if stats["by_status"]:
            print("Por Status:")
            for status, data in sorted(stats["by_status"].items()):
                print(f"  • {status.upper():15s}: {data['total']:3d} planos, "
                      f"{data['changed']:3d} mudanças, "
                      f"{data['needs_review_true']:3d} precisam revisão")
            print()

        print(f"{'=' * 80}\n")

        return stats

    except Exception as e:
        print(f"\n❌ ERRO durante execução:")
        print(f"   {type(e).__name__}: {str(e)}")
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Recalcula needs_review para planos de intervenção",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Ver o que seria mudado (sem aplicar)
  python scripts/recalculate_needs_review.py --dry-run

  # Recalcular e aplicar mudanças
  python scripts/recalculate_needs_review.py

  # Recalcular apenas planos ativos
  python scripts/recalculate_needs_review.py --status active

  # Dry-run apenas em planos ativos
  python scripts/recalculate_needs_review.py --dry-run --status active

Status válidos: draft, active, paused, completed, cancelled
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Não persiste mudanças, apenas mostra o que seria alterado",
    )

    parser.add_argument(
        "--status",
        type=str,
        help="Filtrar por status específico (active, draft, completed, etc.)",
    )

    args = parser.parse_args()

    # Executar recálculo
    stats = recalculate_needs_review(
        dry_run=args.dry_run,
        status_filter=args.status,
    )

    # Exit code baseado no resultado
    if "error" in stats:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
