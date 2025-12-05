#!/usr/bin/env python3
"""

Executa testes de carga no endpoint /api/v1/intervention-plans/pending-review
para validar performance antes do deploy em produção.

Uso:
    python scripts/load_test_pending_review.py --requests 100 --concurrent 10
    python scripts/load_test_pending_review.py --requests 1000 --concurrent 50 --url https://api-staging.example.com

Requisitos:
    pip install aiohttp

Autor: Claude Code
Data: 2025-11-24
Script de teste de carga para endpoint /pending-review.

Simula múltiplas requisições concorrentes para validar performance.

Usage:
    python scripts/load_test_pending_review.py --url http://localhost:8000 --requests 100 --concurrent 10

Requirements:
    pip install requests aiohttp rich
"""

import argparse
import asyncio
import statistics
import time
from datetime import datetime
from typing import List

try:
    import aiohttp
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("❌ Dependências faltando. Instale com:")
    print("   pip install aiohttp rich")
    exit(1)

console = Console()


class LoadTestResult:
    """Resultado de um teste de carga."""

    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0


async def make_request(session: aiohttp.ClientSession, url: str, headers: dict) -> tuple:
    """Faz uma requisição HTTP assíncrona."""
    start = time.time()
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            await response.text()  # Consumir resposta
            duration = time.time() - start
            return duration, response.status, None
    except Exception as e:
        duration = time.time() - start
        return duration, 0, str(e)


async def run_load_test(
    base_url: str, endpoint: str, num_requests: int, concurrent: int, token: str = None
) -> LoadTestResult:
    """Executa teste de carga com requisições concorrentes."""
    result = LoadTestResult()
    result.start_time = time.time()

    # Preparar headers
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # URL completa
    full_url = f"{base_url}{endpoint}"

    console.print(f"\n🚀 Iniciando teste de carga...")
    console.print(f"   URL: {full_url}")
    console.print(f"   Requisições: {num_requests}")
    console.print(f"   Concorrência: {concurrent}")
    console.print(f"   Token: {'✅ Sim' if token else '❌ Não'}\n")

    async with aiohttp.ClientSession() as session:
        # Criar tasks em batches para controlar concorrência
        for i in range(0, num_requests, concurrent):
            batch_size = min(concurrent, num_requests - i)
            tasks = [make_request(session, full_url, headers) for _ in range(batch_size)]

            # Executar batch
            results = await asyncio.gather(*tasks)

            # Processar resultados
            for duration, status_code, error in results:
                result.response_times.append(duration)
                result.status_codes.append(status_code)
                if error:
                    result.errors.append(error)

            # Progress
            completed = i + batch_size
            console.print(f"   Progresso: {completed}/{num_requests} ({completed/num_requests*100:.1f}%)")

    result.end_time = time.time()
    return result


def analyze_results(result: LoadTestResult) -> dict:
    """Analisa resultados do teste de carga."""
    total_time = result.end_time - result.start_time
    successful = len([s for s in result.status_codes if 200 <= s < 300])
    failed = len(result.status_codes) - successful

    # Calcular percentis
    sorted_times = sorted(result.response_times)
    p50 = sorted_times[len(sorted_times) // 2] if sorted_times else 0
    p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
    p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0

    return {
        "total_requests": len(result.status_codes),
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / len(result.status_codes) * 100) if result.status_codes else 0,
        "total_time": total_time,
        "requests_per_second": len(result.status_codes) / total_time if total_time > 0 else 0,
        "avg_response_time": statistics.mean(result.response_times) if result.response_times else 0,
        "min_response_time": min(result.response_times) if result.response_times else 0,
        "max_response_time": max(result.response_times) if result.response_times else 0,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "errors": len(result.errors),
    }


