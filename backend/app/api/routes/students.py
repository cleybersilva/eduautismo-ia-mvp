"""
Student API routes.

This module defines the FastAPI routes for student operations.
"""

from typing import List
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.student_service import StudentService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> StudentResponse:
    """
    Create a new student.

    Args:
        student_data: Student creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created student object
    """
    teacher_id = UUID(current_user["user_id"])
    student = StudentService.create_student(db, student_data, teacher_id)
    return student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)) -> StudentResponse:
    """
    Get a student by ID.

    Args:
        student_id: Student ID
        db: Database session

    Returns:
        Student object

    Raises:
        HTTPException: If student not found
    """
    student = StudentService.get(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@router.get("/", response_model=List[StudentResponse])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[StudentResponse]:
    """
    List students with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of student objects
    """
    return StudentService.get_multi(db, skip=skip, limit=limit)


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)) -> StudentResponse:
    """
    Update a student.

    Args:
        student_id: Student ID
        student_data: Update data
        db: Database session

    Returns:
        Updated student object

    Raises:
        HTTPException: If student not found
    """
    student = StudentService.update(db, student_id, student_data)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a student.

    Args:
        student_id: Student ID
        db: Database session

    Raises:
        HTTPException: If student not found
    """
    success = StudentService.delete(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
