"""
Pytest configuration and shared fixtures for EduAutismo IA tests.

This file is automatically loaded by pytest and provides common fixtures
and configuration for all test modules.
"""

import pytest
from typing import Generator


@pytest.fixture
def sample_fixture():
    """Example fixture - replace with actual fixtures as needed."""
    return {"example": "data"}


# Add more shared fixtures here as your test suite grows
