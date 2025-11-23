"""add needs_review field to intervention_plans

Revision ID: zxo9rq852lkg
Revises: 0a32abc79858
Create Date: 2025-11-23 21:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'zxo9rq852lkg'
down_revision = '0a32abc79858'
branch_labels = None
depends_on = None


def upgrade():
    """Add needs_review column to intervention_plans table."""
    # Add needs_review column with default False
    op.add_column(
        'intervention_plans',
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade():
    """Remove needs_review column from intervention_plans table."""
    op.drop_column('intervention_plans', 'needs_review')
