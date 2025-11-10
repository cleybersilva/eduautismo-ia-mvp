"""
Database Package - EduAutismo IA

Exports database session and base classes.
"""

from backend.app.db.base import Base, BaseModel, TimestampMixin, UUIDMixin
from backend.app.db.session import AsyncSessionLocal, engine, get_db, init_db, close_db

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "AsyncSessionLocal",
    "engine",
    "get_db",
    "init_db",
    "close_db",
]
