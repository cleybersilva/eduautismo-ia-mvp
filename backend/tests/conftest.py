"""
Pytest configuration and shared fixtures for EduAutismo IA tests.

This file is automatically loaded by pytest and provides common fixtures
and configuration for all test modules.
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import get_db
from app.core.security import get_password_hash
from app.db.base import Base  # Use the correct Base
from app.main import app
from app.models.student import Student
from app.models.user import User

# Test database URL - use separate test database
# Use 'postgres' hostname when running inside Docker, 'localhost' otherwise
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", f"postgresql://eduautismo:eduautismo_dev_pass@{DB_HOST}:5432/eduautismo_test"
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, pool_pre_ping=True)

    # Import all models to ensure they're registered
    from app.models import activity, assessment, student, user  # noqa

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

    # Clean up all data before each test
    from app.models.activity import Activity
    from app.models.assessment import Assessment
    from app.models.student import Student
    from app.models.user import User

    session.query(Assessment).delete()
    session.query(Activity).delete()
    session.query(Student).delete()
    session.query(User).delete()
    session.commit()

    yield session

    # Rollback any remaining transactions
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
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user) -> dict:
    """Get authentication headers with valid token."""
    response = client.post("/api/v1/auth/login", data={"username": test_user.email, "password": "testpass123"})
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
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_activity(db_session, test_student, test_user):
    """Create test activity."""
    from app.models.activity import Activity

    activity = Activity(
        student_id=test_student.id,
        title="Atividade de Teste",
        description="Descrição da atividade de teste",
        activity_type="cognitive",
        difficulty="easy",
        duration_minutes=30,
        objectives=["Objetivo 1", "Objetivo 2"],
        materials=["Material 1", "Material 2"],
        instructions=["Instruções passo a passo"],  # Must be a list
        theme="matemática",
        generated_by_ai=True,
        created_by_id=test_user.id,  # Fixed: use created_by_id instead of teacher_id
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity
