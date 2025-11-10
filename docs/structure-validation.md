# Structure Validation Guide

## Overview

The EduAutismo IA project includes a comprehensive structure validation system that ensures your project maintains the correct directory and file organization. This system can automatically create missing files with templates, making it easier to maintain consistency across the codebase.

## Quick Start

```bash
# 1. Validate structure and generate report
python scripts/check_structure.py --report-only

# 2. Create all missing Priority 1 (Critical) files
python scripts/check_structure.py --create-missing --priority 1

# 3. Create all missing Priority 1 & 2 files
python scripts/check_structure.py --create-missing --priority 2

# 4. Run complete validation workflow
./scripts/validate_structure.sh
```

## Priority System

Files are classified into three priority levels:

### Priority 1: Critical (Must Have)
These are essential files without which the project cannot function:
- `__init__.py` files for all Python packages
- Package initialization files
- Core module markers

**Example:**
```bash
python scripts/check_structure.py --create-missing --priority 1
```

### Priority 2: Important (Should Have)
These files provide core functionality and are necessary for a complete application:
- Database models (Student, Activity, Assessment)
- Pydantic schemas for validation
- Business logic services
- API route handlers
- Test configuration (conftest.py)
- Authentication dependencies

**Example:**
```bash
python scripts/check_structure.py --create-missing --priority 2
```

### Priority 3: Optional (Nice to Have)
Configuration and quality-of-life files:
- `pytest.ini` - Test configuration
- `.coveragerc` - Code coverage settings
- Additional utilities

**Example:**
```bash
python scripts/check_structure.py --create-missing --priority 3
```

## Tools

### 1. check_structure.py

The main validation script with file generation capabilities.

#### Usage

```bash
python scripts/check_structure.py [OPTIONS]
```

#### Options

- `--verbose`, `-v` - Show detailed information about all checks
- `--create-missing` - Create missing files with templates
- `--priority N` - Maximum priority level to create (1-3)
- `--report-only` - Only report, don't create anything
- `--project-root PATH` - Path to project root (default: current directory)

#### Examples

```bash
# Just validate and report
python scripts/check_structure.py --report-only

# Create only critical files
python scripts/check_structure.py --create-missing --priority 1

# Create critical + important files with verbose output
python scripts/check_structure.py --create-missing --priority 2 --verbose

# Full validation with optional files
python scripts/check_structure.py --create-missing --priority 3
```

#### Output

The script provides:
- Directory completion percentage
- File completion percentage by priority
- Overall project completion percentage
- Detailed list of missing items
- Status indicator (Excellent/Good/Fair/Poor)

**Example Output:**
```
EduAutismo IA - Project Structure Validator
Project root: /path/to/project
Date: 2025-11-09 22:30:00

======================================================================
Project Structure Validation Summary
======================================================================

Directories:
  Present: 38/38 (100.0%)

Files:
  Present: 29/31 (93.5%)
  Missing: 2/31

  Missing by Priority:
    Priority 3 (Optional): 2 files

Overall Completion: 97.1%

Status: ✓ Excellent - Project structure is complete
======================================================================
```

### 2. validate_structure.sh

Complete validation workflow with multiple checks.

#### Usage

```bash
./scripts/validate_structure.sh [OPTIONS]
```

#### Options

- `--fix` - Automatically create missing files (Priority 1 by default)
- `--priority N` - Set priority level for creation (1-3)
- `--help`, `-h` - Show help message

#### Features

1. **Python Version Check** - Verifies Python 3 is installed
2. **Structure Validation** - Runs check_structure.py
3. **Package Structure Verification** - Checks for `__init__.py` files
4. **Critical Files Check** - Validates essential project files
5. **Syntax Validation** - Checks Python files for syntax errors
6. **Git Status** - Shows uncommitted changes if in a git repo

#### Examples

```bash
# Just validate (no changes)
./scripts/validate_structure.sh

# Create critical files automatically
./scripts/validate_structure.sh --fix

# Create critical + important files
./scripts/validate_structure.sh --fix --priority 2
```

## File Templates

When creating missing files, the system uses intelligent templates based on file type:

### Models (SQLAlchemy)

```python
"""
Student model for EduAutismo IA.

This module defines the database model for student.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base


class Student(Base):
    """Student database model."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # TODO: Add model-specific fields here
```

