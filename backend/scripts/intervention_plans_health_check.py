#!/usr/bin/env python3
"""
Script de relatório de saúde dos planos de intervenção.

Gera estatísticas e identifica planos que precisam de atenção.

Uso:
    python scripts/intervention_plans_health_check.py [--format FORMAT]

Formatos:
    - console: Saída formatada para terminal (padrão)
    - json: Saída em formato JSON
    - csv: Saída em formato CSV
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
from datetime import date, timedelta
from typing import Dict, List

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.intervention_plan import InterventionPlan, PlanStatus, ReviewFrequency
from app.models.student import Student


def generate_health_report(output_format: str = "console") -> Dict:
    """
    Gera relatório de saúde dos planos de intervenção.

    Args:
        output_format: Formato de saída (console, json, csv)

    Returns:
        Dict com estatísticas e listas de planos problemáticos
    """
    # Criar engine e session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Buscar todos os planos
        plans = db.query(InterventionPlan).all()

        # Inicializar report
        report = {
            "timestamp": date.today().isoformat(),
            "total_plans": len(plans),
            "by_status": {},
            "needs_attention": {
                "needs_review": [],
                "overdue": [],
                "never_reviewed": [],
                "ending_soon": [],
            },
            "summary": {
                "active_plans": 0,
                "needs_review_count": 0,
                "overdue_count": 0,
                "never_reviewed_count": 0,
                "ending_soon_count": 0,
            },
        }

        # Processar cada plano
        for plan in plans:
            # Estatísticas por status
            status_key = plan.status.value
            if status_key not in report["by_status"]:
                report["by_status"][status_key] = 0
            report["by_status"][status_key] += 1

            # Contar planos ativos
            if plan.status == PlanStatus.ACTIVE:
                report["summary"]["active_plans"] += 1

                # Recalcular needs_review
                needs_review = plan.calculate_needs_review()

                # Planos que precisam revisão
                if needs_review:
                    report["summary"]["needs_review_count"] += 1
                    report["needs_attention"]["needs_review"].append({
                        "id": str(plan.id),
                        "title": plan.title,
                        "student_id": str(plan.student_id),
                        "review_frequency": plan.review_frequency.value,
                        "last_reviewed_at": plan.last_reviewed_at.isoformat() if plan.last_reviewed_at else None,
                        "days_since_review": (date.today() - plan.last_reviewed_at).days if plan.last_reviewed_at else None,
                    })

                # Planos nunca revisados
                if plan.last_reviewed_at is None:
                    report["summary"]["never_reviewed_count"] += 1
                    report["needs_attention"]["never_reviewed"].append({
                        "id": str(plan.id),
                        "title": plan.title,
                        "student_id": str(plan.student_id),
                        "created_at": plan.created_at.date().isoformat() if plan.created_at else None,
                        "days_since_creation": (date.today() - plan.created_at.date()).days if plan.created_at else None,
                    })

                # Planos atrasados (end_date passou)
                if plan.is_overdue:
                    report["summary"]["overdue_count"] += 1
                    report["needs_attention"]["overdue"].append({
                        "id": str(plan.id),
                        "title": plan.title,
                        "student_id": str(plan.student_id),
                        "end_date": plan.end_date.isoformat(),
                        "days_overdue": (date.today() - plan.end_date).days,
                    })

                # Planos terminando em breve (próximos 7 dias)
                if plan.days_remaining > 0 and plan.days_remaining <= 7:
                    report["summary"]["ending_soon_count"] += 1
                    report["needs_attention"]["ending_soon"].append({
                        "id": str(plan.id),
                        "title": plan.title,
                        "student_id": str(plan.student_id),
                        "end_date": plan.end_date.isoformat(),
                        "days_remaining": plan.days_remaining,
                    })

        # Formatar saída
        if output_format == "console":
            _print_console_report(report)
        elif output_format == "json":
            print(json.dumps(report, indent=2))
        elif output_format == "csv":
            _print_csv_report(report)
        else:
            print(f"❌ Formato inválido: {output_format}")
            return {"error": "invalid_format"}

        return report

    except Exception as e:
        print(f"\n❌ ERRO durante geração do relatório:")
        print(f"   {type(e).__name__}: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()


def _print_console_report(report: Dict):
    """Imprime relatório formatado para console."""
    print("\n" + "=" * 80)
    print("RELATÓRIO DE SAÚDE - PLANOS DE INTERVENÇÃO")
    print("=" * 80)
    print(f"\nData: {report['timestamp']}")
    print(f"Total de planos: {report['total_plans']}")
    print()

    # Status
    print("📊 DISTRIBUIÇÃO POR STATUS")
    print("-" * 80)
    for status, count in sorted(report["by_status"].items()):
        percentage = (count / report["total_plans"] * 100) if report["total_plans"] > 0 else 0
        bar_length = int(percentage / 2)  # Max 50 chars
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {status.upper():15s} {bar} {count:3d} ({percentage:5.1f}%)")
    print()

    # Summary
    summary = report["summary"]
    print("📈 RESUMO EXECUTIVO")
    print("-" * 80)
    print(f"  • Planos ativos:           {summary['active_plans']:3d}")
    print(f"  • Precisam revisão:        {summary['needs_review_count']:3d} ⚠️")
    print(f"  • Nunca revisados:         {summary['never_reviewed_count']:3d} {'🔴' if summary['never_reviewed_count'] > 0 else '✅'}")
    print(f"  • Atrasados:               {summary['overdue_count']:3d} {'🔴' if summary['overdue_count'] > 0 else '✅'}")
    print(f"  • Terminando em breve:     {summary['ending_soon_count']:3d} {'⚠️ ' if summary['ending_soon_count'] > 0 else '✅'}")
    print()

    # Alerts
    needs_attention = report["needs_attention"]

    if summary['needs_review_count'] > 0:
        print("⚠️  PLANOS QUE PRECISAM REVISÃO")
        print("-" * 80)
        for plan in needs_attention["needs_review"][:10]:  # Top 10
            days = plan.get("days_since_review", "N/A")
            print(f"  • {plan['title'][:55]:55s} ({plan['review_frequency']:10s}) - {days} dias")
        if len(needs_attention["needs_review"]) > 10:
            print(f"  ... e mais {len(needs_attention['needs_review']) - 10} planos")
        print()

    if summary['never_reviewed_count'] > 0:
        print("🔴 PLANOS NUNCA REVISADOS")
        print("-" * 80)
        for plan in needs_attention["never_reviewed"][:10]:
            days = plan.get("days_since_creation", 0)
            print(f"  • {plan['title'][:55]:55s} - Criado há {days} dias")
        if len(needs_attention["never_reviewed"]) > 10:
            print(f"  ... e mais {len(needs_attention['never_reviewed']) - 10} planos")
        print()

    if summary['overdue_count'] > 0:
        print("🔴 PLANOS ATRASADOS")
        print("-" * 80)
        for plan in needs_attention["overdue"][:10]:
            days = plan.get("days_overdue", 0)
            print(f"  • {plan['title'][:55]:55s} - {days} dias atrasado")
        if len(needs_attention["overdue"]) > 10:
            print(f"  ... e mais {len(needs_attention['overdue']) - 10} planos")
        print()

    if summary['ending_soon_count'] > 0:
        print("⚠️  PLANOS TERMINANDO EM BREVE (próximos 7 dias)")
        print("-" * 80)
        for plan in needs_attention["ending_soon"]:
            days = plan.get("days_remaining", 0)
            print(f"  • {plan['title'][:55]:55s} - {days} dias restantes")
        print()

    # Health Score
    active = summary['active_plans']
    if active > 0:
        issues = (
            summary['needs_review_count'] +
            summary['never_reviewed_count'] +
            summary['overdue_count']
        )
        health_score = max(0, 100 - (issues / active * 100))

        print("💯 ÍNDICE DE SAÚDE")
        print("-" * 80)
        if health_score >= 90:
            status = "EXCELENTE ✅"
        elif health_score >= 70:
            status = "BOM ⚠️ "
        elif health_score >= 50:
            status = "ATENÇÃO 🟡"
        else:
            status = "CRÍTICO 🔴"

        print(f"  Score: {health_score:.1f}% - {status}")
        print()

    print("=" * 80)
    print()


def _print_csv_report(report: Dict):
    """Imprime relatório em formato CSV."""
    import csv
    import sys

    writer = csv.writer(sys.stdout)

    # Summary
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Date", report["timestamp"]])
    writer.writerow(["Total Plans", report["total_plans"]])
    writer.writerow(["Active Plans", report["summary"]["active_plans"]])
    writer.writerow(["Needs Review", report["summary"]["needs_review_count"]])
    writer.writerow(["Never Reviewed", report["summary"]["never_reviewed_count"]])
    writer.writerow(["Overdue", report["summary"]["overdue_count"]])
    writer.writerow(["Ending Soon", report["summary"]["ending_soon_count"]])
    writer.writerow([])

    # Needs Review Details
    if report["needs_attention"]["needs_review"]:
        writer.writerow(["Plans Needing Review"])
        writer.writerow(["ID", "Title", "Review Frequency", "Days Since Review"])
        for plan in report["needs_attention"]["needs_review"]:
            writer.writerow([
                plan["id"],
                plan["title"],
                plan["review_frequency"],
                plan.get("days_since_review", "N/A"),
            ])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gera relatório de saúde dos planos de intervenção",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["console", "json", "csv"],
        default="console",
        help="Formato de saída (console, json, csv)",
    )

    args = parser.parse_args()

    # Gerar relatório
    report = generate_health_report(output_format=args.format)

    # Exit code baseado no resultado
    if "error" in report:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
