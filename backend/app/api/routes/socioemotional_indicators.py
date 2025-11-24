"""
Social Emotional Indicator API endpoints - Gestão de indicadores socioemocionais.

Endpoints para registro, análise e monitoramento de indicadores socioemocionais de estudantes.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, get_professional_id
from app.core.database import get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.socioemotional_indicator import (
    BulkIndicatorCreate,
    BulkIndicatorResponse,
    IndicatorComparison,
    IndicatorFilter,
    IndicatorTrend,
    SocialEmotionalIndicatorCreate,
    SocialEmotionalIndicatorListResponse,
    SocialEmotionalIndicatorResponse,
    SocialEmotionalIndicatorUpdate,
    SocialEmotionalProfile,
)
from app.services.socioemotional_indicator_service import SocialEmotionalIndicatorService

router = APIRouter(prefix="/socioemotional-indicators", tags=["socioemotional-indicators"])


@router.post("/", response_model=SocialEmotionalIndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(
    indicator: SocialEmotionalIndicatorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Cria novo indicador socioemocional.

    **Permissões**: Requer autenticação. Profissional autenticado será registrado como autor.

    **Tipos de Indicadores** (12 tipos):
    - `emotional_regulation`: Regulação Emocional
    - `social_interaction`: Interação Social
    - `communication_skills`: Habilidades Comunicativas
    - `adaptive_behavior`: Comportamento Adaptativo
    - `sensory_processing`: Processamento Sensorial
    - `attention_focus`: Atenção e Foco
    - `anxiety_level`: Nível de Ansiedade
    - `frustration_tolerance`: Tolerância à Frustração
    - `self_regulation`: Autorregulação
    - `peer_relationship`: Relacionamento com Pares
    - `executive_function`: Função Executiva
    - `flexibility`: Flexibilidade Cognitiva/Comportamental

    **Score**: 1 (muito baixo) a 10 (muito alto)

    **Contextos de Medição**:
    - classroom, recess, therapy_session, group_activity, individual_activity,
      transition, structured_task, unstructured_time, home, other

    **Campos Opcionais**:
    - observations: Observações qualitativas
    - specific_behaviors: Comportamentos específicos observados
    - environmental_factors: Fatores ambientais
    - triggers: Gatilhos identificados
    - supports_used: Suportes/estratégias utilizados

    **Retorna**:
    - Indicador criado com propriedades calculadas (score_level, is_concerning)

    **Erros**:
    - 404: Estudante não encontrado
    """
    try:
        service = SocialEmotionalIndicatorService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.create(indicator, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/bulk", response_model=BulkIndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_bulk_indicators(
    bulk_data: BulkIndicatorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Cria múltiplos indicadores de uma vez.

    **Permissões**: Requer autenticação.

    **Uso**: Útil para registrar avaliações completas com múltiplos indicadores.

    **Exemplo**:
    ```json
    {
      "student_id": "uuid",
      "measured_at": "2025-01-17T10:00:00Z",
      "indicators": [
        {
          "indicator_type": "emotional_regulation",
          "context": "classroom",
          "score": 7
        },
        {
          "indicator_type": "social_interaction",
          "context": "recess",
          "score": 5
        }
      ]
    }
    ```

    **Retorna**:
    - Contagem de criados/falhados
    - Lista de IDs criados
    - Lista de erros (se houver)

    **Comportamento**:
    - Operação parcial: alguns podem falhar, outros serem criados
    - Erros individuais são retornados na lista de erros
    """
    service = SocialEmotionalIndicatorService(db)
    professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
    return service.create_bulk(bulk_data, professional_id)


@router.get("/{indicator_id}", response_model=SocialEmotionalIndicatorResponse)
def get_indicator(
    indicator_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Busca indicador por ID.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Dados completos do indicador
    - Propriedades calculadas (score_level, is_concerning, indicator_display_name)

    **Erros**:
    - 404: Indicador não encontrado
    """
    try:
        service = SocialEmotionalIndicatorService(db)
        return service.get_by_id(indicator_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{indicator_id}", response_model=SocialEmotionalIndicatorResponse)
def update_indicator(
    indicator_id: UUID,
    indicator_update: SocialEmotionalIndicatorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Atualiza indicador socioemocional.

    **Permissões**: Apenas o profissional que criou o indicador pode editá-lo.

    **Retorna**:
    - Indicador atualizado

    **Erros**:
    - 404: Indicador não encontrado
    - 400: Profissional não criou o indicador
    """
    try:
        service = SocialEmotionalIndicatorService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        return service.update(indicator_id, indicator_update, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(
    indicator_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
):
    """
    Remove indicador.

    **Permissões**: Apenas o profissional que criou o indicador pode removê-lo.

    **Erros**:
    - 404: Indicador não encontrado
    - 400: Profissional não criou o indicador
    """
    try:
        service = SocialEmotionalIndicatorService(db)
        professional_id = professional_id_param if professional_id_param is not None else UUID(current_user["user_id"])
        service.delete(indicator_id, professional_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=SocialEmotionalIndicatorListResponse)
def list_indicators(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[UUID] = Query(None, description="Filtrar por estudante"),
    professional_id: Optional[UUID] = Query(None, description="Filtrar por profissional"),
    indicator_type: Optional[str] = Query(None, description="Filtrar por tipo de indicador"),
    context: Optional[str] = Query(None, description="Filtrar por contexto"),
    score_min: Optional[int] = Query(None, ge=1, le=10, description="Score mínimo"),
    score_max: Optional[int] = Query(None, ge=1, le=10, description="Score máximo"),
    is_concerning: Optional[bool] = Query(None, description="Apenas indicadores preocupantes"),
    search: Optional[str] = Query(None, description="Buscar em observações"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista indicadores com filtros e paginação.

    **Permissões**: Requer autenticação.

    **Filtros Disponíveis**:
    - `student_id`: Indicadores de um estudante
    - `professional_id`: Indicadores registrados por profissional
    - `indicator_type`: Tipo específico de indicador
    - `context`: Contexto da medição
    - `score_min/max`: Range de scores
    - `is_concerning`: Apenas indicadores preocupantes
    - `search`: Busca em observações e comportamentos

    **Ordenação**: Mais recentes primeiro (por `measured_at`)

    **Retorna**:
    - Lista paginada de indicadores
    - Total de registros
    """
    filters = IndicatorFilter(
        student_id=student_id,
        professional_id=professional_id,
        indicator_type=indicator_type,
        context=context,
        score_min=score_min,
        score_max=score_max,
        is_concerning=is_concerning,
        search=search,
    )

    service = SocialEmotionalIndicatorService(db)
    indicators, total = service.list(skip=skip, limit=limit, filters=filters)

    total_pages = (total + limit - 1) // limit

    return SocialEmotionalIndicatorListResponse(
        indicators=indicators,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/student/{student_id}/list", response_model=SocialEmotionalIndicatorListResponse)
def list_indicators_by_student(
    student_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista todos os indicadores de um estudante específico.

    **Retorna**:
    - Todos os indicadores socioemocionais do estudante
    - Ordenados por data de medição
    """
    service = SocialEmotionalIndicatorService(db)
    indicators, total = service.get_by_student(student_id, skip=skip, limit=limit)

    total_pages = (total + limit - 1) // limit

    return SocialEmotionalIndicatorListResponse(
        indicators=indicators,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/student/{student_id}/profile", response_model=SocialEmotionalProfile)
def get_student_profile(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Gera perfil socioemocional completo de um estudante.

    **Permissões**: Requer autenticação.

    **Retorna**:
    - Total de medições
    - Data da última medição
    - Resumo por tipo de indicador (contagem, média, último score)
    - Indicadores preocupantes
    - Pontos fortes (scores consistentemente altos)
    - Áreas para desenvolvimento (scores baixos)
    - Tendências (últimos 90 dias) para cada indicador

    **Útil para**:
    - Dashboards do estudante
    - Relatórios para família
    - Planejamento de intervenções
    - Identificação de padrões

    **Erros**:
    - 404: Estudante não encontrado
    """
    try:
        service = SocialEmotionalIndicatorService(db)
        return service.get_profile(student_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/student/{student_id}/trend", response_model=IndicatorTrend)
def get_indicator_trend(
    student_id: UUID,
    indicator_type: str = Query(..., description="Tipo de indicador"),
    days: int = Query(90, ge=1, le=365, description="Número de dias para análise"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Analisa tendência de um indicador ao longo do tempo.

    **Permissões**: Requer autenticação.

    **Parâmetros**:
    - `indicator_type`: Tipo de indicador a analisar
    - `days`: Período de análise (padrão: 90 dias, máximo: 365)

    **Retorna**:
    - Lista de medições no período
    - Score médio
    - Direção da tendência (improving, stable, declining)
    - Score mais recente e mais antigo
    - Número de medições

    **Análise de Tendência**:
    - Compara primeira metade vs segunda metade do período
    - `improving`: Segunda metade > Primeira metade (+1 ou mais)
    - `declining`: Segunda metade < Primeira metade (-1 ou menos)
    - `stable`: Variação menor que ±1

    **Útil para**:
    - Gráficos de evolução
    - Avaliação de efetividade de intervenções
    - Relatórios de progresso

    **Erros**:
    - 404: Sem dados para o indicador no período
    """
    try:
        from app.models.socioemotional_indicator import IndicatorType

        service = SocialEmotionalIndicatorService(db)
        return service.get_trend(student_id, IndicatorType(indicator_type), days)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de indicador inválido")


@router.get("/student/{student_id}/compare", response_model=IndicatorComparison)
def compare_periods(
    student_id: UUID,
    indicator_type: str = Query(..., description="Tipo de indicador"),
    period1_start: datetime = Query(..., description="Início período 1"),
    period1_end: datetime = Query(..., description="Fim período 1"),
    period2_start: datetime = Query(..., description="Início período 2"),
    period2_end: datetime = Query(..., description="Fim período 2"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Compara indicador entre dois períodos temporais.

    **Permissões**: Requer autenticação.

    **Uso**: Avaliar impacto de intervenções comparando períodos antes/depois.

    **Parâmetros**:
    - `indicator_type`: Tipo de indicador
    - `period1_start/end`: Período 1 (ex: antes da intervenção)
    - `period2_start/end`: Período 2 (ex: durante/após intervenção)

    **Retorna**:
    - Média de cada período
    - Mudança percentual
    - Direção da mudança (improved, stable, declined)
    - Significância estatística (simplificado: > 20% de mudança)

    **Análise**:
    - `improved`: Aumento > 10%
    - `declined`: Redução > 10%
    - `stable`: Variação entre -10% e +10%
    - `statistical_significance`: true se mudança > 20%

    **Útil para**:
    - Avaliação de efetividade de planos de intervenção
    - Relatórios comparativos
    - Tomada de decisão sobre continuidade de intervenções

    **Erros**:
    - 404: Dados insuficientes em um dos períodos
    """
    try:
        from app.models.socioemotional_indicator import IndicatorType

        service = SocialEmotionalIndicatorService(db)
        return service.compare_periods(
            student_id=student_id,
            indicator_type=IndicatorType(indicator_type),
            period1_start=period1_start,
            period1_end=period1_end,
            period2_start=period2_start,
            period2_end=period2_end,
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de indicador inválido")
