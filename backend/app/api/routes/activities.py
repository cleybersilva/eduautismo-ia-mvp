"""
Activity API routes.

This module defines the FastAPI routes for activity operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse
)
from backend.app.services.activity_service import ActivityService


router = APIRouter(
    prefix="/activitys",
    tags=["activitys"]
)


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db)
) -> ActivityResponse:
    """
    Create a new activity.

    Args:
        activity_data: Activity creation data
        db: Database session

    Returns:
        Created activity object
    """
    return ActivityService.create(db, activity_data)


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
) -> ActivityResponse:
    """
    Get a activity by ID.

    Args:
        activity_id: Activity ID
        db: Database session

    Returns:
        Activity object

    Raises:
        HTTPException: If activity not found
    """
    activity = ActivityService.get(db, activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity not found"
        )
    return activity


@router.get("/", response_model=List[ActivityResponse])
def list_activitys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ActivityResponse]:
    """
    List activitys with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of activity objects
    """
    return ActivityService.get_multi(db, skip=skip, limit=limit)


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db)
) -> ActivityResponse:
    """
    Update a activity.

    Args:
        activity_id: Activity ID
        activity_data: Update data
        db: Database session

    Returns:
        Updated activity object

    Raises:
        HTTPException: If activity not found
    """
    activity = ActivityService.update(db, activity_id, activity_data)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity not found"
        )
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a activity.

    Args:
        activity_id: Activity ID
        db: Database session

    Raises:
        HTTPException: If activity not found
    """
    success = ActivityService.delete(db, activity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity not found"
        )
