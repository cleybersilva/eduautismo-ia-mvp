"""
Database Session Configuration - EduAutismo IA

Async database session management with SQLAlchemy.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.core.config import settings
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    poolclass=NullPool if settings.ENV == "test" else None,  # Disable pooling for tests
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database.

    Creates all tables defined in models.
    Use Alembic migrations for production.
    """
    from backend.app.db.base import Base

    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from backend.app.models import user, student, activity, assessment  # noqa

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