def print_results(analysis: dict, result: LoadTestResult):
    """Imprime resultados formatados."""
    console.print("\n" + "=" * 70)
    console.print("  📊 RESULTADOS DO TESTE DE CARGA")
    console.print("=" * 70 + "\n")

    # Tabela geral
    table = Table(title="Resumo Geral", show_header=True)
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="green")

    table.add_row("Total de Requisições", str(analysis["total_requests"]))
    table.add_row("Bem-sucedidas", f"{analysis['successful']} ({analysis['success_rate']:.1f}%)")
    table.add_row("Falhadas", f"{analysis['failed']}")
    table.add_row("Tempo Total", f"{analysis['total_time']:.2f}s")
    table.add_row("Req/s", f"{analysis['requests_per_second']:.2f}")

    console.print(table)

    # Tabela de latência
    table_latency = Table(title="Latência (segundos)", show_header=True)
    table_latency.add_column("Métrica", style="cyan")
    table_latency.add_column("Valor", style="yellow")
    table_latency.add_column("Status", style="bold")

    # Adicionar linhas com status
    def get_status(value, threshold_ok, threshold_warning):
        if value <= threshold_ok:
            return "✅ Ótimo", "green"
        elif value <= threshold_warning:
            return "⚠️  Aceitável", "yellow"
        else:
            return "❌ Ruim", "red"

    avg_status, avg_color = get_status(analysis["avg_response_time"], 0.5, 1.0)
    p50_status, p50_color = get_status(analysis["p50"], 0.5, 1.0)
    p95_status, p95_color = get_status(analysis["p95"], 1.0, 2.0)
    p99_status, p99_color = get_status(analysis["p99"], 2.0, 3.0)

    table_latency.add_row("Média", f"{analysis['avg_response_time']:.3f}s", f"[{avg_color}]{avg_status}[/]")
    table_latency.add_row("Mínima", f"{analysis['min_response_time']:.3f}s", "")
    table_latency.add_row("Máxima", f"{analysis['max_response_time']:.3f}s", "")
    table_latency.add_row("P50 (Mediana)", f"{analysis['p50']:.3f}s", f"[{p50_color}]{p50_status}[/]")
    table_latency.add_row("P95", f"{analysis['p95']:.3f}s", f"[{p95_color}]{p95_status}[/]")
    table_latency.add_row("P99", f"{analysis['p99']:.3f}s", f"[{p99_color}]{p99_status}[/]")

    console.print(table_latency)

    # Erros
    if result.errors:
        console.print(f"\n❌ Erros ({len(result.errors)}):")
        for i, error in enumerate(result.errors[:10], 1):  # Mostrar apenas 10 primeiros
            console.print(f"   {i}. {error}")
        if len(result.errors) > 10:
            console.print(f"   ... e mais {len(result.errors) - 10} erros")

    # Avaliação final
    console.print("\n" + "=" * 70)
    if analysis["success_rate"] >= 99 and analysis["p95"] <= 2.0:
        console.print("✅ [bold green]APROVADO[/] - Performance dentro do esperado!")
    elif analysis["success_rate"] >= 95 and analysis["p95"] <= 3.0:
        console.print("⚠️  [bold yellow]ATENÇÃO[/] - Performance aceitável mas pode melhorar")
    else:
        console.print("❌ [bold red]FALHOU[/] - Performance abaixo do esperado!")
    console.print("=" * 70 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Teste de carga para endpoint /pending-review")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--endpoint", default="/api/v1/intervention-plans/pending-review", help="Endpoint a testar")
    parser.add_argument("-n", "--requests", type=int, default=100, help="Número total de requisições")
    parser.add_argument("-c", "--concurrent", type=int, default=10, help="Requisições concorrentes")
    parser.add_argument("--token", help="Token de autenticação (opcional)")

    args = parser.parse_args()

    # Executar teste
    console.print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    result = asyncio.run(
        run_load_test(
            base_url=args.url,
            endpoint=args.endpoint,
            num_requests=args.requests,
            concurrent=args.concurrent,
            token=args.token,
        )
    )

    # Analisar e imprimir resultados
    analysis = analyze_results(result)
    print_results(analysis, result)

    console.print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Exit code baseado em sucesso
    if analysis["success_rate"] >= 95 and analysis["p95"] <= 2.0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
