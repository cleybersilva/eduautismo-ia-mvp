"""
Assessment API routes (Sync Version).

This module defines the FastAPI routes for assessment operations.
"""

from typing import List, Optional
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import (ActivityNotFoundError,
                                 AssessmentNotFoundError,
                                 PermissionDeniedError, StudentNotFoundError)
from app.schemas.assessment import (AssessmentCreate, AssessmentResponse,
                                    AssessmentUpdate)
from app.services.assessment_service import AssessmentService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Create a new assessment.

    Args:
        assessment_data: Assessment creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created assessment object

    Raises:
        HTTPException: If validation fails or resources not found
    """
    try:
        teacher_id = UUID(current_user["user_id"])
        assessment = AssessmentService.create_assessment(db=db, assessment_data=assessment_data, teacher_id=teacher_id)
        return assessment
    except ActivityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: UUID, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Get an assessment by ID.

    Args:
        assessment_id: Assessment UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Assessment object

    Raises:
        HTTPException: If assessment not found
    """
    try:
        teacher_id = UUID(current_user["user_id"])
        assessment = AssessmentService.get_assessment(db=db, assessment_id=assessment_id, teacher_id=teacher_id)
        return assessment
    except AssessmentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to view this assessment"
        )


@router.get("/student/{student_id}", response_model=List[AssessmentResponse])
def list_assessments_by_student(
    student_id: UUID,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AssessmentResponse]:
    """
    List assessments for a specific student.

    Args:
        student_id: Student UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of assessment objects
    """
    assessments, _ = AssessmentService.list_assessments(db=db, student_id=student_id, skip=skip, limit=limit)
    return assessments


@router.get("/", response_model=List[AssessmentResponse])
def list_assessments(
    student_id: Optional[UUID] = Query(None),
    activity_id: Optional[UUID] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AssessmentResponse]:
    """
    List assessments with pagination and filters.

    Args:
        student_id: Optional filter by student
        activity_id: Optional filter by activity
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of assessment objects
    """
    teacher_id = UUID(current_user["user_id"])
    assessments, _ = AssessmentService.list_assessments(
        db=db, student_id=student_id, activity_id=activity_id, teacher_id=teacher_id, skip=skip, limit=limit
    )
    return assessments


@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: UUID,
    assessment_data: AssessmentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    """
    Update an assessment.

    Args:
        assessment_id: Assessment UUID
        assessment_data: Update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated assessment object

    Raises:
        HTTPException: If assessment not found or permission denied
    """
    try:
        teacher_id = UUID(current_user["user_id"])
        assessment = AssessmentService.update_assessment(
            db=db, assessment_id=assessment_id, assessment_data=assessment_data, teacher_id=teacher_id
        )
        return assessment
    except AssessmentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to update this assessment"
        )


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: UUID, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    """
    Delete an assessment.

    Args:
        assessment_id: Assessment UUID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If assessment not found or permission denied
    """
    try:
        teacher_id = UUID(current_user["user_id"])
        AssessmentService.delete_assessment(db=db, assessment_id=assessment_id, teacher_id=teacher_id)
    except AssessmentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this assessment"
        )
