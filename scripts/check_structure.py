#!/usr/bin/env python3
"""
Project Structure Validator for EduAutismo IA MVP

This script validates the project structure against the expected layout
defined in the project documentation and can create missing files with templates.

Usage:
    python scripts/check_structure.py [OPTIONS]

Examples:
    # Just validate and report
    python scripts/check_structure.py --report-only

    # Create all missing Priority 1 (Critical) files
    python scripts/check_structure.py --create-missing --priority 1

    # Create all missing Priority 1 & 2 files
    python scripts/check_structure.py --create-missing --priority 2

    # Verbose output
    python scripts/check_structure.py --verbose

Options:
    --verbose, -v           Show detailed information about all checks
    --create-missing        Create missing files with templates
    --priority N            Only create files up to priority N (1=Critical, 2=Important, 3=Optional)
    --report-only           Only report, don't create anything
    --project-root PATH     Path to project root (default: current directory)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class FileDefinition:
    """Definition of an expected file with template"""
    path: str
    priority: int  # 1=Critical, 2=Important, 3=Optional
    template: str
    description: str


@dataclass
class ValidationResult:
    """Results of structure validation"""
    missing_dirs: List[str]
    missing_files: Dict[int, List[FileDefinition]]  # Priority -> Files
    present_dirs: List[str]
    present_files: List[str]
    created_files: List[str]
    created_dirs: List[str]


class FileTemplates:
    """File templates for different types of files"""

    @staticmethod
    def get_init_py() -> str:
        """Template for __init__.py files"""
        return '"""Package initialization."""\n'

    @staticmethod
    def get_model_template(name: str) -> str:
        """Template for SQLAlchemy models"""
        return f'''"""
{name.title()} model for EduAutismo IA.

This module defines the database model for {name}.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base


class {name.title()}(Base):
    """
    {name.title()} database model.

    Attributes:
        id: Primary key
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "{name.lower()}s"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # TODO: Add model-specific fields here

    def __repr__(self) -> str:
        return f"<{name.title()}(id={{self.id}})>"
'''

    @staticmethod
    def get_schema_template(name: str) -> str:
        """Template for Pydantic schemas"""
        return f'''"""
{name.title()} Pydantic schemas for request/response validation.

This module defines the Pydantic schemas for {name} API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class {name.title()}Base(BaseModel):
    """Base schema for {name.title()} with shared attributes."""

    # TODO: Add base fields here
    pass


class {name.title()}Create(BaseModel):
    """Schema for creating a new {name.lower()}."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add creation fields here
    pass


class {name.title()}Update(BaseModel):
    """Schema for updating an existing {name.lower()}."""

    model_config = ConfigDict(from_attributes=True)

    # TODO: Add update fields here
    pass


class {name.title()}InDB({name.title()}Base):
    """Schema for {name.lower()} as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class {name.title()}Response({name.title()}InDB):
    """Schema for {name.lower()} API response."""

    model_config = ConfigDict(from_attributes=True)
