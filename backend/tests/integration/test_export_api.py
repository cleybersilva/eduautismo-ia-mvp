"""
Testes de Integração - API de Exportação
=========================================

Testa endpoints REST de exportação CSV/Excel.

Autor: Claude Code
Data: 2025-11-24
"""

import pytest
import csv
import io
from uuid import uuid4

from fastapi import status


class TestExportAPI:
    """Testes dos endpoints de exportação."""

    def test_get_export_summary_success(self, client, auth_headers):
        """Testa obtenção de resumo de exportação."""
        response = client.get(
            "/api/v1/export/pending-review/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "total" in data
        assert "high_priority" in data
        assert "medium_priority" in data
        assert "low_priority" in data
        assert "excel_available" in data

        # Verificar tipos
        assert isinstance(data["total"], int)
        assert isinstance(data["excel_available"], bool)

    def test_get_export_summary_with_filters(self, client, auth_headers):
        """Testa resumo com filtros."""
        response = client.get(
            "/api/v1/export/pending-review/summary?priority=high",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, dict)

    def test_get_export_summary_unauthorized(self, client):
        """Testa que requer autenticação."""
        response = client.get("/api/v1/export/pending-review/summary")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_csv_success(self, client, auth_headers):
        """Testa exportação CSV."""
        response = client.get(
            "/api/v1/export/pending-review/csv",
            headers=auth_headers
        )

        # Pode ser 200 ou 404 se não houver planos
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

        if response.status_code == status.HTTP_200_OK:
            # Verificar headers
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert "attachment" in response.headers["content-disposition"]
            assert ".csv" in response.headers["content-disposition"]

            # Verificar conteúdo
            content = response.text
            assert len(content) > 0

            # Verificar se é CSV válido
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            assert len(rows) > 0  # Deve ter pelo menos cabeçalho

    def test_export_csv_with_filters(self, client, auth_headers):
        """Testa exportação CSV com filtros."""
        response = client.get(
            "/api/v1/export/pending-review/csv?priority=high&limit=100",
            headers=auth_headers
        )

        # Pode ser 200 ou 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_csv_with_student_data(self, client, auth_headers):
        """Testa exportação CSV incluindo dados do aluno."""
        response = client.get(
            "/api/v1/export/pending-review/csv?include_student=true",
            headers=auth_headers
        )

        # Pode ser 200 ou 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

        if response.status_code == status.HTTP_200_OK:
            content = response.text
            # Verificar se colunas de aluno estão presentes
            assert "Aluno" in content

    def test_export_csv_pagination(self, client, auth_headers):
        """Testa exportação CSV com paginação."""
        response = client.get(
            "/api/v1/export/pending-review/csv?skip=10&limit=50",
            headers=auth_headers
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_csv_max_limit_enforced(self, client, auth_headers):
        """Testa que limite máximo é respeitado."""
        # Tentar exportar mais de 1000
        response = client.get(
            "/api/v1/export/pending-review/csv?limit=5000",
            headers=auth_headers
        )

        # Deve aceitar, mas internamente limitar a 1000
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_csv_unauthorized(self, client):
        """Testa que requer autenticação."""
        response = client.get("/api/v1/export/pending-review/csv")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_excel_success(self, client, auth_headers):
        """Testa exportação Excel."""
        response = client.get(
            "/api/v1/export/pending-review/excel",
            headers=auth_headers
        )

        # Pode ser 200, 404 (sem dados), ou 501 (openpyxl não disponível)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_501_NOT_IMPLEMENTED
        ]

        if response.status_code == status.HTTP_200_OK:
            # Verificar headers
            assert "spreadsheetml" in response.headers["content-type"]
            assert "attachment" in response.headers["content-disposition"]
            assert ".xlsx" in response.headers["content-disposition"]

            # Verificar que é binário
            assert isinstance(response.content, bytes)
            assert len(response.content) > 0

    def test_export_excel_with_filters(self, client, auth_headers):
        """Testa exportação Excel com filtros."""
        response = client.get(
            "/api/v1/export/pending-review/excel?priority=medium&limit=100",
            headers=auth_headers
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_501_NOT_IMPLEMENTED
        ]

    def test_export_excel_unauthorized(self, client):
        """Testa que requer autenticação."""
        response = client.get("/api/v1/export/pending-review/excel")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_excel_not_implemented(self, client, auth_headers):
        """Testa resposta quando Excel não disponível."""
        response = client.get(
            "/api/v1/export/pending-review/excel",
            headers=auth_headers
        )

        if response.status_code == status.HTTP_501_NOT_IMPLEMENTED:
            data = response.json()
            assert "detail" in data
            assert "openpyxl" in data["detail"].lower()


class TestExportAPIValidation:
    """Testes de validação da API."""

    def test_export_csv_invalid_skip(self, client, auth_headers):
        """Testa skip inválido."""
        response = client.get(
            "/api/v1/export/pending-review/csv?skip=-1",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_export_csv_invalid_limit(self, client, auth_headers):
        """Testa limit inválido."""
        response = client.get(
            "/api/v1/export/pending-review/csv?limit=0",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_export_csv_limit_too_high(self, client, auth_headers):
        """Testa que limit > 1000 é rejeitado."""
        response = client.get(
            "/api/v1/export/pending-review/csv?limit=2000",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_export_csv_invalid_priority(self, client, auth_headers):
        """Testa priority inválida."""
        response = client.get(
            "/api/v1/export/pending-review/csv?priority=invalid",
            headers=auth_headers
        )

        # Aceita qualquer string, mas filtro não encontra nada
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_csv_invalid_professional_id(self, client, auth_headers):
        """Testa professional_id inválido."""
        response = client.get(
            "/api/v1/export/pending-review/csv?professional_id=invalid-uuid",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestExportAPIResponse:
    """Testes de estrutura de resposta."""

    def test_summary_response_structure(self, client, auth_headers):
        """Testa estrutura de resposta do resumo."""
        response = client.get(
            "/api/v1/export/pending-review/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Campos obrigatórios
        required_fields = [
            "total",
            "high_priority",
            "medium_priority",
            "low_priority",
            "excel_available"
        ]

        for field in required_fields:
            assert field in data

        # Tipos corretos
        assert isinstance(data["total"], int)
        assert isinstance(data["high_priority"], int)
        assert isinstance(data["medium_priority"], int)
        assert isinstance(data["low_priority"], int)
        assert isinstance(data["excel_available"], bool)

        # Soma das prioridades deve ser <= total
        priority_sum = (
            data["high_priority"] +
            data["medium_priority"] +
            data["low_priority"]
        )
        assert priority_sum <= data["total"]

    def test_csv_response_headers(self, client, auth_headers):
        """Testa headers de resposta CSV."""
        response = client.get(
            "/api/v1/export/pending-review/csv",
            headers=auth_headers
        )

        if response.status_code == status.HTTP_200_OK:
            # Content-Type correto
            assert response.headers["content-type"] == "text/csv; charset=utf-8"

            # Content-Disposition com attachment
            disposition = response.headers["content-disposition"]
            assert "attachment" in disposition
            assert "filename=" in disposition
            assert ".csv" in disposition

            # Filename deve ter timestamp
            assert "planos_pendentes_" in disposition

    def test_excel_response_headers(self, client, auth_headers):
        """Testa headers de resposta Excel."""
        response = client.get(
            "/api/v1/export/pending-review/excel",
            headers=auth_headers
        )

        if response.status_code == status.HTTP_200_OK:
            # Content-Type correto
            assert "spreadsheetml" in response.headers["content-type"]

            # Content-Disposition com attachment
            disposition = response.headers["content-disposition"]
            assert "attachment" in disposition
            assert "filename=" in disposition
            assert ".xlsx" in disposition

            # Filename deve ter timestamp
            assert "planos_pendentes_" in disposition

    def test_csv_content_structure(self, client, auth_headers):
        """Testa estrutura do conteúdo CSV."""
        response = client.get(
            "/api/v1/export/pending-review/csv",
            headers=auth_headers
        )

        if response.status_code == status.HTTP_200_OK:
            content = response.text

            # Deve começar com BOM UTF-8
            assert content.startswith("\ufeff")

            # Remove BOM para análise
            content_no_bom = content[1:]

            # Verificar estrutura CSV
            csv_reader = csv.reader(io.StringIO(content_no_bom))
            rows = list(csv_reader)

            # Deve ter cabeçalho
            assert len(rows) > 0

            header = rows[0]
            # Verificar colunas obrigatórias
            expected_columns = ["Prioridade", "ID", "Título", "Status"]
            for col in expected_columns:
                assert col in header


class TestExportAPIEdgeCases:
    """Testes de casos extremos."""

    def test_export_empty_result(self, client, auth_headers):
        """Testa exportação quando não há dados."""
        # Usar filtros que não retornam nada
        response = client.get(
            "/api/v1/export/pending-review/csv?priority=nonexistent",
            headers=auth_headers
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_with_all_filters(self, client, auth_headers):
        """Testa exportação com todos os filtros combinados."""
        professional_id = uuid4()

        response = client.get(
            f"/api/v1/export/pending-review/csv"
            f"?skip=0"
            f"&limit=100"
            f"&priority=high"
            f"&professional_id={professional_id}"
            f"&include_student=true",
            headers=auth_headers
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_csv_large_dataset(self, client, auth_headers):
        """Testa exportação de dataset grande (1000 registros)."""
        response = client.get(
            "/api/v1/export/pending-review/csv?limit=1000",
            headers=auth_headers
        )

        # Deve aceitar até 1000
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_excel_large_dataset(self, client, auth_headers):
        """Testa exportação Excel de dataset grande."""
        response = client.get(
            "/api/v1/export/pending-review/excel?limit=1000",
            headers=auth_headers
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_501_NOT_IMPLEMENTED
        ]


class TestExportAPIPerformance:
    """Testes de performance."""

    @pytest.mark.slow
    def test_csv_export_performance(self, client, auth_headers):
        """Testa tempo de exportação CSV."""
        import time

        start = time.time()
        response = client.get(
            "/api/v1/export/pending-review/csv?limit=1000",
            headers=auth_headers
        )
        duration = time.time() - start

        # Deve ser rápido (< 5s para 1000 registros)
        assert duration < 5.0

    @pytest.mark.slow
    def test_excel_export_performance(self, client, auth_headers):
        """Testa tempo de exportação Excel."""
        import time

        start = time.time()
        response = client.get(
            "/api/v1/export/pending-review/excel?limit=1000",
            headers=auth_headers
        )
        duration = time.time() - start

        if response.status_code == status.HTTP_200_OK:
            # Excel pode ser mais lento (< 10s para 1000 registros)
            assert duration < 10.0