### Schemas (Pydantic)

```python
"""
Student Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    """Base schema for Student with shared attributes."""
    # TODO: Add base fields here
    pass


class StudentCreate(BaseModel):
    """Schema for creating a new student."""
    model_config = ConfigDict(from_attributes=True)
    # TODO: Add creation fields here
    pass


class StudentResponse(StudentInDB):
    """Schema for student API response."""
    model_config = ConfigDict(from_attributes=True)
```

### Services (Business Logic)

```python
"""
Student business logic service.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """Service class for Student business logic."""

    @staticmethod
    def create(db: Session, student_data: StudentCreate) -> Student:
        """Create a new student."""
        db_obj = Student(**student_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, student_id: int) -> Optional[Student]:
        """Get a student by ID."""
        return db.query(Student).filter(Student.id == student_id).first()

    # ... more methods
```

### Routes (FastAPI)

```python
"""
Student API routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from backend.app.services.student_service import StudentService


router = APIRouter(
    prefix="/students",
    tags=["students"]
)


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """Create a new student."""
    return StudentService.create(db, student_data)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """Get a student by ID."""
    student = StudentService.get(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

# ... more endpoints
```

### Tests

```python
"""
Unit tests for student_service.

This module contains unit tests for the student_service module.
"""

import pytest
from fastapi.testclient import TestClient


class TestStudentServiceUnit:
    """Test class for student_service unit tests."""

    def test_student_service_placeholder(self):
        """
        Placeholder test for student_service.

        TODO: Implement actual unit tests
        """
        # TODO: Add test implementation
        assert True  # Placeholder assertion
```

## Step-by-Step Validation Process

### Step 1: Check Current Structure

First, understand the current state of your project:

```bash
# See directory tree
tree -L 3 -I '__pycache__|*.pyc|venv|.git|node_modules'

# Or use find
find . -type f -name "*.py" | grep -E "(backend/app/|tests/)" | sort

# Run basic validation
python scripts/check_structure.py --report-only
```

### Step 2: Analyze the Report

Look at the output to understand:
- How many directories are present/missing
- How many files are present/missing by priority
- Overall completion percentage
- Specific missing items

### Step 3: Create Missing Files

Based on the report, create files incrementally:

```bash
# Start with critical files
python scripts/check_structure.py --create-missing --priority 1

# Verify creation
python scripts/check_structure.py --report-only

# Add important files
python scripts/check_structure.py --create-missing --priority 2

# Verify again
python scripts/check_structure.py --report-only
```

### Step 4: Verify Package Structure

Ensure all Python packages have `__init__.py`:

```bash
# Check all __init__.py files
find backend/app -name "__init__.py" -type f

# Should output all package init files
```

### Step 5: Validate Python Syntax

Check for syntax errors in created files:

```bash
# Check specific file
python -m py_compile backend/app/models/student.py

# Or use flake8
flake8 backend/app/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Step 6: Review and Customize

All created files contain TODO comments. Replace them with actual implementation:

1. **Models**: Add SQLAlchemy columns
2. **Schemas**: Add Pydantic fields
3. **Services**: Add business logic
4. **Routes**: Add endpoints
5. **Tests**: Add test cases

## Common Workflows

### New Project Setup

```bash
# 1. Create full structure
python scripts/check_structure.py --create-missing --priority 2

# 2. Verify
./scripts/validate_structure.sh

# 3. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Fixing Incomplete Structure

```bash
# 1. Check what's missing
python scripts/check_structure.py --report-only

# 2. Create missing files
python scripts/check_structure.py --create-missing --priority 2

# 3. Run full validation
./scripts/validate_structure.sh
```

### Adding New Features

When adding a new resource (e.g., "Teacher"):

```bash
# Current templates support: student, activity, assessment
# For new resources, create files manually following the same pattern

# Or modify check_structure.py to add new templates
```

## Integration with Development Workflow

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate structure before commit
python scripts/check_structure.py --report-only
exit $?
```

### CI/CD Integration

Add to GitHub Actions (`.github/workflows/validate.yml`):

```yaml
name: Validate Structure

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Validate structure
        run: python scripts/check_structure.py --report-only
```

### Make Task

Add to `Makefile`:

```makefile
.PHONY: validate
validate:
	@echo "Validating project structure..."
	@python scripts/check_structure.py --report-only

