"""
Unit tests for database base configuration.

Tests SQLAlchemy base model, mixins, and utility methods.
"""

import uuid
from datetime import datetime
from unittest.mock import Mock

from sqlalchemy import Column, String

from app.db.base import BaseModel


# Create test models for tablename generation testing
class TestModelSimple(BaseModel):
    """Simple test model using BaseModel."""

    __abstract__ = False
    name = Column(String(100))


class TestModelComplex(BaseModel):
    """Complex test model to test tablename generation."""

    __abstract__ = False
    description = Column(String(200))


class StudentAssessment(BaseModel):
    """Test model with multiple words to test tablename generation."""

    __abstract__ = False
    score = Column(String(50))


class Analysis(BaseModel):
    """Test model ending with 's' to test pluralization."""

    __abstract__ = False
    data = Column(String(100))


class Status(BaseModel):
    """Another test model ending with 's'."""

    __abstract__ = False
    value = Column(String(50))


class TestBaseModel:
    """Tests for BaseModel."""

    def test_tablename_simple_class(self):
        """Test automatic tablename generation for simple class."""
        assert TestModelSimple.__tablename__ == "test_model_simples"

    def test_tablename_complex_class(self):
        """Test automatic tablename generation for complex class."""
        assert TestModelComplex.__tablename__ == "test_model_complexs"

    def test_tablename_multiple_words(self):
        """Test tablename generation for multi-word class names."""
        assert StudentAssessment.__tablename__ == "student_assessments"

    def test_tablename_already_ends_with_s(self):
        """Test that models ending with 's' don't get double 's'."""
        # The implementation adds 's' only if not ending with 's'
        assert Analysis.__tablename__ == "analysis"

    def test_tablename_status_model(self):
        """Test another model ending with 's'."""
        assert Status.__tablename__ == "status"

    def test_tablename_camelcase_to_snake_case(self):
        """Test CamelCase to snake_case conversion."""
        # StudentAssessment -> student_assessment -> student_assessments
        tablename = StudentAssessment.__tablename__
        assert "_" in tablename
        assert tablename.islower()

    def test_to_dict_method(self):
        """Test to_dict() converts model to dictionary."""
        # Create a mock model instance
        model = TestModelSimple()
        model.id = uuid.uuid4()
        model.name = "Test Name"
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        # Mock the __table__ attribute
        mock_column_id = Mock()
        mock_column_id.name = "id"

        mock_column_name = Mock()
        mock_column_name.name = "name"

        mock_column_created = Mock()
        mock_column_created.name = "created_at"

        mock_column_updated = Mock()
        mock_column_updated.name = "updated_at"

        model.__table__ = Mock()
        model.__table__.columns = [
            mock_column_id,
            mock_column_name,
            mock_column_created,
            mock_column_updated,
        ]

        result = model.to_dict()

        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert result["name"] == "Test Name"
        assert isinstance(result["id"], uuid.UUID)

    def test_to_dict_with_multiple_fields(self):
        """Test that to_dict() includes all table columns."""
        model = TestModelComplex()
        model.id = uuid.uuid4()
        model.description = "Test Description"
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        # Mock the __table__ attribute
        mock_columns = []
        for field_name in ["id", "description", "created_at", "updated_at"]:
            mock_col = Mock()
            mock_col.name = field_name
            mock_columns.append(mock_col)

        model.__table__ = Mock()
        model.__table__.columns = mock_columns

        result = model.to_dict()

        assert len(result) == 4
        assert result["description"] == "Test Description"

    def test_repr_method(self):
        """Test __repr__() string representation."""
        model = TestModelSimple()
        test_uuid = uuid.uuid4()
        model.id = test_uuid

        repr_str = repr(model)

        assert "TestModelSimple" in repr_str
        assert "id=" in repr_str
        assert str(test_uuid) in repr_str

    def test_repr_format(self):
        """Test __repr__() format matches expected pattern."""
        model = TestModelComplex()
        test_uuid = uuid.uuid4()
        model.id = test_uuid

        repr_str = repr(model)

        assert repr_str.startswith("<TestModelComplex(id=")
        assert repr_str.endswith(")>")
        assert str(test_uuid) in repr_str

    def test_base_model_is_abstract(self):
        """Test that BaseModel itself is marked as abstract."""
        assert BaseModel.__abstract__ is True


class TestTablenameGeneration:
    """Tests for __tablename__ generation logic."""

    def test_two_word_class_name(self):
        """Test two word class names."""

        class UserProfile(BaseModel):
            __abstract__ = False
            bio = Column(String(200))

        assert UserProfile.__tablename__ == "user_profiles"

    def test_three_word_class_name(self):
        """Test three word class names."""

        class StudentProfileData(BaseModel):
            __abstract__ = False
            data = Column(String(100))

        assert StudentProfileData.__tablename__ == "student_profile_datas"

    def test_consecutive_capitals(self):
        """Test class names with consecutive capital letters."""

        class HTTPRequest(BaseModel):
            __abstract__ = False
            url = Column(String(200))

        # Converts to h_t_t_p_request -> h_t_t_p_requests
        assert "_" in HTTPRequest.__tablename__
        assert HTTPRequest.__tablename__.endswith("s")


class TestMixinsPresence:
    """Tests to verify mixins are properly integrated."""

    def test_base_model_has_uuid_field(self):
        """Test that BaseModel includes UUID primary key from UUIDMixin."""
        # Check that 'id' field definition exists in BaseModel
        assert hasattr(BaseModel, "id")

    def test_base_model_has_timestamp_fields(self):
        """Test that BaseModel includes timestamp fields from TimestampMixin."""
        # Check that timestamp fields exist
        assert hasattr(BaseModel, "created_at")
        assert hasattr(BaseModel, "updated_at")

    def test_test_model_inherits_mixin_fields(self):
        """Test that child models inherit mixin fields."""
        assert hasattr(TestModelSimple, "id")
        assert hasattr(TestModelSimple, "created_at")
        assert hasattr(TestModelSimple, "updated_at")
        assert hasattr(TestModelSimple, "name")
