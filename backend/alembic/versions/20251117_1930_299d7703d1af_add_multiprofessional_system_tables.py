"""add multiprofessional system tables

Revision ID: 299d7703d1af
Revises: 20250110_0001
Create Date: 2025-11-17 19:30:06.282422

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "299d7703d1af"
down_revision: Union[str, None] = "20250110_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create professionals table
    op.create_table(
        'professionals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('role', sa.String(50), nullable=False, index=True),
        sa.Column('specialty', sa.String(255), nullable=True),
        sa.Column('registration_number', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create professional_observations table
    op.create_table(
        'professional_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('observation_type', sa.String(50), nullable=False, index=True),
        sa.Column('context', sa.String(100), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('severity_level', sa.Integer, nullable=False, default=1),
        sa.Column('requires_intervention', sa.Boolean, default=False),
        sa.Column('is_private', sa.Boolean, default=False),
        sa.Column('behavioral_indicators', postgresql.JSON, nullable=True),
        sa.Column('socioemotional_indicators', postgresql.JSON, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_observations_student_date', 'professional_observations', ['student_id', 'observed_at'])
    op.create_index('ix_observations_professional_date', 'professional_observations', ['professional_id', 'observed_at'])

    # Create intervention_plans table
    op.create_table(
        'intervention_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('objective', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('strategies', postgresql.JSON, nullable=False),
        sa.Column('target_behaviors', postgresql.JSON, nullable=False),
        sa.Column('success_criteria', postgresql.JSON, nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('review_frequency', sa.String(50), nullable=False),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress_notes', postgresql.JSON, nullable=True),
        sa.Column('materials_resources', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('progress_percentage', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['professionals.id']),
    )
    op.create_index('ix_plans_student_status', 'intervention_plans', ['student_id', 'status'])

    # Create intervention_plan_professionals join table
    op.create_table(
        'intervention_plan_professionals',
        sa.Column('intervention_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['intervention_plan_id'], ['intervention_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('intervention_plan_id', 'professional_id'),
    )

    # Create social_emotional_indicators table
    op.create_table(
        'social_emotional_indicators',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('indicator_type', sa.String(50), nullable=False, index=True),
        sa.Column('context', sa.String(100), nullable=True),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('observations', sa.Text, nullable=True),
        sa.Column('specific_behaviors', sa.Text, nullable=True),
        sa.Column('environmental_factors', sa.Text, nullable=True),
        sa.Column('triggers', sa.Text, nullable=True),
        sa.Column('supports_used', sa.Text, nullable=True),
        sa.Column('measured_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_indicators_student_type', 'social_emotional_indicators', ['student_id', 'indicator_type'])
    op.create_index('ix_indicators_student_date', 'social_emotional_indicators', ['student_id', 'measured_at'])


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop tables in reverse order
    op.drop_index('ix_indicators_student_date', table_name='social_emotional_indicators')
    op.drop_index('ix_indicators_student_type', table_name='social_emotional_indicators')
    op.drop_table('social_emotional_indicators')

    op.drop_table('intervention_plan_professionals')

    op.drop_index('ix_plans_student_status', table_name='intervention_plans')
    op.drop_table('intervention_plans')

    op.drop_index('ix_observations_professional_date', table_name='professional_observations')
    op.drop_index('ix_observations_student_date', table_name='professional_observations')
    op.drop_table('professional_observations')

    op.drop_table('professionals')
