"""
Unit tests for common schemas.

Tests Pydantic validation for common/shared schemas.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from app.schemas.common import BaseResponseSchema, PaginatedResponse


class TestPaginatedResponse:
    """Tests for PaginatedResponse schema."""

    def test_paginated_response_create_method(self):
        """Test PaginatedResponse.create() factory method."""
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        total = 10
        skip = 0
        limit = 2

        response = PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)

        assert response.items == items
        assert response.total == total
        assert response.skip == skip
        assert response.limit == limit
        assert response.has_more is True  # skip + len(items) = 2 < 10

    def test_paginated_response_create_no_more_items(self):
        """Test PaginatedResponse.create() when there are no more items."""
        items = [{"id": 1}, {"id": 2}]
        total = 2
        skip = 0
        limit = 10

        response = PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)

        assert response.has_more is False  # skip + len(items) = 2 >= 2

    def test_paginated_response_create_with_offset(self):
        """Test PaginatedResponse.create() with offset."""
        items = [{"id": 3}, {"id": 4}]
        total = 10
        skip = 2
        limit = 2

        response = PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)

        assert response.skip == 2
        assert response.has_more is True  # skip + len(items) = 4 < 10

    def test_paginated_response_direct_creation(self):
        """Test direct PaginatedResponse creation."""
        response = PaginatedResponse(
            items=["item1", "item2"],
            total=5,
            skip=0,
            limit=2,
            has_more=True,
        )

        assert len(response.items) == 2
        assert response.total == 5
        assert response.has_more is True

    def test_paginated_response_empty_items(self):
        """Test PaginatedResponse with empty items list."""
        response = PaginatedResponse.create(items=[], total=0, skip=0, limit=10)

        assert response.items == []
        assert response.total == 0
        assert response.has_more is False

    def test_paginated_response_default_values(self):
        """Test PaginatedResponse.create() with default values."""
        items = ["item1"]

        response = PaginatedResponse.create(items=items, total=5)

        assert response.skip == 0  # default
        assert response.limit == 20  # default
        assert response.has_more is True  # 0 + 1 < 5
