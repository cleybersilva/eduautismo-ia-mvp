"""add notifications table

Revision ID: a1b2c3d4e5f6
Revises: 5403edb1d087
Create Date: 2025-11-24 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5403edb1d087'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria tabela de notificações para sistema de alertas.

    Suporta:
    - 7 tipos de notificação (review_overdue, review_due_soon, etc)
    - 4 níveis de prioridade (urgent, high, medium, low)
    - Marcação como lida
    - Expiração automática
    - Relacionamento com planos e usuários
    """
    # Detectar se é PostgreSQL ou SQLite
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == 'postgresql'

    # Usar UUID nativo para PostgreSQL, String para SQLite
    if is_postgresql:
        uuid_type = postgresql.UUID(as_uuid=True)
        id_default = sa.text('gen_random_uuid()')
    else:
        uuid_type = sa.String(36)
        id_default = None  # SQLite não suporta server_default para UUID

    op.create_table(
        'notifications',
        sa.Column('id', uuid_type, primary_key=True, nullable=False, default=uuid.uuid4 if not is_postgresql else None, server_default=id_default if is_postgresql else None),
        sa.Column('user_id', uuid_type, nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('intervention_plan_id', uuid_type, nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()') if is_postgresql else sa.text("(datetime('now'))"), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['intervention_plan_id'], ['intervention_plans.id'], ondelete='CASCADE'),
    )

    # Índices para performance
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], unique=False)
    op.create_index('ix_notifications_type', 'notifications', ['type'], unique=False)
    op.create_index('ix_notifications_priority', 'notifications', ['priority'], unique=False)
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'], unique=False)
    op.create_index('ix_notifications_intervention_plan_id', 'notifications', ['intervention_plan_id'], unique=False)
    op.create_index('ix_notifications_expires_at', 'notifications', ['expires_at'], unique=False)

    # Índice composto para query principal (usuário + não lidas)
    op.create_index(
        'ix_notifications_user_unread',
        'notifications',
        ['user_id', 'is_read'],
        unique=False
    )

    # Índice composto para query com prioridade
    op.create_index(
        'ix_notifications_user_priority',
        'notifications',
        ['user_id', 'priority'],
        unique=False
    )


def downgrade() -> None:
    """Remove tabela de notificações."""
    op.drop_index('ix_notifications_user_priority', table_name='notifications')
    op.drop_index('ix_notifications_user_unread', table_name='notifications')
    op.drop_index('ix_notifications_expires_at', table_name='notifications')
    op.drop_index('ix_notifications_intervention_plan_id', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_priority', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
