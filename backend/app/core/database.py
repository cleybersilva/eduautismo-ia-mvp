"""
Configuração do banco de dados
"""

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Sync PostgreSQL (for compatibility)
engine = create_engine(
    (
        settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        if not settings.DATABASE_URL.startswith("postgresql+psycopg2")
        else settings.DATABASE_URL
    ),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async PostgreSQL
async_database_url = (
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    if not settings.DATABASE_URL.startswith("postgresql+asyncpg")
    else settings.DATABASE_URL
)
async_engine = create_async_engine(
    async_database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()


# Sync Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async Dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
