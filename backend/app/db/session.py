"""
Database Session Configuration - EduAutismo IA

Synchronous database session management with SQLAlchemy.
"""

from typing import Generator

from app.core.config import settings
from app.utils.logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

logger = get_logger(__name__)


# Create engine
engine = create_engine(
    (
        settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        if not settings.DATABASE_URL.startswith("postgresql+psycopg2")
        else settings.DATABASE_URL
    ),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,  # Disable pooling for tests
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Session: Database session

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            result = db.query(Item).all()
            return result
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database.

    Creates all tables defined in models.
    Use Alembic migrations for production.
    """
    from app.db.base import Base

    # Import all models to ensure they're registered
    from app.models import activity, assessment, student, user  # noqa

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def close_db() -> None:
    """Close database connections."""
    engine.dispose()
    logger.info("Database connections closed")