.PHONY: fix-structure
fix-structure:
	@echo "Creating missing files..."
	@python scripts/check_structure.py --create-missing --priority 2
```

## Troubleshooting

### Issue: Script not found

```bash
# Make sure you're in project root
pwd
# Should show: /path/to/eduautismo-ia-mvp

# Make script executable
chmod +x scripts/check_structure.py
chmod +x scripts/validate_structure.sh
```

### Issue: Permission denied

```bash
# Run with python explicitly
python3 scripts/check_structure.py

# Or fix permissions
chmod +x scripts/*.py scripts/*.sh
```

### Issue: Import errors in created files

The generated files may have import errors initially because:
1. Dependencies might not be installed
2. Referenced files might not exist yet

**Solutions:**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create missing dependencies
python ../scripts/check_structure.py --create-missing --priority 2

# Update imports in main.py or config.py as needed
```

### Issue: Syntax errors after creation

If files have syntax errors:
```bash
# Check specific file
python -m py_compile backend/app/models/student.py

# Fix the file manually
# The template provides a working structure, syntax errors likely come from manual edits
```

## Best Practices

1. **Start with Priority 1**: Always create critical files first
2. **Review TODOs**: Check all TODO comments in generated files
3. **Customize Templates**: Modify templates in `check_structure.py` to match your needs
4. **Regular Validation**: Run validation before commits
5. **Version Control**: Commit generated files immediately with clear messages
6. **Incremental Updates**: Add Priority 2 and 3 files as needed, not all at once
7. **Test Early**: Run tests after creating test files to ensure structure is correct

## File Reference

### Created by Priority 1
- All `__init__.py` files in:
  - `backend/app/`
  - `backend/app/api/`
  - `backend/app/core/`
  - `backend/app/models/`
  - `backend/app/services/`
  - `backend/app/schemas/`
  - `backend/app/utils/`
  - `backend/app/api/routes/`
  - `backend/app/api/dependencies/`
  - `backend/tests/`
  - `backend/tests/unit/`
  - `backend/tests/integration/`
  - `backend/tests/fixtures/`

### Created by Priority 2
- **Models**: `student.py`, `activity.py`, `assessment.py`
- **Schemas**: `student.py`, `activity.py`, `assessment.py`
- **Services**: `student_service.py`, `activity_service.py`, `assessment_service.py`
- **Routes**: `students.py`, `activities.py`, `assessments.py`
- **Tests**: `conftest.py`, `test_student_service.py`, `test_students_api.py`
- **Dependencies**: `auth.py`

### Created by Priority 3
- `backend/pytest.ini`
- `backend/.coveragerc`

## Advanced Usage

### Custom Templates

To add custom templates, edit `scripts/check_structure.py`:

```python
# In FileTemplates class, add new method
@staticmethod
def get_custom_template(name: str) -> str:
    return f'''"""Custom template for {name}."""
    # Your template here
    '''

# In _define_expected_files(), add file definition
FileDefinition(
    'path/to/file.py',
    2,  # Priority
    templates.get_custom_template('MyClass'),
    'Description of the file'
),
```

### Extending Validation

To add new validation checks:

```python
# In ProjectStructureValidator class
def validate_custom_rule(self):
    """Add custom validation logic."""
    # Your validation code here
    pass
```

## Exit Codes

The scripts use exit codes to indicate status:

- `0`: Success (≥ 95% completion)
- `1`: Warning (≥ 70% completion)
- `2`: Error (< 70% completion)

Use these in CI/CD:
```bash
python scripts/check_structure.py --report-only
if [ $? -eq 2 ]; then
    echo "Critical structure issues!"
    exit 1
fi
```

## Next Steps

After validating your structure:

1. **Configure Environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

2. **Set Up Database**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Install Dependencies**
   ```bash
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```

4. **Run Tests**
   ```bash
   pytest backend/tests/
   ```

5. **Start Development Servers**
   ```bash
   # Backend
   uvicorn backend.app.main:app --reload

   # Frontend
   cd frontend && npm run dev
   ```

## Support

For issues or questions:
- Check this documentation
- Review generated file templates
- Check `CLAUDE.md` for project-specific guidance
- Review `README.md` for general project info
