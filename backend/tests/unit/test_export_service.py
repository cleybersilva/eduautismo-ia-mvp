"""
Testes Unitários - Export Service
==================================

Testa funcionalidades do serviço de exportação.

Autor: Claude Code
Data: 2025-11-24
"""

import pytest
import csv
import io
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.services.export_service import ExportService


@pytest.fixture
def mock_db_session():
    """Mock de sessão do banco de dados."""
    return MagicMock()


@pytest.fixture
def export_service(mock_db_session):
    """Fixture do serviço de exportação."""
    return ExportService(mock_db_session)


@pytest.fixture
def sample_plan():
    """Mock de plano de intervenção."""
    plan = MagicMock()
    plan.id = uuid4()
    plan.title = "Plano de Teste"
    plan.description = "Descrição do plano"
    plan.status = MagicMock(value="active")
    plan.review_frequency = MagicMock(value="weekly")
    plan.needs_review = True
    plan.last_reviewed_at = None
    plan.created_at = MagicMock()
    plan.created_at.strftime = MagicMock(return_value="24/11/2025 10:00")
    plan.updated_at = None
    plan.student_id = uuid4()
    plan.student = None
    return plan


@pytest.fixture
def sample_pending_review_result(sample_plan):
    """Mock de resultado de pending review."""
    return {
        "items": [
            {"plan": sample_plan, "priority": "high"},
            {"plan": sample_plan, "priority": "medium"},
        ],
        "total": 2,
        "high_priority": 1,
        "medium_priority": 1,
        "low_priority": 0,
    }


class TestExportServiceCSV:
    """Testes de exportação CSV."""

    def test_export_to_csv_success(self, export_service, sample_pending_review_result):
        """Testa exportação CSV bem-sucedida."""
        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ):
            csv_data = export_service.export_to_csv()

            assert csv_data is not None
            assert len(csv_data) > 0

            # Verificar se é CSV válido
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(csv_reader)

            assert len(rows) == 2
            assert "Prioridade" in csv_reader.fieldnames
            assert "Título" in csv_reader.fieldnames

    def test_export_to_csv_with_filters(self, export_service, sample_pending_review_result):
        """Testa exportação CSV com filtros."""
        professional_id = uuid4()

        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ) as mock_get:
            export_service.export_to_csv(
                skip=10, limit=100, priority_filter="high", professional_id=professional_id
            )

            # Verificar que filtros foram passados
            mock_get.assert_called_once_with(
                skip=10, limit=100, priority_filter="high", professional_id=professional_id
            )

    def test_export_to_csv_with_student_data(self, export_service, sample_pending_review_result):
        """Testa exportação CSV com dados do aluno."""
        # Adicionar mock de estudante
        student = MagicMock()
        student.name = "João Silva"
        student.age = 10

        for item in sample_pending_review_result["items"]:
            item["plan"].student = student

        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ):
            csv_data = export_service.export_to_csv(include_student=True)

            # Verificar que colunas de estudante foram incluídas
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            fieldnames = csv_reader.fieldnames

            assert "Aluno ID" in fieldnames
            assert "Aluno Nome" in fieldnames

    def test_export_to_csv_empty_result(self, export_service):
        """Testa exportação quando não há planos."""
        empty_result = {
            "items": [],
            "total": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
        }

        with patch.object(
            export_service.plan_service, "get_pending_review_plans", return_value=empty_result
        ):
            csv_data = export_service.export_to_csv()

            assert csv_data == ""

    def test_export_to_csv_max_limit(self, export_service, sample_pending_review_result):
        """Testa que limit máximo é respeitado."""
        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ) as mock_get:
            export_service.export_to_csv(limit=5000)  # Limite muito alto

            # Deve ser limitado a 1000
            call_args = mock_get.call_args
            assert call_args[1]["limit"] == 1000

    def test_export_to_csv_priority_formatting(self, export_service, sample_pending_review_result):
        """Testa formatação de prioridade no CSV."""
        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ):
            csv_data = export_service.export_to_csv()

            csv_reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(csv_reader)

            # Verificar que prioridades estão em uppercase
            assert rows[0]["Prioridade"] == "HIGH"
            assert rows[1]["Prioridade"] == "MEDIUM"


class TestExportServiceExcel:
    """Testes de exportação Excel."""

    @pytest.mark.skipif(
        not hasattr(ExportService, "export_to_excel"), reason="Excel export not available"
    )
    def test_export_to_excel_success(self, export_service, sample_pending_review_result):
        """Testa exportação Excel bem-sucedida."""
        with patch("app.services.export_service.EXCEL_AVAILABLE", True):
            with patch.object(
                export_service.plan_service,
                "get_pending_review_plans",
                return_value=sample_pending_review_result,
            ):
                excel_data = export_service.export_to_excel()

                assert excel_data is not None
                assert isinstance(excel_data, bytes)
                assert len(excel_data) > 0

    def test_export_to_excel_not_available(self, export_service, sample_pending_review_result):
        """Testa exportação Excel quando openpyxl não disponível."""
        with patch("app.services.export_service.EXCEL_AVAILABLE", False):
            with patch.object(
                export_service.plan_service,
                "get_pending_review_plans",
                return_value=sample_pending_review_result,
            ):
                excel_data = export_service.export_to_excel()

                assert excel_data is None

    def test_export_to_excel_empty_result(self, export_service):
        """Testa exportação Excel quando não há planos."""
        empty_result = {
            "items": [],
            "total": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
        }

        with patch("app.services.export_service.EXCEL_AVAILABLE", True):
            with patch.object(
                export_service.plan_service, "get_pending_review_plans", return_value=empty_result
            ):
                excel_data = export_service.export_to_excel()

                assert excel_data is None


class TestExportServiceHelpers:
    """Testes de métodos helper."""

    def test_get_plan_row_data_basic(self, export_service, sample_plan):
        """Testa extração de dados básicos do plano."""
        row = export_service._get_plan_row_data(sample_plan, include_student=False)

        assert "ID" in row
        assert row["Título"] == "Plano de Teste"
        assert row["Descrição"] == "Descrição do plano"
        assert row["Status"] == "active"
        assert row["Frequência de Revisão"] == "weekly"
        assert row["Precisa Revisão"] == "Sim"
        assert row["Última Revisão"] == "Nunca"

    def test_get_plan_row_data_with_student(self, export_service, sample_plan):
        """Testa extração de dados com informações do aluno."""
        # Adicionar estudante ao plano
        student = MagicMock()
        student.name = "Maria Santos"
        student.age = 12
        sample_plan.student = student

        row = export_service._get_plan_row_data(sample_plan, include_student=True)

        assert "Aluno ID" in row
        assert "Aluno Nome" in row
        assert row["Aluno Nome"] == "Maria Santos"
        assert row["Aluno Idade"] == 12

    def test_get_plan_row_data_with_review_date(self, export_service, sample_plan):
        """Testa formatação de data de revisão."""
        # Adicionar data de revisão
        sample_plan.last_reviewed_at = MagicMock()
        sample_plan.last_reviewed_at.strftime = MagicMock(return_value="15/11/2025")

        row = export_service._get_plan_row_data(sample_plan)

        assert row["Última Revisão"] == "15/11/2025"


class TestExportServiceSummary:
    """Testes de resumo de exportação."""

    def test_get_export_summary(self, export_service, sample_pending_review_result):
        """Testa obtenção de resumo."""
        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ):
            summary = export_service.get_export_summary()

            assert summary["total"] == 2
            assert summary["high_priority"] == 1
            assert summary["medium_priority"] == 1
            assert summary["low_priority"] == 0
            assert "excel_available" in summary

    def test_get_export_summary_with_filters(self, export_service, sample_pending_review_result):
        """Testa resumo com filtros aplicados."""
        professional_id = uuid4()

        with patch.object(
            export_service.plan_service,
            "get_pending_review_plans",
            return_value=sample_pending_review_result,
        ) as mock_get:
            export_service.get_export_summary(
                priority_filter="high", professional_id=professional_id
            )

            # Verificar que filtros foram passados
            call_args = mock_get.call_args
            assert call_args[1]["priority_filter"] == "high"
            assert call_args[1]["professional_id"] == professional_id


class TestExportServiceEdgeCases:
    """Testes de casos extremos."""

    def test_export_with_special_characters(self, export_service):
        """Testa exportação com caracteres especiais."""
        plan = MagicMock()
        plan.id = uuid4()
        plan.title = 'Plano com "aspas" e, vírgulas'
        plan.description = "Descrição com\nquebras\nde linha"
        plan.status = MagicMock(value="active")
        plan.review_frequency = MagicMock(value="weekly")
        plan.needs_review = True
        plan.last_reviewed_at = None
        plan.created_at = MagicMock()
        plan.created_at.strftime = MagicMock(return_value="24/11/2025 10:00")
        plan.updated_at = None
        plan.student_id = uuid4()
        plan.student = None

        result = {
            "items": [{"plan": plan, "priority": "high"}],
            "total": 1,
            "high_priority": 1,
            "medium_priority": 0,
            "low_priority": 0,
        }

        with patch.object(
            export_service.plan_service, "get_pending_review_plans", return_value=result
        ):
            csv_data = export_service.export_to_csv()

            # Verificar que CSV foi gerado
            assert csv_data is not None
            assert len(csv_data) > 0

            # Verificar que caracteres especiais foram tratados
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(csv_reader)

            assert rows[0]["Título"] == 'Plano com "aspas" e, vírgulas'

    def test_export_with_none_values(self, export_service):
        """Testa exportação com valores None."""
        plan = MagicMock()
        plan.id = uuid4()
        plan.title = "Plano"
        plan.description = None  # None
        plan.status = MagicMock(value="active")
        plan.review_frequency = MagicMock(value="weekly")
        plan.needs_review = True
        plan.last_reviewed_at = None
        plan.created_at = MagicMock()
        plan.created_at.strftime = MagicMock(return_value="24/11/2025 10:00")
        plan.updated_at = None
        plan.student_id = uuid4()
        plan.student = None

        result = {
            "items": [{"plan": plan, "priority": "high"}],
            "total": 1,
            "high_priority": 1,
            "medium_priority": 0,
            "low_priority": 0,
        }

        with patch.object(
            export_service.plan_service, "get_pending_review_plans", return_value=result
        ):
            csv_data = export_service.export_to_csv()

            # Verificar que CSV foi gerado
            assert csv_data is not None

            csv_reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(csv_reader)

            # None deve ser convertido para string vazia
            assert rows[0]["Descrição"] == ""