'''

    @staticmethod
    def get_service_template(name: str) -> str:
        """Template for service modules"""
        return f'''"""
{name.title()} business logic service.

This module contains the business logic for {name} operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.{name.lower()} import {name.title()}
from backend.app.schemas.{name.lower()} import {name.title()}Create, {name.title()}Update


class {name.title()}Service:
    """
    Service class for {name.title()} business logic.

    This class handles all business logic operations for {name}.
    """

    @staticmethod
    def create(db: Session, {name.lower()}_data: {name.title()}Create) -> {name.title()}:
        """
        Create a new {name.lower()}.

        Args:
            db: Database session
            {name.lower()}_data: {name.title()} creation data

        Returns:
            Created {name.lower()} object
        """
        # TODO: Implement creation logic
        db_obj = {name.title()}(**{name.lower()}_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, {name.lower()}_id: int) -> Optional[{name.title()}]:
        """
        Get a {name.lower()} by ID.

        Args:
            db: Database session
            {name.lower()}_id: {name.title()} ID

        Returns:
            {name.title()} object or None if not found
        """
        return db.query({name.title()}).filter({name.title()}.id == {name.lower()}_id).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[{name.title()}]:
        """
        Get multiple {name.lower()}s.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of {name.lower()} objects
        """
        return db.query({name.title()}).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, {name.lower()}_id: int, {name.lower()}_data: {name.title()}Update) -> Optional[{name.title()}]:
        """
        Update a {name.lower()}.

        Args:
            db: Database session
            {name.lower()}_id: {name.title()} ID
            {name.lower()}_data: Update data

        Returns:
            Updated {name.lower()} object or None if not found
        """
        db_obj = {name.title()}Service.get(db, {name.lower()}_id)
        if not db_obj:
            return None

        update_data = {name.lower()}_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, {name.lower()}_id: int) -> bool:
        """
        Delete a {name.lower()}.

        Args:
            db: Database session
            {name.lower()}_id: {name.title()} ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = {name.title()}Service.get(db, {name.lower()}_id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True
'''

    @staticmethod
    def get_route_template(name: str) -> str:
        """Template for FastAPI routes"""
        return f'''"""
{name.title()} API routes.

This module defines the FastAPI routes for {name} operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.{name.lower()} import (
    {name.title()}Create,
    {name.title()}Update,
    {name.title()}Response
)
from backend.app.services.{name.lower()}_service import {name.title()}Service


router = APIRouter(
    prefix="/{name.lower()}s",
    tags=["{name.lower()}s"]
)


@router.post("/", response_model={name.title()}Response, status_code=status.HTTP_201_CREATED)
def create_{name.lower()}(
    {name.lower()}_data: {name.title()}Create,
    db: Session = Depends(get_db)
) -> {name.title()}Response:
    """
    Create a new {name.lower()}.

    Args:
        {name.lower()}_data: {name.title()} creation data
        db: Database session

    Returns:
        Created {name.lower()} object
    """
    return {name.title()}Service.create(db, {name.lower()}_data)


@router.get("/{{{name.lower()}_id}}", response_model={name.title()}Response)
def get_{name.lower()}(
    {name.lower()}_id: int,
    db: Session = Depends(get_db)
) -> {name.title()}Response:
    """
    Get a {name.lower()} by ID.

    Args:
        {name.lower()}_id: {name.title()} ID
        db: Database session

    Returns:
        {name.title()} object

    Raises:
        HTTPException: If {name.lower()} not found
    """
    {name.lower()} = {name.title()}Service.get(db, {name.lower()}_id)
    if not {name.lower()}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name.title()} not found"
        )
    return {name.lower()}


@router.get("/", response_model=List[{name.title()}Response])
def list_{name.lower()}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[{name.title()}Response]:
    """
    List {name.lower()}s with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of {name.lower()} objects
    """
    return {name.title()}Service.get_multi(db, skip=skip, limit=limit)


@router.put("/{{{name.lower()}_id}}", response_model={name.title()}Response)
def update_{name.lower()}(
    {name.lower()}_id: int,
    {name.lower()}_data: {name.title()}Update,
    db: Session = Depends(get_db)
) -> {name.title()}Response:
    """
    Update a {name.lower()}.

    Args:
        {name.lower()}_id: {name.title()} ID
        {name.lower()}_data: Update data
        db: Database session

    Returns:
        Updated {name.lower()} object

    Raises:
        HTTPException: If {name.lower()} not found
    """
    {name.lower()} = {name.title()}Service.update(db, {name.lower()}_id, {name.lower()}_data)
    if not {name.lower()}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name.title()} not found"
        )
    return {name.lower()}


@router.delete("/{{{name.lower()}_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{name.lower()}(
    {name.lower()}_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a {name.lower()}.

    Args:
        {name.lower()}_id: {name.title()} ID
        db: Database session

    Raises:
        HTTPException: If {name.lower()} not found
    """
    success = {name.title()}Service.delete(db, {name.lower()}_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name.title()} not found"
        )
