"""
Assessment API routes.

This module defines the FastAPI routes for assessment operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse
)
from app.services.assessment_service import AssessmentService


router = APIRouter(
    prefix="/assessments",
    tags=["assessments"]
)


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Create a new assessment.

    Args:
        assessment_data: Assessment creation data
        db: Database session

    Returns:
        Created assessment object
    """
    return AssessmentService.create(db, assessment_data)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Get a assessment by ID.

    Args:
        assessment_id: Assessment ID
        db: Database session

    Returns:
        Assessment object

    Raises:
        HTTPException: If assessment not found
    """
    assessment = AssessmentService.get(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment not found"
        )
    return assessment


@router.get("/", response_model=List[AssessmentResponse])
def list_assessments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[AssessmentResponse]:
    """
    List assessments with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of assessment objects
    """
    return AssessmentService.get_multi(db, skip=skip, limit=limit)


@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: int,
    assessment_data: AssessmentUpdate,
    db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Update a assessment.

    Args:
        assessment_id: Assessment ID
        assessment_data: Update data
        db: Database session

    Returns:
        Updated assessment object

    Raises:
        HTTPException: If assessment not found
    """
    assessment = AssessmentService.update(db, assessment_id, assessment_data)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment not found"
        )
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a assessment.

    Args:
        assessment_id: Assessment ID
        db: Database session

    Raises:
        HTTPException: If assessment not found
    """
    success = AssessmentService.delete(db, assessment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment not found"
        )
