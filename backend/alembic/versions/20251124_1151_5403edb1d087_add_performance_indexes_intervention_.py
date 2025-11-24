"""add_performance_indexes_intervention_plans

Revision ID: 5403edb1d087
Revises: zxo9rq852lkg
Create Date: 2025-11-24 11:51:09.162950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5403edb1d087'
down_revision: Union[str, None] = 'zxo9rq852lkg'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona índices de performance para tabela intervention_plans.

    Índices criados:
    1. Composto (status, needs_review) - Para queries de pending_review
    2. last_reviewed_at - Para cálculos de dias desde última revisão
    3. review_frequency - Para filtros e agrupamentos
    4. created_by_id - Para filtros por profissional criador
    """
    # Índice composto para query principal de pending_review
    # WHERE status = 'active' AND needs_review = true
    op.create_index(
        'ix_intervention_plans_status_needs_review',
        'intervention_plans',
        ['status', 'needs_review'],
        unique=False
    )

    # Índice para cálculos de dias desde última revisão e ordenação
    op.create_index(
        'ix_intervention_plans_last_reviewed_at',
        'intervention_plans',
        ['last_reviewed_at'],
        unique=False
    )

    # Índice para filtros por frequência de revisão
    op.create_index(
        'ix_intervention_plans_review_frequency',
        'intervention_plans',
        ['review_frequency'],
        unique=False
    )

    # Índice para filtros por profissional criador
    op.create_index(
        'ix_intervention_plans_created_by_id',
        'intervention_plans',
        ['created_by_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove índices de performance."""
    op.drop_index('ix_intervention_plans_created_by_id', table_name='intervention_plans')
    op.drop_index('ix_intervention_plans_review_frequency', table_name='intervention_plans')
    op.drop_index('ix_intervention_plans_last_reviewed_at', table_name='intervention_plans')
    op.drop_index('ix_intervention_plans_status_needs_review', table_name='intervention_plans')
