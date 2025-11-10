"""Initial migration - create all tables

Revision ID: 20250110_0001
Revises:
Create Date: 2025-01-10 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250110_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all database tables."""

    # Create custom enum types
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'teacher', 'parent', 'therapist')")
    op.execute("CREATE TYPE tea_level AS ENUM ('level_1', 'level_2', 'level_3')")
    op.execute("CREATE TYPE activity_type AS ENUM ('cognitive', 'social', 'motor', 'sensory', 'communication', 'daily_living', 'academic')")
    op.execute("CREATE TYPE difficulty_level AS ENUM ('very_easy', 'easy', 'medium', 'hard', 'very_hard')")
    op.execute("CREATE TYPE completion_status AS ENUM ('not_started', 'in_progress', 'completed', 'abandoned', 'needs_assistance')")
    op.execute("CREATE TYPE engagement_level AS ENUM ('none', 'low', 'medium', 'high', 'very_high')")
    op.execute("CREATE TYPE difficulty_rating AS ENUM ('too_easy', 'slightly_easy', 'appropriate', 'slightly_hard', 'too_hard')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'teacher', 'parent', 'therapist', name='user_role'), default='teacher', nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.String(1000), nullable=True),
        sa.Column('institution', sa.String(255), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_token', sa.String(255), nullable=True),
        sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create students table
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('date_of_birth', sa.Date, nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('diagnosis', sa.String(500), nullable=False),
        sa.Column('tea_level', sa.Enum('level_1', 'level_2', 'level_3', name='tea_level'), nullable=True),
        sa.Column('interests', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('learning_profile', postgresql.JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('teacher_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('activity_type', sa.Enum('cognitive', 'social', 'motor', 'sensory', 'communication', 'daily_living', 'academic', name='activity_type'), nullable=False, index=True),
        sa.Column('difficulty', sa.Enum('very_easy', 'easy', 'medium', 'hard', 'very_hard', name='difficulty_level'), nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('objectives', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('materials', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('instructions', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('adaptations', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('visual_supports', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('success_criteria', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('theme', sa.String(255), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('generated_by_ai', sa.Boolean, default=True, nullable=False),
        sa.Column('generation_metadata', postgresql.JSONB, nullable=True),
        sa.Column('resources_urls', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('attachments', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('is_published', sa.Boolean, default=True, nullable=False),
        sa.Column('is_template', sa.Boolean, default=False, nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('completion_status', sa.Enum('not_started', 'in_progress', 'completed', 'abandoned', 'needs_assistance', name='completion_status'), nullable=False, index=True),
        sa.Column('engagement_level', sa.Enum('none', 'low', 'medium', 'high', 'very_high', name='engagement_level'), nullable=False),
        sa.Column('difficulty_rating', sa.Enum('too_easy', 'slightly_easy', 'appropriate', 'slightly_hard', 'too_hard', name='difficulty_rating'), nullable=False),
        sa.Column('actual_duration_minutes', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('strengths_observed', sa.Text, nullable=True),
        sa.Column('challenges_observed', sa.Text, nullable=True),
        sa.Column('recommendations', sa.Text, nullable=True),
        sa.Column('skills_demonstrated', postgresql.JSONB, nullable=True),
        sa.Column('behavioral_notes', postgresql.JSONB, nullable=True),
        sa.Column('independence_level', sa.String(50), nullable=True),
        sa.Column('assistance_needed', sa.String(255), nullable=True),
        sa.Column('modifications_made', sa.Text, nullable=True),
        sa.Column('objectives_met', postgresql.JSONB, nullable=True),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('assessed_by_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assessed_by_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes for better query performance
    op.create_index('ix_activities_tags', 'activities', ['tags'], postgresql_using='gin')
    op.create_index('ix_students_interests', 'students', ['interests'], postgresql_using='gin')


def downgrade() -> None:
    """Drop all database tables."""

    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('assessments')
    op.drop_table('activities')
    op.drop_table('students')
    op.drop_table('users')

    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS difficulty_rating")
    op.execute("DROP TYPE IF EXISTS engagement_level")
    op.execute("DROP TYPE IF EXISTS completion_status")
    op.execute("DROP TYPE IF EXISTS difficulty_level")
    op.execute("DROP TYPE IF EXISTS activity_type")
    op.execute("DROP TYPE IF EXISTS tea_level")
    op.execute("DROP TYPE IF EXISTS user_role")
