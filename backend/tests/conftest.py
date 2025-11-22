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
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import get_password_hash
from app.db.base import Base  # Use the correct Base
from app.models.student import Student
from app.models.user import User

# Test database URL - use separate test database
# Use 'postgres' hostname when running inside Docker, 'localhost' otherwise
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

# Try PostgreSQL first, fallback to SQLite for local development
USE_SQLITE = os.getenv("USE_SQLITE_TESTS", "true").lower() == "true"

if USE_SQLITE:
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
    # Set DATABASE_URL for app initialization
    os.environ["DATABASE_URL"] = SQLALCHEMY_TEST_DATABASE_URL
else:
    SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL", f"postgresql://eduautismo:eduautismo_dev_pass@{DB_HOST}:5432/eduautismo_test"
    )
    os.environ["DATABASE_URL"] = SQLALCHEMY_TEST_DATABASE_URL

# Import app AFTER setting DATABASE_URL
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    if USE_SQLITE:
        # For SQLite :memory:, use StaticPool to ensure all connections use the same database
        engine = create_engine(
            SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    else:
        # For PostgreSQL, use normal pool with pre-ping
        engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, pool_pre_ping=True)

    # Import all models to ensure they're registered with Base.metadata
    from app.models.activity import Activity
    from app.models.assessment import Assessment
    from app.models.intervention_plan import InterventionPlan
    from app.models.observation import ProfessionalObservation
    from app.models.professional import Professional
    from app.models.socioemotional_indicator import SocialEmotionalIndicator
    from app.models.student import Student
    from app.models.user import User

    # noqa on unused imports
    _ = (User, Student, Activity, Assessment, Professional, ProfessionalObservation, InterventionPlan, SocialEmotionalIndicator)

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

    # Clean up all data before each test (wrapped in try-except for SQLite)
    try:
        from app.models.activity import Activity
        from app.models.assessment import Assessment
        from app.models.intervention_plan import InterventionPlan
        from app.models.observation import ProfessionalObservation
        from app.models.professional import Professional
        from app.models.socioemotional_indicator import SocialEmotionalIndicator
        from app.models.student import Student
        from app.models.user import User

        # Delete in order to respect foreign key constraints
        session.query(Assessment).delete()
        session.query(Activity).delete()
        session.query(SocialEmotionalIndicator).delete()
        session.query(ProfessionalObservation).delete()
        # Delete intervention plan professionals association first
        session.execute(InterventionPlan.__table__.delete())
        session.query(Professional).delete()
        session.query(Student).delete()
        session.query(User).delete()
        session.commit()
    except Exception:
        # If deletion fails (e.g., tables don't exist yet), just rollback
        session.rollback()

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
def test_student(client, auth_headers) -> dict:
    """Create test student via API and return JSON response."""
    student_data = {
        "name": "João Silva",
        "date_of_birth": "2015-03-15",
        "age": 9,
        "diagnosis": "TEA Nível 1",
        "tea_level": "level_1",
        "interests": ["dinossauros", "lego"],
    }
    response = client.post("/api/v1/students/", json=student_data, headers=auth_headers)
    assert response.status_code == 201, f"Failed to create student: {response.json()}"
    return response.json()


@pytest.fixture
def test_activity(client, auth_headers, test_student):
    """Create test activity via API and return JSON response."""
    activity_data = {
        "student_id": test_student["id"],
        "title": "Atividade de Teste",
        "description": "Descrição da atividade de teste",
        "activity_type": "cognitive",
        "difficulty": "easy",
        "duration_minutes": 30,
        "objectives": ["Objetivo 1", "Objetivo 2"],
        "materials": ["Material 1", "Material 2"],
        "instructions": ["Instruções passo a passo"],
        "theme": "matemática",
    }
    response = client.post("/api/v1/activities/", json=activity_data, headers=auth_headers)
    assert response.status_code == 201, f"Failed to create activity: {response.json()}"
    return response.json()
