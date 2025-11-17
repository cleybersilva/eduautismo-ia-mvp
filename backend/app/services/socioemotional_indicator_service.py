"""
Social Emotional Indicator Service - Lógica de negócios para indicadores socioemocionais.

Gerenciamento e análise de indicadores socioemocionais de estudantes.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.models.professional import Professional
from app.models.socioemotional_indicator import (
    IndicatorType,
    MeasurementContext,
    SocialEmotionalIndicator,
)
from app.models.student import Student
from app.schemas.socioemotional_indicator import (
    BulkIndicatorCreate,
    BulkIndicatorResponse,
    IndicatorComparison,
    IndicatorFilter,
    IndicatorTrend,
    SocialEmotionalIndicatorCreate,
    SocialEmotionalIndicatorUpdate,
    SocialEmotionalProfile,
)


class SocialEmotionalIndicatorService:
    """Service para operações com indicadores socioemocionais."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        indicator_data: SocialEmotionalIndicatorCreate,
        professional_id: UUID,
    ) -> SocialEmotionalIndicator:
        """
        Cria novo indicador socioemocional.

        Args:
            indicator_data: Dados do indicador
            professional_id: ID do profissional que está criando

        Returns:
            SocialEmotionalIndicator criado

        Raises:
            NotFoundException: Se estudante ou profissional não existe
        """
        # Verificar se estudante existe
        student = self.db.query(Student).filter(Student.id == indicator_data.student_id).first()
        if not student:
            raise NotFoundException(f"Estudante {indicator_data.student_id} não encontrado")

        # Verificar se profissional existe
        professional = self.db.query(Professional).filter(Professional.id == professional_id).first()
        if not professional:
            raise NotFoundException(f"Profissional {professional_id} não encontrado")

        # Criar indicador
        indicator = SocialEmotionalIndicator(
            **indicator_data.model_dump(),
            professional_id=professional_id,
        )

        self.db.add(indicator)
        self.db.commit()
        self.db.refresh(indicator)

        return indicator

    def create_bulk(
        self,
        bulk_data: BulkIndicatorCreate,
        professional_id: UUID,
    ) -> BulkIndicatorResponse:
        """
        Cria múltiplos indicadores de uma vez.

        Args:
            bulk_data: Dados dos indicadores
            professional_id: ID do profissional que está criando

        Returns:
            BulkIndicatorResponse com resultado da operação
        """
        created_ids = []
        errors = []

        for indicator_dict in bulk_data.indicators:
            try:
                indicator_data = SocialEmotionalIndicatorCreate(
                    student_id=bulk_data.student_id,
                    measured_at=bulk_data.measured_at,
                    **indicator_dict
                )
                indicator = self.create(indicator_data, professional_id)
                created_ids.append(indicator.id)
            except Exception as e:
                errors.append(f"Erro ao criar indicador: {str(e)}")

        return BulkIndicatorResponse(
            created_count=len(created_ids),
            failed_count=len(errors),
            created_ids=created_ids,
            errors=errors if errors else None,
        )

    def get_by_id(self, indicator_id: UUID) -> SocialEmotionalIndicator:
        """
        Busca indicador por ID.

        Args:
            indicator_id: ID do indicador

        Returns:
            SocialEmotionalIndicator encontrado

        Raises:
            NotFoundException: Se indicador não existe
        """
        indicator = (
            self.db.query(SocialEmotionalIndicator)
            .filter(SocialEmotionalIndicator.id == indicator_id)
            .first()
        )

        if not indicator:
            raise NotFoundException(f"Indicador {indicator_id} não encontrado")

        return indicator

    def update(
        self,
        indicator_id: UUID,
        update_data: SocialEmotionalIndicatorUpdate,
        professional_id: UUID,
    ) -> SocialEmotionalIndicator:
        """
        Atualiza indicador.

        Args:
            indicator_id: ID do indicador
            update_data: Dados para atualização
            professional_id: ID do profissional que está atualizando

        Returns:
            SocialEmotionalIndicator atualizado

        Raises:
            NotFoundException: Se indicador não existe
            ValidationException: Se profissional não criou o indicador
        """
        indicator = self.get_by_id(indicator_id)

        # Apenas quem criou pode editar
        if indicator.professional_id != professional_id:
            raise ValidationException("Apenas o profissional que criou o indicador pode editá-lo")

        # Atualizar campos fornecidos
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(indicator, field, value)

        self.db.commit()
        self.db.refresh(indicator)

        return indicator

    def delete(self, indicator_id: UUID, professional_id: UUID) -> bool:
        """
        Remove indicador.

        Args:
            indicator_id: ID do indicador
            professional_id: ID do profissional que está removendo

        Returns:
            True se removido com sucesso

        Raises:
            NotFoundException: Se indicador não existe
            ValidationException: Se profissional não criou o indicador
        """
        indicator = self.get_by_id(indicator_id)

        # Apenas quem criou pode deletar
        if indicator.professional_id != professional_id:
            raise ValidationException("Apenas o profissional que criou o indicador pode removê-lo")

        self.db.delete(indicator)
        self.db.commit()

        return True

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[IndicatorFilter] = None,
    ) -> tuple[List[SocialEmotionalIndicator], int]:
        """
        Lista indicadores com filtros e paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            filters: Filtros opcionais

        Returns:
            Tupla (lista de indicadores, total)
        """
        query = self.db.query(SocialEmotionalIndicator)

        # Aplicar filtros
        if filters:
            if filters.student_id:
                query = query.filter(SocialEmotionalIndicator.student_id == filters.student_id)

            if filters.professional_id:
                query = query.filter(SocialEmotionalIndicator.professional_id == filters.professional_id)

            if filters.indicator_type:
                query = query.filter(SocialEmotionalIndicator.indicator_type == filters.indicator_type)

            if filters.context:
                query = query.filter(SocialEmotionalIndicator.context == filters.context)

            if filters.score_min is not None:
                query = query.filter(SocialEmotionalIndicator.score >= filters.score_min)

            if filters.score_max is not None:
                query = query.filter(SocialEmotionalIndicator.score <= filters.score_max)

            if filters.is_concerning is not None:
                # Filtrar indicadores preocupantes (precisa lógica complexa)
                # Simplificado: usar score extremos
                if filters.is_concerning:
                    query = query.filter(
                        or_(
                            SocialEmotionalIndicator.score <= 3,
                            SocialEmotionalIndicator.score >= 8
                        )
                    )

            if filters.date_from:
                query = query.filter(SocialEmotionalIndicator.measured_at >= filters.date_from)

            if filters.date_to:
                query = query.filter(SocialEmotionalIndicator.measured_at <= filters.date_to)

            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        SocialEmotionalIndicator.observations.ilike(search_pattern),
                        SocialEmotionalIndicator.specific_behaviors.ilike(search_pattern),
                    )
                )

        # Total de registros
        total = query.count()

        # Ordenação (mais recentes primeiro) e paginação
        indicators = (
            query.order_by(SocialEmotionalIndicator.measured_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return indicators, total

    def get_by_student(
        self,
        student_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[SocialEmotionalIndicator], int]:
        """Lista indicadores de um estudante específico."""
        filters = IndicatorFilter(student_id=student_id)
        return self.list(skip=skip, limit=limit, filters=filters)

    def get_trend(
        self,
        student_id: UUID,
        indicator_type: IndicatorType,
        days: int = 90,
    ) -> IndicatorTrend:
        """
        Analisa tendência de um indicador ao longo do tempo.

        Args:
            student_id: ID do estudante
            indicator_type: Tipo de indicador
            days: Número de dias para análise (padrão: 90)

        Returns:
            IndicatorTrend com análise de tendência
        """
        # Data limite
        date_from = datetime.now() - timedelta(days=days)

        # Buscar medições
        measurements_query = (
            self.db.query(SocialEmotionalIndicator)
            .filter(
                and_(
                    SocialEmotionalIndicator.student_id == student_id,
                    SocialEmotionalIndicator.indicator_type == indicator_type,
                    SocialEmotionalIndicator.measured_at >= date_from,
                )
            )
            .order_by(SocialEmotionalIndicator.measured_at)
            .all()
        )

        if not measurements_query:
            raise NotFoundException(
                f"Nenhuma medição encontrada para {indicator_type} nos últimos {days} dias"
            )

        # Preparar dados das medições
        measurements = [
            {
                "date": m.measured_at.isoformat(),
                "score": m.score,
                "context": str(m.context),
            }
            for m in measurements_query
        ]

        # Calcular média
        scores = [m.score for m in measurements_query]
        average_score = sum(scores) / len(scores)

        # Determinar direção da tendência
        if len(scores) >= 2:
            first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)

            if second_half_avg > first_half_avg + 1:
                trend_direction = "improving"
            elif second_half_avg < first_half_avg - 1:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        # Criar indicador base para pegar display_name
        sample_indicator = measurements_query[0]

        return IndicatorTrend(
            indicator_type=indicator_type,
            indicator_display_name=sample_indicator.indicator_display_name,
            measurements=measurements,
            average_score=average_score,
            trend_direction=trend_direction,
            latest_score=scores[-1],
            earliest_score=scores[0],
            measurement_count=len(measurements),
        )

    def get_profile(self, student_id: UUID) -> SocialEmotionalProfile:
        """
        Gera perfil socioemocional completo de um estudante.

        Args:
            student_id: ID do estudante

        Returns:
            SocialEmotionalProfile com análise completa
        """
        # Verificar se estudante existe
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise NotFoundException(f"Estudante {student_id} não encontrado")

        # Buscar todos os indicadores do estudante
        all_indicators = (
            self.db.query(SocialEmotionalIndicator)
            .filter(SocialEmotionalIndicator.student_id == student_id)
            .all()
        )

        if not all_indicators:
            # Retornar perfil vazio se não há medições
            return SocialEmotionalProfile(
                student_id=student_id,
                student_name=getattr(student, 'name', None),
                total_measurements=0,
                last_measured_at=None,
                indicators_summary={},
                concerning_indicators=[],
                strengths=[],
                areas_for_development=[],
                trends=[],
            )

        # Total de medições
        total_measurements = len(all_indicators)

        # Última medição
        last_measured_at = max(ind.measured_at for ind in all_indicators)

        # Resumo por tipo de indicador
        indicators_summary = {}
        for indicator_type in IndicatorType:
            type_indicators = [
                ind for ind in all_indicators
                if ind.indicator_type == indicator_type
            ]
            if type_indicators:
                scores = [ind.score for ind in type_indicators]
                indicators_summary[str(indicator_type)] = {
                    "count": len(type_indicators),
                    "average_score": sum(scores) / len(scores),
                    "latest_score": type_indicators[-1].score,
                    "is_concerning": type_indicators[-1].is_concerning,
                }

        # Indicadores preocupantes
        concerning_indicators = [
            ind.indicator_display_name
            for ind in all_indicators
            if ind.is_concerning
        ]
        concerning_indicators = list(set(concerning_indicators))  # Remover duplicatas

        # Pontos fortes (scores altos consistentes em indicadores positivos)
        strengths = []
        for indicator_type in IndicatorType:
            if str(indicator_type) in indicators_summary:
                summary = indicators_summary[str(indicator_type)]
                if summary["average_score"] >= 7:
                    # Criar indicador temporário para pegar display_name
                    temp_ind = SocialEmotionalIndicator(indicator_type=indicator_type)
                    strengths.append(temp_ind.indicator_display_name)

        # Áreas para desenvolvimento (scores baixos)
        areas_for_development = []
        for indicator_type in IndicatorType:
            if str(indicator_type) in indicators_summary:
                summary = indicators_summary[str(indicator_type)]
                if summary["average_score"] <= 4:
                    temp_ind = SocialEmotionalIndicator(indicator_type=indicator_type)
                    areas_for_development.append(temp_ind.indicator_display_name)

        # Tendências (últimos 90 dias)
        trends = []
        for indicator_type in IndicatorType:
            try:
                trend = self.get_trend(student_id, indicator_type, days=90)
                trends.append(trend)
            except NotFoundException:
                # Sem dados para este indicador
                pass

        return SocialEmotionalProfile(
            student_id=student_id,
            student_name=getattr(student, 'name', None),
            total_measurements=total_measurements,
            last_measured_at=last_measured_at,
            indicators_summary=indicators_summary,
            concerning_indicators=concerning_indicators,
            strengths=strengths,
            areas_for_development=areas_for_development,
            trends=trends,
        )

    def compare_periods(
        self,
        student_id: UUID,
        indicator_type: IndicatorType,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
    ) -> IndicatorComparison:
        """
        Compara indicador entre dois períodos.

        Args:
            student_id: ID do estudante
            indicator_type: Tipo de indicador
            period1_start: Início do período 1
            period1_end: Fim do período 1
            period2_start: Início do período 2
            period2_end: Fim do período 2

        Returns:
            IndicatorComparison com análise comparativa
        """
        # Período 1
        period1_indicators = (
            self.db.query(SocialEmotionalIndicator)
            .filter(
                and_(
                    SocialEmotionalIndicator.student_id == student_id,
                    SocialEmotionalIndicator.indicator_type == indicator_type,
                    SocialEmotionalIndicator.measured_at >= period1_start,
                    SocialEmotionalIndicator.measured_at <= period1_end,
                )
            )
            .all()
        )

        # Período 2
        period2_indicators = (
            self.db.query(SocialEmotionalIndicator)
            .filter(
                and_(
                    SocialEmotionalIndicator.student_id == student_id,
                    SocialEmotionalIndicator.indicator_type == indicator_type,
                    SocialEmotionalIndicator.measured_at >= period2_start,
                    SocialEmotionalIndicator.measured_at <= period2_end,
                )
            )
            .all()
        )

        if not period1_indicators or not period2_indicators:
            raise NotFoundException("Dados insuficientes para comparação entre períodos")

        # Médias
        period1_avg = sum(ind.score for ind in period1_indicators) / len(period1_indicators)
        period2_avg = sum(ind.score for ind in period2_indicators) / len(period2_indicators)

        # Mudança percentual
        change_percentage = ((period2_avg - period1_avg) / period1_avg) * 100

        # Direção da mudança
        if change_percentage > 10:
            change_direction = "improved"
        elif change_percentage < -10:
            change_direction = "declined"
        else:
            change_direction = "stable"

        # Significância estatística (simplificado)
        statistical_significance = abs(change_percentage) > 20

        return IndicatorComparison(
            student_id=student_id,
            indicator_type=indicator_type,
            period1_start=period1_start,
            period1_end=period1_end,
            period1_average=period1_avg,
            period2_start=period2_start,
            period2_end=period2_end,
            period2_average=period2_avg,
            change_percentage=change_percentage,
            change_direction=change_direction,
            statistical_significance=statistical_significance,
        )
