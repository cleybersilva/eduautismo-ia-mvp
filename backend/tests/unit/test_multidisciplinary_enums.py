"""
Unit tests for MVP 3.0 Multidisciplinary Enums.

Tests Subject, GradeLevel, and PedagogicalActivityType enums and helper functions.
"""

import pytest

from app.utils.constants import (
    GradeLevel,
    PedagogicalActivityType,
    Subject,
    get_grade_level_display_name,
    get_grade_levels,
    get_pedagogical_activity_types,
    get_subject_display_name,
    get_subjects,
    get_subjects_by_grade_level,
)


class TestSubjectEnum:
    """Test Subject enum."""

    def test_subject_enum_values(self):
        """Test that all 25 subjects are defined."""
        subjects = list(Subject)
        assert len(subjects) == 25

    def test_core_subjects_exist(self):
        """Test core subjects are present."""
        assert Subject.MATEMATICA.value == "matematica"
        assert Subject.PORTUGUES.value == "portugues"
        assert Subject.CIENCIAS.value == "ciencias"
        assert Subject.HISTORIA.value == "historia"
        assert Subject.GEOGRAFIA.value == "geografia"

    def test_arts_subjects_exist(self):
        """Test arts and PE subjects."""
        assert Subject.ARTE.value == "arte"
        assert Subject.EDUCACAO_FISICA.value == "educacao_fisica"
        assert Subject.MUSICA.value == "musica"

    def test_language_subjects_exist(self):
        """Test language subjects."""
        assert Subject.INGLES.value == "ingles"
        assert Subject.ESPANHOL.value == "espanhol"

    def test_high_school_subjects_exist(self):
        """Test high school specific subjects."""
        assert Subject.BIOLOGIA.value == "biologia"
        assert Subject.FISICA.value == "fisica"
        assert Subject.QUIMICA.value == "quimica"
        assert Subject.FILOSOFIA.value == "filosofia"
        assert Subject.SOCIOLOGIA.value == "sociologia"


class TestGradeLevelEnum:
    """Test GradeLevel enum."""

    def test_grade_level_enum_count(self):
        """Test that all 18 grade levels are defined."""
        grade_levels = list(GradeLevel)
        assert len(grade_levels) == 18

    def test_infantil_levels_exist(self):
        """Test early childhood levels."""
        assert GradeLevel.INFANTIL_MATERNAL.value == "infantil_maternal"
        assert GradeLevel.INFANTIL_1.value == "infantil_1"
        assert GradeLevel.INFANTIL_2.value == "infantil_2"

    def test_fundamental_1_levels_exist(self):
        """Test elementary years 1-5."""
        assert GradeLevel.FUNDAMENTAL_1_1ANO.value == "fundamental_1_1ano"
        assert GradeLevel.FUNDAMENTAL_1_2ANO.value == "fundamental_1_2ano"
        assert GradeLevel.FUNDAMENTAL_1_3ANO.value == "fundamental_1_3ano"
        assert GradeLevel.FUNDAMENTAL_1_4ANO.value == "fundamental_1_4ano"
        assert GradeLevel.FUNDAMENTAL_1_5ANO.value == "fundamental_1_5ano"

    def test_fundamental_2_levels_exist(self):
        """Test middle school years 6-9."""
        assert GradeLevel.FUNDAMENTAL_2_6ANO.value == "fundamental_2_6ano"
        assert GradeLevel.FUNDAMENTAL_2_7ANO.value == "fundamental_2_7ano"
        assert GradeLevel.FUNDAMENTAL_2_8ANO.value == "fundamental_2_8ano"
        assert GradeLevel.FUNDAMENTAL_2_9ANO.value == "fundamental_2_9ano"

    def test_medio_levels_exist(self):
        """Test high school levels."""
        assert GradeLevel.MEDIO_1ANO.value == "medio_1ano"
        assert GradeLevel.MEDIO_2ANO.value == "medio_2ano"
        assert GradeLevel.MEDIO_3ANO.value == "medio_3ano"

    def test_eja_levels_exist(self):
        """Test adult education levels."""
        assert GradeLevel.EJA_FUNDAMENTAL.value == "eja_fundamental"
        assert GradeLevel.EJA_MEDIO_1.value == "eja_medio_1"
        assert GradeLevel.EJA_MEDIO_3.value == "eja_medio_3"


