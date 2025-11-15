"""
Custom SQLAlchemy types for database portability.

Provides types that work across different database backends (PostgreSQL, SQLite, etc.).
"""

import json
import uuid
from typing import Any, List

from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY as PostgreSQL_ARRAY
from sqlalchemy.dialects.postgresql import JSONB as PostgreSQL_JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.types import JSON


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available,
    otherwise uses String(36) for portability with SQLite.

    Based on: https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load dialect-specific implementation."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        """Process value being sent to database."""
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return value

    def process_result_value(self, value, dialect):
        """Process value being received from database."""
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


class StringArray(TypeDecorator):
    """
    Platform-independent string array type.

    Uses PostgreSQL's ARRAY(String) when available,
    otherwise uses Text with JSON encoding for portability with SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load dialect-specific implementation."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_ARRAY(String))
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        """Process value being sent to database."""
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            # For non-PostgreSQL, serialize list to JSON
            return json.dumps(value) if value else "[]"

    def process_result_value(self, value, dialect):
        """Process value being received from database."""
        if value is None:
            return []
        elif dialect.name == "postgresql":
            return value if value else []
        else:
            # For non-PostgreSQL, deserialize JSON to list
            try:
                return json.loads(value) if value else []
            except (json.JSONDecodeError, TypeError):
                return []


class PortableJSON(TypeDecorator):
    """
    Platform-independent JSON type.

    Uses PostgreSQL's JSONB when available for better performance,
    otherwise uses standard JSON type for portability with SQLite.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load dialect-specific implementation."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_JSONB)
        else:
            return dialect.type_descriptor(JSON)
