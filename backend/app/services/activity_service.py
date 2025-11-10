"""
Activity business logic service.

This module contains the business logic for activity operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.activity import Activity
from backend.app.schemas.activity import ActivityCreate, ActivityUpdate


class ActivityService:
    """
    Service class for Activity business logic.

    This class handles all business logic operations for activity.
    """

    @staticmethod
    def create(db: Session, activity_data: ActivityCreate) -> Activity:
        """
        Create a new activity.

        Args:
            db: Database session
            activity_data: Activity creation data

        Returns:
            Created activity object
        """
        # TODO: Implement creation logic
        db_obj = Activity(**activity_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, activity_id: int) -> Optional[Activity]:
        """
        Get a activity by ID.

        Args:
            db: Database session
            activity_id: Activity ID

        Returns:
            Activity object or None if not found
        """
        return db.query(Activity).filter(Activity.id == activity_id).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Activity]:
        """
        Get multiple activitys.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of activity objects
        """
        return db.query(Activity).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, activity_id: int, activity_data: ActivityUpdate) -> Optional[Activity]:
        """
        Update a activity.

        Args:
            db: Database session
            activity_id: Activity ID
            activity_data: Update data

        Returns:
            Updated activity object or None if not found
        """
        db_obj = ActivityService.get(db, activity_id)
        if not db_obj:
            return None

        update_data = activity_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, activity_id: int) -> bool:
        """
        Delete a activity.

        Args:
            db: Database session
            activity_id: Activity ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = ActivityService.get(db, activity_id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True
