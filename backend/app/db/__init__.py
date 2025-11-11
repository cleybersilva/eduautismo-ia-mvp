"""
Database Package - EduAutismo IA

Exports database session and base classes.
"""

from app.db.base import Base, BaseModel, TimestampMixin, UUIDMixin
from app.db.session import SessionLocal, engine, get_db, init_db, close_db

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "close_db",
]