class TestPedagogicalActivityTypeEnum:
    """Test PedagogicalActivityType enum."""

    def test_pedagogical_type_count(self):
        """Test that all 10 pedagogical types are defined."""
        types = list(PedagogicalActivityType)
        assert len(types) == 10

    def test_pedagogical_types_exist(self):
        """Test all pedagogical activity types."""
        assert PedagogicalActivityType.EXERCICIO.value == "exercicio"
        assert PedagogicalActivityType.JOGO_EDUCATIVO.value == "jogo_educativo"
        assert PedagogicalActivityType.PROJETO.value == "projeto"
        assert PedagogicalActivityType.LEITURA.value == "leitura"
        assert PedagogicalActivityType.ARTE_MANUAL.value == "arte_manual"
        assert PedagogicalActivityType.EXPERIMENTO.value == "experimento"
        assert PedagogicalActivityType.DEBATE.value == "debate"
        assert PedagogicalActivityType.PESQUISA.value == "pesquisa"
        assert PedagogicalActivityType.APRESENTACAO.value == "apresentacao"
        assert PedagogicalActivityType.AVALIACAO.value == "avaliacao"


class TestHelperFunctions:
    """Test helper functions for enums."""

    def test_get_subjects_returns_list(self):
        """Test get_subjects returns list of strings."""
        subjects = get_subjects()
        assert isinstance(subjects, list)
        assert len(subjects) == 25
        assert "matematica" in subjects
        assert "portugues" in subjects

    def test_get_grade_levels_returns_list(self):
        """Test get_grade_levels returns list of strings."""
        grade_levels = get_grade_levels()
        assert isinstance(grade_levels, list)
        assert len(grade_levels) == 18
        assert "fundamental_1_3ano" in grade_levels

    def test_get_pedagogical_activity_types_returns_list(self):
        """Test get_pedagogical_activity_types returns list."""
        types = get_pedagogical_activity_types()
        assert isinstance(types, list)
        assert len(types) == 10
        assert "exercicio" in types

    def test_get_subject_display_name(self):
        """Test display name translation for subjects."""
        assert get_subject_display_name(Subject.MATEMATICA) == "Matemática"
        assert get_subject_display_name(Subject.PORTUGUES) == "Português"
        assert get_subject_display_name(Subject.EDUCACAO_FISICA) == "Educação Física"

    def test_get_grade_level_display_name(self):
        """Test display name translation for grade levels."""
        assert get_grade_level_display_name(GradeLevel.INFANTIL_MATERNAL) == "Infantil - Maternal"
        assert get_grade_level_display_name(GradeLevel.FUNDAMENTAL_1_3ANO) == "3º Ano - Fundamental I"
        assert get_grade_level_display_name(GradeLevel.MEDIO_1ANO) == "1ª Série - Ensino Médio"

    def test_get_subjects_by_grade_level_infantil(self):
        """Test subjects for early childhood."""
        subjects = get_subjects_by_grade_level(GradeLevel.INFANTIL_1)
        assert Subject.PORTUGUES in subjects
        assert Subject.MATEMATICA in subjects
        assert Subject.ARTE in subjects
        assert Subject.MUSICA in subjects
        assert Subject.EDUCACAO_FISICA in subjects
        # Should not have high school subjects
        assert Subject.FISICA not in subjects

    def test_get_subjects_by_grade_level_fundamental_1(self):
        """Test subjects for elementary years 1-5."""
        subjects = get_subjects_by_grade_level(GradeLevel.FUNDAMENTAL_1_3ANO)
        assert Subject.PORTUGUES in subjects
        assert Subject.MATEMATICA in subjects
        assert Subject.CIENCIAS in subjects
        assert Subject.HISTORIA in subjects
        assert Subject.GEOGRAFIA in subjects
        assert Subject.INGLES in subjects
        # Should not have high school subjects
        assert Subject.FISICA not in subjects

    def test_get_subjects_by_grade_level_medio(self):
        """Test subjects for high school."""
        subjects = get_subjects_by_grade_level(GradeLevel.MEDIO_1ANO)
        assert Subject.MATEMATICA in subjects
        assert Subject.BIOLOGIA in subjects
        assert Subject.FISICA in subjects
        assert Subject.QUIMICA in subjects
        assert Subject.FILOSOFIA in subjects
        assert Subject.SOCIOLOGIA in subjects

    def test_get_subjects_by_grade_level_eja(self):
        """Test subjects for adult education."""
        subjects = get_subjects_by_grade_level(GradeLevel.EJA_FUNDAMENTAL)
        assert Subject.MATEMATICA in subjects
        assert Subject.PORTUGUES in subjects
        assert Subject.EDUCACAO_FINANCEIRA in subjects
        assert Subject.EMPREENDEDORISMO in subjects
