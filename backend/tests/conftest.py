"""
Pytest configuration and shared fixtures for EduAutismo IA tests.

This file is automatically loaded by pytest and provides common fixtures
and configuration for all test modules.
"""

import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.core.database import get_db
from app.db.base import Base  # Use the correct Base
from app.models.user import User
from app.models.student import Student
from app.core.security import get_password_hash

# Test database URL - use separate test database
# Use 'postgres' hostname when running inside Docker, 'localhost' otherwise
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql://eduautismo:eduautismo_dev_pass@{DB_HOST}:5432/eduautismo_test"
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, pool_pre_ping=True)

    # Import all models to ensure they're registered
    from app.models import user, student, activity, assessment  # noqa

    # Drop all tables and recreate for fresh test environment
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup after all tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create database session for test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create FastAPI test client."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        role="teacher",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user) -> dict:
    """Get authentication headers with valid token."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_student(db_session, test_user) -> Student:
    """Create test student."""
    from datetime import date

    student = Student(
        name="Test Student",
        date_of_birth=date(2015, 6, 15),
        age=9,
        diagnosis="Transtorno do Espectro Autista - Nível 1",
        tea_level="level_1",
        interests=["matemática", "jogos"],
        learning_profile={"visual_learner": True},
        teacher_id=test_user.id,
        is_active=True
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student
