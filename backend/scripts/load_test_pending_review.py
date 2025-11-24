#!/usr/bin/env python3
"""
Script de Teste de Carga - Endpoint Pending Review
===================================================

Executa testes de carga no endpoint /api/v1/intervention-plans/pending-review
para validar performance antes do deploy em produção.

Uso:
    python scripts/load_test_pending_review.py --requests 100 --concurrent 10
    python scripts/load_test_pending_review.py --requests 1000 --concurrent 50 --url https://api-staging.example.com

Requisitos:
    pip install aiohttp

Autor: Claude Code
Data: 2025-11-24
"""

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass
from typing import List
from statistics import mean, median

try:
    import aiohttp
except ImportError:
    print("❌ Erro: aiohttp não instalado")
    print("   Execute: pip install aiohttp")
    sys.exit(1)


@dataclass
class LoadTestResult:
    """Resultado de um teste de carga."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    response_times: List[float]
    status_codes: dict
    errors: List[str]


async def make_request(
    session: aiohttp.ClientSession, url: str, headers: dict = None
) -> tuple[int, float, str]:
    """
    Faz uma requisição HTTP GET.

    Returns:
        (status_code, response_time, error_message)
    """
    start_time = time.time()

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            await response.text()  # Consumir resposta
            response_time = time.time() - start_time
            return (response.status, response_time, "")

    except asyncio.TimeoutError:
        response_time = time.time() - start_time
        return (0, response_time, "Timeout")

    except Exception as e:
        response_time = time.time() - start_time
        return (0, response_time, str(e))


async def run_load_test(
    base_url: str, endpoint: str, num_requests: int, concurrent: int, token: str = None
) -> LoadTestResult:
    """
    Executa teste de carga com requisições concorrentes.

    Args:
        base_url: URL base da API (ex: http://localhost:8000)
        endpoint: Endpoint a testar (ex: /api/v1/intervention-plans/pending-review)
        num_requests: Número total de requisições
        concurrent: Número de requisições concorrentes
        token: Token JWT opcional para autenticação

    Returns:
        LoadTestResult com métricas do teste
    """
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"\n🚀 Iniciando teste de carga...")
    print(f"   URL: {url}")
    print(f"   Total de requisições: {num_requests}")
    print(f"   Requisições concorrentes: {concurrent}")
    print(f"   Autenticação: {'Sim' if token else 'Não'}\n")

    response_times = []
    status_codes = {}
    errors = []
    successful = 0
    failed = 0

    start_time = time.time()

    # Criar sessão HTTP
    async with aiohttp.ClientSession() as session:
        # Criar batches de requisições concorrentes
        for batch_start in range(0, num_requests, concurrent):
            batch_size = min(concurrent, num_requests - batch_start)

            # Criar tasks para o batch
            tasks = [make_request(session, url, headers) for _ in range(batch_size)]

            # Executar batch
            results = await asyncio.gather(*tasks)

            # Processar resultados
            for status, resp_time, error in results:
                response_times.append(resp_time)

                if status == 200:
                    successful += 1
                else:
                    failed += 1

                # Contar status codes
                status_codes[status] = status_codes.get(status, 0) + 1

                # Armazenar erros
                if error:
                    errors.append(error)

            # Progresso
            completed = batch_start + batch_size
            progress = (completed / num_requests) * 100
            print(f"   Progresso: {completed}/{num_requests} ({progress:.1f}%)", end="\r")

    total_time = time.time() - start_time
    print()  # Nova linha após progresso

    return LoadTestResult(
        total_requests=num_requests,
        successful_requests=successful,
        failed_requests=failed,
        total_time=total_time,
        response_times=response_times,
        status_codes=status_codes,
        errors=errors[:10],  # Primeiros 10 erros
    )


def analyze_results(result: LoadTestResult) -> dict:
    """Analisa resultados do teste de carga."""
    sorted_times = sorted(result.response_times)
    n = len(sorted_times)

    # Calcular percentis
    p50 = sorted_times[int(n * 0.50)] if n > 0 else 0
    p95 = sorted_times[int(n * 0.95)] if n > 0 else 0
    p99 = sorted_times[int(n * 0.99)] if n > 0 else 0

    return {
        "mean": mean(result.response_times) if result.response_times else 0,
        "median": median(result.response_times) if result.response_times else 0,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "min": min(result.response_times) if result.response_times else 0,
        "max": max(result.response_times) if result.response_times else 0,
        "success_rate": (result.successful_requests / result.total_requests * 100)
        if result.total_requests > 0
        else 0,
        "requests_per_second": result.total_requests / result.total_time
        if result.total_time > 0
        else 0,
    }


def print_results(result: LoadTestResult, analysis: dict):
    """Imprime resultados formatados."""
    print("\n" + "=" * 70)
    print("RESULTADOS DO TESTE DE CARGA")
    print("=" * 70 + "\n")

    # Resumo
    print("📊 RESUMO:")
    print(f"   Total de requisições:  {result.total_requests}")
    print(f"   Requisições bem-sucedidas: {result.successful_requests}")
    print(f"   Requisições com falha: {result.failed_requests}")
    print(f"   Taxa de sucesso: {analysis['success_rate']:.2f}%")
    print(f"   Tempo total: {result.total_time:.2f}s")
    print(f"   Requisições/segundo: {analysis['requests_per_second']:.2f}\n")

    # Latência
    print("⏱️  LATÊNCIA:")
    print(f"   Média: {analysis['mean']*1000:.2f}ms")
    print(f"   Mediana (P50): {analysis['p50']*1000:.2f}ms")
    print(f"   P95: {analysis['p95']*1000:.2f}ms")
    print(f"   P99: {analysis['p99']*1000:.2f}ms")
    print(f"   Mínima: {analysis['min']*1000:.2f}ms")
    print(f"   Máxima: {analysis['max']*1000:.2f}ms\n")

    # Status codes
    print("📈 STATUS CODES:")
    for status, count in sorted(result.status_codes.items()):
        percentage = (count / result.total_requests) * 100
        print(f"   {status}: {count} ({percentage:.1f}%)")

    # Erros
    if result.errors:
        print(f"\n❌ ERROS (primeiros 10):")
        for i, error in enumerate(result.errors, 1):
            print(f"   {i}. {error}")

    # Avaliação
    print("\n" + "=" * 70)
    print("AVALIAÇÃO")
    print("=" * 70)

    # Critérios de sucesso
    success_criteria = {
        "Taxa de sucesso > 95%": analysis["success_rate"] > 95,
        "P95 < 2000ms": analysis["p95"] < 2.0,
        "P99 < 5000ms": analysis["p99"] < 5.0,
        "Sem timeouts": 0 not in result.status_codes or result.status_codes[0] == 0,
    }

    all_passed = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {criterion}")

    print()
    if all_passed:
        print("✅ SUCESSO: Todos os critérios foram atendidos!")
        print("   O endpoint está pronto para produção.\n")
        return 0
    else:
        print("⚠️  ATENÇÃO: Alguns critérios não foram atendidos.")
        print("   Revise a performance antes do deploy em produção.\n")
        return 1


def get_auth_token(base_url: str, username: str, password: str) -> str:
    """Obtém token de autenticação (sync)."""
    import requests

    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        sys.exit(1)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Teste de carga para endpoint pending-review")

    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL base da API (default: http://localhost:8000)",
    )

    parser.add_argument(
        "--endpoint",
        default="/api/v1/intervention-plans/pending-review",
        help="Endpoint a testar",
    )

    parser.add_argument(
        "--requests", type=int, default=100, help="Número total de requisições (default: 100)"
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Número de requisições concorrentes (default: 10)",
    )

    parser.add_argument("--username", help="Username para autenticação (opcional)")

    parser.add_argument("--password", help="Password para autenticação (opcional)")

    args = parser.parse_args()

    # Obter token se credenciais foram fornecidas
    token = None
    if args.username and args.password:
        print(f"🔐 Obtendo token de autenticação...")
        token = get_auth_token(args.url, args.username, args.password)
        print(f"   ✓ Token obtido\n")

    # Executar teste
    result = asyncio.run(
        run_load_test(args.url, args.endpoint, args.requests, args.concurrent, token)
    )

    # Analisar e imprimir resultados
    analysis = analyze_results(result)
    exit_code = print_results(result, analysis)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