'''

    @staticmethod
    def get_test_template(name: str, test_type: str) -> str:
        """Template for test files"""
        return f'''"""
{test_type.title()} tests for {name}.

This module contains {test_type} tests for the {name} module.
"""

import pytest
from fastapi.testclient import TestClient


class Test{name.title()}{test_type.title()}:
    """Test class for {name} {test_type} tests."""

    def test_{name.lower()}_placeholder(self):
        """
        Placeholder test for {name}.

        TODO: Implement actual {test_type} tests
        """
        # TODO: Add test implementation
        assert True  # Placeholder assertion
'''

    @staticmethod
    def get_dependency_template() -> str:
        """Template for dependencies module"""
        return '''"""
FastAPI dependencies for authentication, database, and other shared functionality.

This module provides dependency injection functions for FastAPI routes.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.security import verify_token


security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # TODO: Implement token verification and user retrieval
    # user_id = verify_token(token)
    # user = get_user_by_id(db, user_id)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials"
    #     )
    # return user

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )
'''

    @staticmethod
    def get_conftest() -> str:
        """Template for pytest conftest.py"""
        return '''"""
Pytest configuration and shared fixtures for EduAutismo IA tests.

This file is automatically loaded by pytest and provides common fixtures
and configuration for all test modules.
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.main import app
from backend.app.core.database import Base, get_db


# Test database URL (use in-memory SQLite for tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.

    Yields:
        Database session for testing
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with overridden database dependency.

    Args:
        db: Test database session

    Yields:
        FastAPI test client
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "test_user": {
            "email": "test@example.com",
            "password": "testpassword123"
        }
    }
