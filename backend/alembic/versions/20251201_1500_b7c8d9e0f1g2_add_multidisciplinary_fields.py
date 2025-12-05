"""add multidisciplinary fields to activities table (MVP 3.0)

Revision ID: b7c8d9e0f1g2
Revises: a1b2c3d4e5f6
Create Date: 2025-12-01 15:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b7c8d9e0f1g2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    """Add multidisciplinary fields to activities table for MVP 3.0."""

    # ========================================================================
    # Step 1: Create ENUM types for PostgreSQL
    # ========================================================================
    # Note: For SQLite, these will be stored as TEXT

    # Create Subject enum (25 disciplines)
    subject_enum = sa.Enum(
        "matematica",
        "portugues",
        "literatura",
        "redacao",
        "ciencias",
        "historia",
        "geografia",
        "arte",
        "educacao_fisica",
        "musica",
        "ingles",
        "espanhol",
        "biologia",
        "fisica",
        "quimica",
        "filosofia",
        "sociologia",
        "informatica",
        "artes_visuais",
        "teatro",
        "danca",
        "educacao_profissional",
        "empreendedorismo",
        "educacao_financeira",
        "educacao_ambiental",
        name="subject",
    )

    # Create GradeLevel enum (18 levels)
    grade_level_enum = sa.Enum(
        "infantil_maternal",
        "infantil_1",
        "infantil_2",
        "fundamental_1_1ano",
        "fundamental_1_2ano",
        "fundamental_1_3ano",
        "fundamental_1_4ano",
        "fundamental_1_5ano",
        "fundamental_2_6ano",
        "fundamental_2_7ano",
        "fundamental_2_8ano",
        "fundamental_2_9ano",
        "medio_1ano",
        "medio_2ano",
        "medio_3ano",
        "eja_fundamental",
        "eja_medio_1",
        "eja_medio_3",
        name="grade_level",
    )

    # Create PedagogicalActivityType enum (10 types)
    pedagogical_type_enum = sa.Enum(
        "exercicio",
        "jogo_educativo",
        "projeto",
        "leitura",
        "arte_manual",
        "experimento",
        "debate",
        "pesquisa",
        "apresentacao",
        "avaliacao",
        name="pedagogical_activity_type",
    )

    # ========================================================================
    # Step 2: Add columns to activities table
    # ========================================================================
    # All fields are nullable for backwards compatibility

    # Add subject column
    op.add_column(
        "activities",
        sa.Column(
            "subject",
            subject_enum,
            nullable=True,
            comment="Educational subject/discipline (v3.0)",
        ),
    )

    # Add grade_level column
    op.add_column(
        "activities",
        sa.Column(
            "grade_level",
            grade_level_enum,
            nullable=True,
            comment="Brazilian education grade level (v3.0)",
        ),
    )

    # Add pedagogical_type column
    op.add_column(
        "activities",
        sa.Column(
            "pedagogical_type",
            pedagogical_type_enum,
            nullable=True,
            comment="Type of pedagogical activity format (v3.0)",
        ),
    )

    # Add bncc_competencies column (array of strings)
    op.add_column(
        "activities",
        sa.Column(
            "bncc_competencies",
            sa.ARRAY(sa.String()),
            nullable=True,
            comment="BNCC competency codes (e.g., ['EF01MA01', 'EF01MA02']) (v3.0)",
        ),
    )

    # ========================================================================
    # Step 3: Create indexes for better query performance
    # ========================================================================

    # Index on subject for filtering by discipline
    op.create_index(
        op.f("ix_activities_subject"),
        "activities",
        ["subject"],
        unique=False,
    )

    # Index on grade_level for filtering by school level
    op.create_index(
        op.f("ix_activities_grade_level"),
        "activities",
        ["grade_level"],
        unique=False,
    )

    # Composite index for subject + grade_level (common query pattern)
    op.create_index(
        "ix_activities_subject_grade",
        "activities",
        ["subject", "grade_level"],
        unique=False,
    )

    print("✅ Migration completed: MVP 3.0 multidisciplinary fields added")
    print("   - Subject enum (25 disciplines)")
    print("   - GradeLevel enum (18 levels)")
    print("   - PedagogicalActivityType enum (10 types)")
    print("   - BNCC competencies array")
    print("   - Performance indexes created")


def downgrade():
    """Remove multidisciplinary fields from activities table."""

    # ========================================================================
    # Step 1: Drop indexes
    # ========================================================================
    op.drop_index("ix_activities_subject_grade", table_name="activities")
    op.drop_index(op.f("ix_activities_grade_level"), table_name="activities")
    op.drop_index(op.f("ix_activities_subject"), table_name="activities")

    # ========================================================================
    # Step 2: Drop columns
    # ========================================================================
    op.drop_column("activities", "bncc_competencies")
    op.drop_column("activities", "pedagogical_type")
    op.drop_column("activities", "grade_level")
    op.drop_column("activities", "subject")

    # ========================================================================
    # Step 3: Drop ENUM types (PostgreSQL only)
    # ========================================================================
    # Note: In PostgreSQL, ENUMs must be dropped after columns
    sa.Enum(name="pedagogical_activity_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="grade_level").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="subject").drop(op.get_bind(), checkfirst=True)

    print("✅ Downgrade completed: MVP 3.0 multidisciplinary fields removed")