'''


class ProjectStructureValidator:
    """Validates and manages the EduAutismo IA project structure"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Expected directories (relative to project root)
        self.expected_dirs = {
            # Root level directories
            '.github',
            '.github/workflows',
            '.vscode',
            'docs',
            'scripts',
            'scripts/setup',
            'scripts/deployment',
            'scripts/backup',
            'scripts/database',
            'scripts/ml',
            'logs',

            # Backend structure
            'backend',
            'backend/app',
            'backend/app/api',
            'backend/app/api/routes',
            'backend/app/api/dependencies',
            'backend/app/core',
            'backend/app/models',
            'backend/app/services',
            'backend/app/utils',
            'backend/app/schemas',
            'backend/migrations',
            'backend/tests',
            'backend/tests/unit',
            'backend/tests/integration',
            'backend/tests/fixtures',

            # Frontend structure
            'frontend',
            'frontend/src',
            'frontend/src/components',
            'frontend/src/pages',
            'frontend/src/services',
            'frontend/src/styles',
            'frontend/src/utils',
            'frontend/public',

            # ML and Infrastructure
            'ml_models',
            'ml_models/behavioral_classifier',
            'ml_models/recommender',
            'terraform',
        }

        # Define expected files with priorities and templates
        self.expected_files = self._define_expected_files()

    def _define_expected_files(self) -> Dict[str, FileDefinition]:
        """Define all expected files with their properties"""
        templates = FileTemplates()
        files = {}

        # Priority 1: Critical files (must have)
        critical_files = [
            FileDefinition(
                'backend/app/__init__.py',
                1,
                templates.get_init_py(),
                'Backend app package initialization'
            ),
            FileDefinition(
                'backend/app/api/__init__.py',
                1,
                templates.get_init_py(),
                'API package initialization'
            ),
            FileDefinition(
                'backend/app/core/__init__.py',
                1,
                templates.get_init_py(),
                'Core package initialization'
            ),
            FileDefinition(
                'backend/app/models/__init__.py',
                1,
                templates.get_init_py(),
                'Models package initialization'
            ),
            FileDefinition(
                'backend/app/services/__init__.py',
                1,
                templates.get_init_py(),
                'Services package initialization'
            ),
            FileDefinition(
                'backend/app/schemas/__init__.py',
                1,
                templates.get_init_py(),
                'Schemas package initialization'
            ),
            FileDefinition(
                'backend/app/utils/__init__.py',
                1,
                templates.get_init_py(),
                'Utils package initialization'
            ),
            FileDefinition(
                'backend/app/api/routes/__init__.py',
                1,
                templates.get_init_py(),
                'Routes package initialization'
            ),
            FileDefinition(
                'backend/app/api/dependencies/__init__.py',
                1,
                templates.get_init_py(),
                'Dependencies package initialization'
            ),
            FileDefinition(
                'backend/tests/__init__.py',
                1,
                templates.get_init_py(),
                'Tests package initialization'
            ),
            FileDefinition(
                'backend/tests/unit/__init__.py',
                1,
                templates.get_init_py(),
                'Unit tests package initialization'
            ),
            FileDefinition(
                'backend/tests/integration/__init__.py',
                1,
                templates.get_init_py(),
                'Integration tests package initialization'
            ),
            FileDefinition(
                'backend/tests/fixtures/__init__.py',
                1,
                templates.get_init_py(),
                'Test fixtures package initialization'
            ),
        ]

        # Priority 2: Important files (should have)
        important_files = [
            FileDefinition(
                'backend/tests/conftest.py',
                2,
                templates.get_conftest(),
                'Pytest configuration and fixtures'
            ),
            FileDefinition(
                'backend/app/api/dependencies/auth.py',
                2,
                templates.get_dependency_template(),
                'Authentication dependencies'
            ),
            FileDefinition(
                'backend/app/models/student.py',
                2,
                templates.get_model_template('student'),
                'Student database model'
            ),
            FileDefinition(
                'backend/app/schemas/student.py',
                2,
                templates.get_schema_template('student'),
                'Student Pydantic schemas'
            ),
            FileDefinition(
                'backend/app/services/student_service.py',
                2,
                templates.get_service_template('student'),
                'Student business logic service'
            ),
            FileDefinition(
                'backend/app/api/routes/students.py',
                2,
                templates.get_route_template('student'),
                'Student API routes'
            ),
            FileDefinition(
                'backend/app/models/activity.py',
                2,
                templates.get_model_template('activity'),
                'Activity database model'
            ),
            FileDefinition(
                'backend/app/schemas/activity.py',
                2,
                templates.get_schema_template('activity'),
                'Activity Pydantic schemas'
            ),
            FileDefinition(
                'backend/app/services/activity_service.py',
                2,
                templates.get_service_template('activity'),
                'Activity business logic service'
            ),
            FileDefinition(
                'backend/app/api/routes/activities.py',
                2,
                templates.get_route_template('activity'),
                'Activity API routes'
            ),
            FileDefinition(
                'backend/app/models/assessment.py',
                2,
                templates.get_model_template('assessment'),
                'Assessment database model'
            ),
            FileDefinition(
                'backend/app/schemas/assessment.py',
                2,
                templates.get_schema_template('assessment'),
                'Assessment Pydantic schemas'
            ),
            FileDefinition(
                'backend/app/services/assessment_service.py',
                2,
                templates.get_service_template('assessment'),
                'Assessment business logic service'
            ),
            FileDefinition(
                'backend/app/api/routes/assessments.py',
                2,
                templates.get_route_template('assessment'),
                'Assessment API routes'
            ),
            FileDefinition(
                'backend/tests/unit/test_student_service.py',
                2,
                templates.get_test_template('student_service', 'unit'),
                'Student service unit tests'
            ),
            FileDefinition(
                'backend/tests/integration/test_students_api.py',
                2,
                templates.get_test_template('students_api', 'integration'),
                'Student API integration tests'
            ),
        ]

        # Priority 3: Optional files (nice to have)
        optional_files = [
            FileDefinition(
                'backend/pytest.ini',
                3,
                '[pytest]\ntestpaths = tests\npython_files = test_*.py\npython_classes = Test*\npython_functions = test_*\naddopts = -v --strict-markers\nmarkers =\n    unit: Unit tests\n    integration: Integration tests\n    slow: Slow running tests\n',
                'Pytest configuration file'
            ),
            FileDefinition(
                'backend/.coveragerc',
                3,
                '[run]\nsource = app\nomit =\n    */tests/*\n    */venv/*\n    */__init__.py\n\n[report]\nexclude_lines =\n    pragma: no cover\n    def __repr__\n    raise AssertionError\n    raise NotImplementedError\n    if __name__ == .__main__.:\n',
                'Code coverage configuration'
            ),
        ]

        # Combine all files into dictionary
        for file_def in critical_files + important_files + optional_files:
            files[file_def.path] = file_def

        return files

    def validate(self, verbose: bool = False) -> ValidationResult:
        """
        Validate the project structure

        Args:
            verbose: If True, print detailed information

        Returns:
            ValidationResult object with validation details
        """
        missing_dirs = []
        present_dirs = []
        missing_files: Dict[int, List[FileDefinition]] = {1: [], 2: [], 3: []}
        present_files = []

        # Check directories
        for dir_path in sorted(self.expected_dirs):
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                present_dirs.append(dir_path)
                if verbose:
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Directory: {dir_path}")
            else:
                missing_dirs.append(dir_path)
                if verbose:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Missing directory: {dir_path}")

        # Check files
        for file_path, file_def in sorted(self.expected_files.items()):
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                present_files.append(file_path)
                if verbose:
                    priority_str = f"P{file_def.priority}"
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} [{priority_str}] File: {file_path}")
            else:
                missing_files[file_def.priority].append(file_def)
                if verbose:
                    priority_str = f"P{file_def.priority}"
                    print(f"{Colors.FAIL}✗{Colors.ENDC} [{priority_str}] Missing file: {file_path}")

        return ValidationResult(
            missing_dirs=missing_dirs,
            missing_files=missing_files,
            present_dirs=present_dirs,
            present_files=present_files,
            created_files=[],
            created_dirs=[]
        )

    def create_missing_directories(self, missing_dirs: List[str], verbose: bool = False) -> List[str]:
        """
        Create missing directories

        Args:
            missing_dirs: List of directory paths to create
            verbose: If True, print detailed information

        Returns:
            List of created directory paths
        """
        created = []
        for dir_path in missing_dirs:
            full_path = self.project_root / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                created.append(dir_path)
                if verbose:
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Created directory: {dir_path}")
            except Exception as e:
                print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to create {dir_path}: {e}")

        return created

    def create_missing_files(
        self,
        missing_files: Dict[int, List[FileDefinition]],
        max_priority: int = 3,
        verbose: bool = False
    ) -> List[str]:
        """
        Create missing files with templates

        Args:
            missing_files: Dictionary of missing files by priority
            max_priority: Maximum priority to create (1-3)
            verbose: If True, print detailed information

        Returns:
            List of created file paths
        """
        created = []

        for priority in range(1, max_priority + 1):
            if priority not in missing_files:
                continue

            for file_def in missing_files[priority]:
                full_path = self.project_root / file_def.path

                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    # Write file with template
                    full_path.write_text(file_def.template, encoding='utf-8')
                    created.append(file_def.path)

                    if verbose:
                        priority_str = f"P{priority}"
                        print(f"{Colors.OKGREEN}✓{Colors.ENDC} [{priority_str}] Created: {file_def.path}")
                        print(f"  {Colors.OKCYAN}└─{Colors.ENDC} {file_def.description}")
                except Exception as e:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to create {file_def.path}: {e}")

        return created

    def print_summary(self, result: ValidationResult, max_priority: Optional[int] = None) -> None:
        """
        Print a summary of the validation results

        Args:
            result: ValidationResult object
            max_priority: If set, only show files up to this priority
        """
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}Project Structure Validation Summary{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        total_dirs = len(self.expected_dirs)
        total_files = len(self.expected_files)

        # Directories summary
        dirs_ok = len(result.present_dirs)
        dirs_missing = len(result.missing_dirs)
        dirs_percentage = (dirs_ok / total_dirs * 100) if total_dirs > 0 else 0

        print(f"{Colors.BOLD}Directories:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}Present:{Colors.ENDC} {dirs_ok}/{total_dirs} ({dirs_percentage:.1f}%)")
        if dirs_missing > 0:
            print(f"  {Colors.FAIL}Missing:{Colors.ENDC} {dirs_missing}/{total_dirs}")

        # Files summary by priority
        print(f"\n{Colors.BOLD}Files:{Colors.ENDC}")
        files_ok = len(result.present_files)
        total_missing = sum(len(files) for files in result.missing_files.values())
        files_percentage = (files_ok / total_files * 100) if total_files > 0 else 0

        print(f"  {Colors.OKGREEN}Present:{Colors.ENDC} {files_ok}/{total_files} ({files_percentage:.1f}%)")

        if total_missing > 0:
            print(f"  {Colors.FAIL}Missing:{Colors.ENDC} {total_missing}/{total_files}")
            print(f"\n  {Colors.BOLD}Missing by Priority:{Colors.ENDC}")
            for priority in [1, 2, 3]:
                if priority in result.missing_files and result.missing_files[priority]:
                    count = len(result.missing_files[priority])
                    priority_names = {1: "Critical", 2: "Important", 3: "Optional"}
                    color = Colors.FAIL if priority == 1 else Colors.WARNING
                    print(f"    {color}Priority {priority} ({priority_names[priority]}):{Colors.ENDC} {count} files")

        # Overall status
        overall_percentage = ((dirs_ok + files_ok) / (total_dirs + total_files) * 100)
        print(f"\n{Colors.BOLD}Overall Completion:{Colors.ENDC} {overall_percentage:.1f}%")

        # Created items (if any)
        if result.created_dirs:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}Created Directories ({len(result.created_dirs)}):{Colors.ENDC}")
            for dir_path in result.created_dirs[:10]:  # Show first 10
                print(f"  {Colors.OKGREEN}+{Colors.ENDC} {dir_path}")
            if len(result.created_dirs) > 10:
                print(f"  {Colors.OKCYAN}... and {len(result.created_dirs) - 10} more{Colors.ENDC}")

        if result.created_files:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}Created Files ({len(result.created_files)}):{Colors.ENDC}")
            for file_path in result.created_files[:10]:  # Show first 10
                print(f"  {Colors.OKGREEN}+{Colors.ENDC} {file_path}")
            if len(result.created_files) > 10:
                print(f"  {Colors.OKCYAN}... and {len(result.created_files) - 10} more{Colors.ENDC}")

        # Detailed missing items (only if requested priority)
        if max_priority is not None and total_missing > 0:
            print(f"\n{Colors.BOLD}Missing Files (Priority <= {max_priority}):{Colors.ENDC}")
            for priority in range(1, max_priority + 1):
                if priority not in result.missing_files or not result.missing_files[priority]:
                    continue

                priority_names = {1: "Critical", 2: "Important", 3: "Optional"}
                color = Colors.FAIL if priority == 1 else Colors.WARNING
                print(f"\n  {color}{Colors.BOLD}Priority {priority} - {priority_names[priority]}:{Colors.ENDC}")

                for file_def in result.missing_files[priority][:10]:
                    print(f"    {color}•{Colors.ENDC} {file_def.path}")
                    print(f"      {Colors.OKCYAN}└─{Colors.ENDC} {file_def.description}")

                if len(result.missing_files[priority]) > 10:
                    remaining = len(result.missing_files[priority]) - 10
                    print(f"    {Colors.OKCYAN}... and {remaining} more{Colors.ENDC}")

        # Status indicator
        print(f"\n{Colors.BOLD}Status:{Colors.ENDC} ", end="")
        if overall_percentage >= 95:
            print(f"{Colors.OKGREEN}✓ Excellent - Project structure is complete{Colors.ENDC}")
        elif overall_percentage >= 80:
            print(f"{Colors.OKGREEN}✓ Good - Project structure is well-formed{Colors.ENDC}")
        elif overall_percentage >= 60:
            print(f"{Colors.WARNING}⚠ Fair - Some components are missing{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ Poor - Major structural issues detected{Colors.ENDC}")

        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate and manage EduAutismo IA project structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Just validate and report
  python scripts/check_structure.py --report-only

  # Create all missing Priority 1 (Critical) files
  python scripts/check_structure.py --create-missing --priority 1

  # Create all missing Priority 1 & 2 files
  python scripts/check_structure.py --create-missing --priority 2

  # Verbose output
  python scripts/check_structure.py --verbose
        """
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information about all checks'
    )
    parser.add_argument(
        '--create-missing',
        action='store_true',
        help='Create missing files with templates'
    )
    parser.add_argument(
        '--priority',
        type=int,
        choices=[1, 2, 3],
        default=3,
        help='Maximum priority level to create (1=Critical, 2=Important, 3=Optional)'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only report, do not create anything'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Path to project root (default: current directory)'
    )

    args = parser.parse_args()

    # Get project root
    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"{Colors.FAIL}Error: Project root does not exist: {project_root}{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.BOLD}EduAutismo IA - Project Structure Validator{Colors.ENDC}")
    print(f"Project root: {project_root}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create validator and run validation
    validator = ProjectStructureValidator(project_root)
    result = validator.validate(verbose=args.verbose and not args.report_only)

    # Create missing items if requested
    if args.create_missing and not args.report_only:
        print(f"\n{Colors.BOLD}Creating missing structure...{Colors.ENDC}\n")

        # Create directories first
        if result.missing_dirs:
            print(f"{Colors.OKCYAN}Creating directories...{Colors.ENDC}")
            result.created_dirs = validator.create_missing_directories(
                result.missing_dirs,
                verbose=args.verbose
            )

        # Create files
        total_to_create = sum(
            len(files) for priority, files in result.missing_files.items()
            if priority <= args.priority
        )

        if total_to_create > 0:
            priority_names = {1: "Critical", 2: "Critical & Important", 3: "All"}
            print(f"\n{Colors.OKCYAN}Creating {priority_names.get(args.priority, 'selected')} files (Priority <= {args.priority})...{Colors.ENDC}")
            result.created_files = validator.create_missing_files(
                result.missing_files,
                max_priority=args.priority,
                verbose=args.verbose
            )

        # Re-validate to show updated status
        print(f"\n{Colors.BOLD}Re-validating structure...{Colors.ENDC}")
        result = validator.validate(verbose=False)

    # Print summary
    validator.print_summary(
        result,
        max_priority=args.priority if (args.create_missing or args.verbose) else None
    )

    # Recommendations
    if not args.report_only and not args.create_missing:
        total_missing_critical = len(result.missing_files.get(1, []))
        total_missing_important = len(result.missing_files.get(2, []))

        if total_missing_critical > 0:
            print(f"{Colors.BOLD}Recommendations:{Colors.ENDC}")
            print(f"  {Colors.FAIL}•{Colors.ENDC} {total_missing_critical} critical files are missing")
            print(f"    Run: {Colors.OKCYAN}python scripts/check_structure.py --create-missing --priority 1{Colors.ENDC}")
        elif total_missing_important > 0:
            print(f"{Colors.BOLD}Recommendations:{Colors.ENDC}")
            print(f"  {Colors.WARNING}•{Colors.ENDC} {total_missing_important} important files are missing")
            print(f"    Run: {Colors.OKCYAN}python scripts/check_structure.py --create-missing --priority 2{Colors.ENDC}")
        print()

    # Exit code based on results
    # 0 = success (>= 95%)
    # 1 = warning (>= 70%)
    # 2 = error (< 70%)
    total = len(validator.expected_dirs) + len(validator.expected_files)
    present = len(result.present_dirs) + len(result.present_files)
    percentage = (present / total * 100) if total > 0 else 0

    if percentage >= 95:
        sys.exit(0)
    elif percentage >= 70:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
