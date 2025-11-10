# 🤖 AI Assistant Guide - EduAutismo IA

> **Versão**: 1.0.0  
> **Última Atualização**: 2025-01-15  
> **Autor**: Cleyber Silva  
> **Projeto**: TCC MBA IA & Big Data - USP

---

## 📋 Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Arquitetura e Stack Tecnológico](#2-arquitetura-e-stack-tecnológico)
3. [Estrutura de Código](#3-estrutura-de-código)
4. [Padrões e Convenções](#4-padrões-e-convenções)
5. [Guia de Implementação](#5-guia-de-implementação)
6. [Exemplos de Código](#6-exemplos-de-código)
7. [Testes e Validação](#7-testes-e-validação)
8. [Deploy e DevOps](#8-deploy-e-devops)
9. [Troubleshooting](#9-troubleshooting)
10. [Referências Rápidas](#10-referências-rápidas)

---

## 1. Visão Geral do Projeto

### 1.1 Contexto

**EduAutismo IA** é uma plataforma de apoio pedagógico para professores da rede pública que trabalham com alunos do Transtorno do Espectro Autista (TEA).

**Objetivo Principal**: Automatizar criação de atividades pedagógicas personalizadas usando IA (GPT-4) baseadas em perfis cognitivos e sensoriais individuais.

### 1.2 Stakeholders

- **Usuários Primários**: Professores de escolas públicas
- **Beneficiários**: Alunos com TEA (6-18 anos)
- **Instituição**: ICMC - USP
- **Contexto**: TCC de MBA em IA e Big Data

### 1.3 Requisitos Funcionais Core
```yaml
RF01_Gestão_Alunos:
  Descrição: CRUD completo de alunos com perfis
  Prioridade: ALTA
  Status: MVP
  
RF02_Avaliações_Comportamentais:
  Descrição: Aplicação de instrumentos CARS, AQ, SPM
  Prioridade: ALTA
  Status: MVP
  
RF03_Geração_Atividades_IA:
  Descrição: Gerar atividades personalizadas via GPT-4
  Prioridade: CRÍTICA
  Status: MVP
  
RF04_Classificação_ML:
  Descrição: Predizer perfil comportamental com ML
  Prioridade: MÉDIA
  Status: MVP
  
RF05_Sistema_Recomendação:
  Descrição: Recomendar atividades baseado em histórico
  Prioridade: MÉDIA
  Status: MVP
  
RF06_Dashboards_Relatórios:
  Descrição: Visualizar evolução e gerar relatórios
  Prioridade: MÉDIA
  Status: MVP
```

### 1.4 Requisitos Não Funcionais
```yaml
RNF01_Performance:
  - API: Latência P95 < 2s
  - Geração de atividade: < 30s
  - ML inference: < 500ms
  
RNF02_Escalabilidade:
  - Suportar 1.000-5.000 alunos ativos
  - 100 requisições/minuto
  - Auto-scaling 2-10 tasks
  
RNF03_Segurança:
  - LGPD compliant
  - Criptografia at rest e in transit
  - Anonimização de dados
  - JWT authentication
  
RNF04_Disponibilidade:
  - SLA: 99.5% uptime
  - RTO: 4 horas
  - RPO: 1 hora
  
RNF05_Manutenibilidade:
  - Cobertura testes: >80%
  - Documentação completa
  - Código seguindo PEP 8
```

---

## 2. Arquitetura e Stack Tecnológico

### 2.1 Arquitetura High-Level
```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                         │
│  ┌──────────────┐              ┌──────────────┐         │
│  │  Streamlit   │              │   REST API   │         │
│  │  Web UI      │◄────────────►│   Docs       │         │
│  └──────────────┘              └──────────────┘         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                     │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│  │  │Student  │  │Activity │  │Assessment│          │   │
│  │  │Service  │  │Service  │  │Service   │          │   │
│  │  └────┬────┘  └────┬────┘  └────┬─────┘          │   │
│  │       │            │            │                 │   │
│  │       └────────────┼────────────┘                 │   │
│  │                    │                              │   │
│  │  ┌─────────────────▼─────────────────┐           │   │
│  │  │        Business Logic              │           │   │
│  │  │  • Validation                      │           │   │
│  │  │  • Authorization                   │           │   │
│  │  │  • Orchestration                   │           │   │
│  │  └────────────────────────────────────┘           │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  DocumentDB  │  │      S3      │
│    (RDS)     │  │  (MongoDB)   │  │   Storage    │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  OpenAI      │  │  Datadog     │  │   AWS KMS    │  │
│  │  GPT-4       │  │  Monitoring  │  │  Encryption  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Stack Detalhado
```python
# Backend Core
PYTHON_VERSION = "3.11+"
FRAMEWORK = "FastAPI 0.104+"
ORM = "SQLAlchemy 2.0+"
VALIDATION = "Pydantic V2"
AUTHENTICATION = "JWT (python-jose)"
ASYNC_SUPPORT = "asyncio, aiohttp"

# Databases
RELATIONAL_DB = {
    "engine": "PostgreSQL 15.4",
    "provider": "AWS RDS",
    "purpose": "Structured data (students, assessments, activities)"
}

DOCUMENT_DB = {
    "engine": "MongoDB 5.0",
    "provider": "AWS DocumentDB",
    "purpose": "Logs, analytics, semi-structured data"
}

CACHE = {
    "engine": "Redis 7.2",
    "provider": "AWS ElastiCache / Local",
    "purpose": "Session cache, API cache"
}

# AI/ML Stack
NLP = {
    "provider": "OpenAI",
    "model": "GPT-4",
    "use_cases": ["Activity generation", "Content adaptation"]
}

ML_FRAMEWORK = {
    "library": "scikit-learn 1.3+",
    "models": ["RandomForest", "GradientBoosting"],
    "use_cases": ["Behavioral classification", "Risk prediction"]
}

DATA_PROCESSING = [
    "pandas 2.1+",
    "numpy 1.25+",
    "scipy 1.11+"
]

# Infrastructure
CLOUD = "AWS"
CONTAINER = "Docker + ECS Fargate"
IaC = "Terraform 1.5+"
CI_CD = "GitHub Actions"
MONITORING = "Datadog (APM, Logs, Metrics)"
```

### 2.3 Diagrama de Componentes
```
┌─────────────────────────────────────────────────────────────┐
│                    src/                                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  api/                                              │     │
│  │  ├── routes/           # Endpoints REST            │     │
│  │  │   ├── students.py   # /api/v1/students         │     │
│  │  │   ├── activities.py # /api/v1/activities       │     │
│  │  │   ├── assessments.py# /api/v1/assessments      │     │
│  │  │   └── auth.py       # /api/v1/auth             │     │
│  │  ├── dependencies/     # FastAPI dependencies      │     │
│  │  └── main.py           # FastAPI app               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  services/                                          │     │
│  │  ├── student_service.py      # Business logic     │     │
│  │  ├── activity_service.py     # Activity CRUD      │     │
│  │  ├── assessment_service.py   # Assessment logic   │     │
│  │  ├── nlp_service.py          # OpenAI integration │     │
│  │  ├── ml_service.py           # ML predictions     │     │
│  │  └── recommendation_service.py # Recommendations  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  models/                                            │     │
│  │  ├── database/         # SQLAlchemy models         │     │
│  │  │   ├── student.py                                │     │
│  │  │   ├── activity.py                               │     │
│  │  │   └── assessment.py                             │     │
│  │  └── ml/               # ML models                 │     │
│  │      ├── behavioral_classifier.py                  │     │
│  │      └── activity_recommender.py                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  schemas/              # Pydantic schemas          │     │
│  │  ├── student.py                                    │     │
│  │  ├── activity.py                                   │     │
│  │  └── assessment.py                                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  core/                 # Core utilities            │     │
│  │  ├── config.py         # Settings                  │     │
│  │  ├── database.py       # DB connection             │     │
│  │  ├── security.py       # Auth, encryption          │     │
│  │  └── exceptions.py     # Custom exceptions         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  utils/                # Helper functions          │     │
│  │  ├── logger.py                                     │     │
│  │  ├── validators.py                                 │     │
│  │  └── helpers.py                                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Estrutura de Código

### 3.1 Diretórios Principais
```bash
eduautismo-ia/
├── .github/
│   └── workflows/              # CI/CD pipelines
│       ├── test.yml            # Run tests on PR
│       ├── deploy-staging.yml  # Deploy to staging
│       └── deploy-prod.yml     # Deploy to production
│
├── docs/                       # Documentation
│   ├── api/                    # API documentation
│   ├── architecture/           # Architecture docs
│   └── guides/                 # User guides
│
├── ml_models/                  # Trained ML models
│   ├── behavioral_classifier/
│   │   ├── model.pkl
│   │   ├── scaler.pkl
│   │   └── metadata.json
│   └── recommender/
│       ├── model.pkl
│       └── metadata.json
│
├── scripts/                    # Automation scripts
│   ├── train_behavioral_model.py
│   ├── train_recommender.py
│   ├── seed_database.py
│   ├── backup.sh
│   ├── deploy.sh
│   └── generate_reports.py
│
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── students.py
│   │   │   ├── activities.py
│   │   │   ├── assessments.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── database.py
│   │   └── main.py
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── database.py         # DB sessions
│   │   ├── security.py         # Auth, JWT
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── models/
│   │   ├── database/           # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── student.py
│   │   │   ├── activity.py
│   │   │   ├── assessment.py
│   │   │   └── user.py
│   │   └── ml/                 # ML models
│   │       ├── __init__.py
│   │       ├── base_model.py
│   │       ├── behavioral_classifier.py
│   │       └── activity_recommender.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── activity.py
│   │   ├── assessment.py
│   │   ├── auth.py
│   │   └── common.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── student_service.py
│   │   ├── activity_service.py
│   │   ├── assessment_service.py
│   │   ├── nlp_service.py
│   │   ├── ml_service.py
│   │   └── recommendation_service.py
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── constants.py
│   │
│   └── web/                    # Streamlit UI
│       ├── app.py              # Main app
│       ├── pages/
│       │   ├── students.py
│       │   ├── activities.py
│       │   └── reports.py
│       └── components/
│           ├── sidebar.py
│           └── charts.py
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── vpc.tf
│   ├── ecs.tf
│   ├── rds.tf
│   └── modules/
│       ├── networking/
│       ├── compute/
│       └── storage/
│
├── tests/                      # Tests
│   ├── unit/
│   │   ├── test_student_service.py
│   │   ├── test_activity_service.py
│   │   └── test_ml_models.py
│   ├── integration/
│   │   ├── test_api_students.py
│   │   └── test_api_activities.py
│   └── fixtures/
│       ├── __init__.py
│       └── sample_data.py
│
├── .env.example                # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml     # Pre-commit hooks
├── alembic.ini                 # Database migrations config
├── docker-compose.yml          # Local development
├── Dockerfile.api              # API container
├── Dockerfile.web              # Web UI container
├── pyproject.toml              # Poetry config
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Dev dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Project README
└── CLAUDE.md                   # This file
```

### 3.2 Módulos Principais

#### 3.2.1 API Routes
```python
# src/api/routes/students.py
"""
Student management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.api.dependencies.database import get_db
from src.api.dependencies.auth import get_current_user
from src.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from src.services.student_service import StudentService

router = APIRouter(prefix="/api/v1/students", tags=["students"])

@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new student"""
    service = StudentService(db)
    return service.create(student, created_by=current_user["sub"])

@router.get("/", response_model=List[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all students"""
    service = StudentService(db)
    return service.list(skip=skip, limit=limit)

# ... outros endpoints
```

#### 3.2.2 Services
```python
# src/services/student_service.py
"""
Student business logic
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.models.database.student import Student
from src.schemas.student import StudentCreate, StudentUpdate
from src.core.exceptions import StudentNotFoundError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class StudentService:
    """Service for student operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, student_data: StudentCreate, created_by: str) -> Student:
        """Create a new student"""
        student = Student(
            **student_data.dict(),
            created_by=created_by
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        
        logger.info(f"Student created: {student.id}")
        return student
    
    def get_by_id(self, student_id: UUID) -> Optional[Student]:
        """Get student by ID"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise StudentNotFoundError(f"Student {student_id} not found")
        return student
    
    def list(self, skip: int = 0, limit: int = 100) -> List[Student]:
        """List all students"""
        return self.db.query(Student).offset(skip).limit(limit).all()
    
    # ... outros métodos
```

#### 3.2.3 Models
```python
# src/models/database/student.py
"""
Student database model
"""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from src.models.database.base import Base

class DiagnosisType(str, enum.Enum):
    AUTISMO_LEVE = "autismo_leve"
    AUTISMO_MODERADO = "autismo_moderado"
    AUTISMO_SEVERO = "autismo_severo"
    SEM_DIAGNOSTICO = "sem_diagnostico"

class Student(Base):
    """Student model"""
    
    __tablename__ = "students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymous_code = Column(String(20), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    grade_level = Column(String(50), nullable=False)
    diagnosis = Column(Enum(DiagnosisType), nullable=True)
    
    # Perfis armazenados como JSON
    cognitive_profile = Column(JSON, nullable=True)
    sensory_profile = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(String(255), nullable=False)  # Hash do professor
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Student(id={self.id}, code={self.anonymous_code}, age={self.age})>"
```

#### 3.2.4 Schemas
```python
# src/schemas/student.py
"""
Student Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

class CognitiveProfile(BaseModel):
    """Cognitive profile schema"""
    memory: int = Field(..., ge=1, le=10)
    attention: int = Field(..., ge=1, le=10)
    processing_speed: int = Field(..., ge=1, le=10)
    executive_function: int = Field(..., ge=1, le=10)
    language: int = Field(..., ge=1, le=10)
    visual_spatial: int = Field(..., ge=1, le=10)

class SensoryProfile(BaseModel):
    """Sensory profile schema"""
    visual: int = Field(..., ge=0, le=3)
    auditory: int = Field(..., ge=0, le=3)
    tactile: int = Field(..., ge=0, le=3)
    vestibular: int = Field(..., ge=0, le=3)
    proprioceptive: int = Field(..., ge=0, le=3)

class StudentCreate(BaseModel):
    """Schema for creating student"""
    age: int = Field(..., ge=6, le=18)
    grade_level: str
    diagnosis: Optional[str] = None
    cognitive_profile: Optional[CognitiveProfile] = None
    sensory_profile: Optional[SensoryProfile] = None
    
    @validator('grade_level')
    def validate_grade_level(cls, v):
        valid_levels = [
            'fundamental_1_1ano', 'fundamental_1_2ano', 'fundamental_1_3ano',
            'fundamental_1_4ano', 'fundamental_1_5ano', 'fundamental_2_6ano',
            'fundamental_2_7ano', 'fundamental_2_8ano', 'fundamental_2_9ano',
            'medio_1ano', 'medio_2ano', 'medio_3ano'
        ]
        if v not in valid_levels:
            raise ValueError(f'Invalid grade level. Must be one of: {valid_levels}')
        return v

class StudentResponse(BaseModel):
    """Schema for student response"""
    id: UUID
    anonymous_code: str
    age: int
    grade_level: str
    diagnosis: Optional[str]
    cognitive_profile: Optional[Dict]
    sensory_profile: Optional[Dict]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True
```

---

## 4. Padrões e Convenções

### 4.1 Estilo de Código Python
```python
"""
PADRÕES OBRIGATÓRIOS:
- PEP 8 compliant
- Black formatter (line length: 88)
- isort para imports
- Type hints em todas as funções
- Docstrings em formato Google style
"""

# ✅ BOM - Seguindo padrões
from typing import List, Optional
from uuid import UUID

def calculate_student_risk_level(
    cognitive_score: float,
    sensory_score: float,
    negative_responses: int
) -> str:
    """
    Calculate risk level based on assessment scores.
    
    Args:
        cognitive_score: Average cognitive profile score (1-10)
        sensory_score: Average sensory profile score (0-3)
        negative_responses: Number of negative responses
    
    Returns:
        Risk level: 'baixo', 'medio', 'alto', or 'muito_alto'
    
    Examples:
        >>> calculate_student_risk_level(7.5, 1.2, 2)
        'baixo'
    """
    # Lógica clara e comentada
    if cognitive_score < 4 and negative_responses > 5:
        return 'muito_alto'
    elif cognitive_score < 6 or negative_responses > 3:
        return 'alto'
    elif sensory_score > 2 or negative_responses > 1:
        return 'medio'
    else:
        return 'baixo'

# ❌ RUIM - Não seguindo padrões
def calcRisk(c,s,n):  # Sem type hints, nomes ruins
    if c<4 and n>5: return 'muito_alto'  # Formatação ruim
    elif c<6 or n>3: return 'alto'
    elif s>2 or n>1: return 'medio'
    else: return 'baixo'
```

### 4.2 Nomenclatura
```python
# Classes: PascalCase
class StudentService:
    pass

class ActivityRecommender:
    pass

# Funções e variáveis: snake_case
def create_student():
    pass

student_id = "123"
cognitive_profile = {}

# Constantes: UPPER_SNAKE_CASE
MAX_STUDENTS_PER_PAGE = 100
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# Variáveis privadas: _prefixo
class MyClass:
    def __init__(self):
        self._internal_state = {}
    
    def _private_method(self):
        pass

# Nomes descritivos, não abreviações
# ✅ BOM
def calculate_average_cognitive_score(profile):
    pass

# ❌ RUIM
def calc_avg_cog(p):
    pass
```

### 4.3 Estrutura de Imports
```python
"""
Ordem de imports (isort):
1. Standard library
2. Third-party libraries
3. Local application/library
"""

# ✅ BOM - Ordem correta
# Standard library
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import UUID

# Third-party
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, String, Integer
from pydantic import BaseModel, Field

# Local
from src.core.config import settings
from src.core.database import get_db
from src.models.database.student import Student
from src.schemas.student import StudentCreate, StudentResponse
from src.services.student_service import StudentService
from src.utils.logger import get_logger

# ❌ RUIM - Ordem errada, imports desnecessários
from src.services.student_service import StudentService
from fastapi import *  # Nunca usar *
import pandas as pd
from src.core.config import settings
import os
```

### 4.4 Error Handling
```python
# ✅ BOM - Error handling explícito
from src.core.exceptions import StudentNotFoundError, ValidationError

def get_student_by_id(student_id: UUID, db: Session) -> Student:
    """
    Get student by ID with proper error handling.
    
    Args:
        student_id: Student UUID
        db: Database session
    
    Returns:
        Student object
    
    Raises:
        StudentNotFoundError: If student doesn't exist
    """
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            logger.warning(f"Student not found: {student_id}")
            raise StudentNotFoundError(
                f"Student with ID {student_id} not found"
            )
        
        return student
    
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError("Failed to retrieve student") from e

# ❌ RUIM - Erro genérico, sem logging
def get_student_by_id(student_id, db):
    try:
        return db.query(Student).filter(Student.id == student_id).first()
    except:
        return None  # Perde informação do erro
```

### 4.5 Logging
```python
# ✅ BOM - Logging estruturado
import logging
from src.utils.logger import get_logger

logger = get_logger(__name__)

def create_activity(activity_data: ActivityCreate, db: Session) -> Activity:
    """Create activity with proper logging"""
    
    logger.info(
        "Creating activity",
        extra={
            'student_id': activity_data.student_id,
            'subject': activity_data.subject,
            'difficulty': activity_data.difficulty
        }
    )
    
    try:
        activity = Activity(**activity_data.dict())
        db.add(activity)
        db.commit()
        
        logger.info(
            "Activity created successfully",
            extra={
                'activity_id': activity.id,
                'student_id': activity_data.student_id
            }
        )
        
        return activity
    
    except Exception as e:
        logger.error(
            "Failed to create activity",
            exc_info=True,
            extra={
                'student_id': activity_data.student_id,
                'error': str(e)
            }
        )
        raise

# ❌ RUIM - Print statements, sem estrutura
def create_activity(activity_data, db):
    print("Creating activity...")  # Não usar print
    activity = Activity(**activity_data.dict())
    db.add(activity)
    db.commit()
    print("Done!")  # Informação insuficiente
    return activity
```

### 4.6 Testes
```python
# tests/unit/test_student_service.py
"""
Padrão de testes:
- Usar pytest
- Fixtures para setup
- Nomenclatura: test_<function>_<scenario>_<expected_result>
- AAA pattern: Arrange, Act, Assert
"""

import pytest
from uuid import uuid4

from src.services.student_service import StudentService
from src.schemas.student import StudentCreate
from src.core.exceptions import StudentNotFoundError

@pytest.fixture
def student_data():
    """Fixture with sample student data"""
    return StudentCreate(
        age=10,
        grade_level="fundamental_1_3ano",
        diagnosis="autismo_leve",
        cognitive_profile={
            "memory": 7,
            "attention": 6,
            "processing_speed": 7,
            "executive_function": 6,
            "language": 8,
            "visual_spatial": 7
        }
    )

def test_create_student_success(db_session, student_data):
    """Test successful student creation"""
    # Arrange
    service = StudentService(db_session)
    created_by = "teacher_hash_123"
    
    # Act
    student = service.create(student_data, created_by=created_by)
    
    # Assert
    assert student.id is not None
    assert student.age == 10
    assert student.grade_level == "fundamental_1_3ano"
    assert student.created_by == created_by

def test_get_student_not_found_raises_error(db_session):
    """Test that getting non-existent student raises error"""
    # Arrange
    service = StudentService(db_session)
    non_existent_id = uuid4()
    
    # Act & Assert
    with pytest.raises(StudentNotFoundError):
        service.get_by_id(non_existent_id)

def test_list_students_pagination(db_session, student_data):
    """Test student list with pagination"""
    # Arrange
    service = StudentService(db_session)
    
    # Create 5 students
    for _ in range(5):
        service.create(student_data, created_by="teacher_hash")
    
    # Act
    page1 = service.list(skip=0, limit=2)
    page2 = service.list(skip=2, limit=2)
    
    # Assert
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id
```

---

## 5. Guia de Implementação

### 5.1 Workflow de Desenvolvimento
```mermaid
graph TD
    A[Nova Feature] --> B[Criar Branch]
    B --> C[Implementar Código]
    C --> D[Escrever Testes]
    D --> E[Executar Testes Localmente]
    E --> F{Testes Passam?}
    F -->|Não| C
    F -->|Sim| G[Commit]
    G --> H[Push Branch]
    H --> I[Criar Pull Request]
    I --> J[CI/CD Tests]
    J --> K{CI Passa?}
    K -->|Não| C
    K -->|Sim| L[Code Review]
    L --> M{Aprovado?}
    M -->|Não| C
    M -->|Sim| N[Merge to Main]
    N --> O[Deploy Automático]
```

### 5.2 Checklist de Feature
```yaml
Pre_Development:
  - [ ] Entender requisito completamente
  - [ ] Verificar se existe issue no GitHub
  - [ ] Criar branch: feature/nome-da-feature
  - [ ] Ler documentação relacionada

Development:
  - [ ] Implementar models (se necessário)
  - [ ] Implementar schemas
  - [ ] Implementar service
  - [ ] Implementar route/endpoint
  - [ ] Adicionar validações
  - [ ] Adicionar logging
  - [ ] Adicionar error handling
  - [ ] Seguir padrões de código

Testing:
  - [ ] Escrever testes unitários (>80% coverage)
  - [ ] Escrever testes de integração
  - [ ] Testar casos edge
  - [ ] Testar error scenarios
  - [ ] Executar: pytest tests/ -v
  - [ ] Verificar coverage: pytest --cov=src

Documentation:
  - [ ] Docstrings em todas funções
  - [ ] Atualizar README se necessário
  - [ ] Atualizar API docs
  - [ ] Comentários em código complexo

Quality:
  - [ ] black src/ tests/
  - [ ] flake8 src/ tests/
  - [ ] mypy src/
  - [ ] isort src/ tests/

Pre_Commit:
  - [ ] Revisar diff
  - [ ] Commit message descritiva
  - [ ] Push para branch
  - [ ] Criar PR com descrição clara

Code_Review:
  - [ ] Endereçar comentários
  - [ ] Re-push mudanças
  - [ ] Aguardar aprovação
  - [ ] Merge após aprovação
```

### 5.3 Implementação de Endpoint (Passo a Passo)

#### Exemplo: Endpoint de Geração de Atividade

**Passo 1: Criar Schema**
```python
# src/schemas/activity.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ActivityGenerateRequest(BaseModel):
    """Request schema for activity generation"""
    student_id: UUID
    subject: str = Field(..., description="Subject: matematica, portugues, ciencias, etc")
    topic: str = Field(..., description="Specific topic within subject")
    difficulty: int = Field(..., ge=1, le=10, description="Difficulty level 1-10")
    duration_minutes: int = Field(30, ge=10, le=120, description="Activity duration")
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "subject": "matematica",
                "topic": "adicao",
                "difficulty": 3,
                "duration_minutes": 30
            }
        }

class ActivityResponse(BaseModel):
    """Response schema for activity"""
    id: UUID
    student_id: UUID
    subject: str
    topic: str
    title: str
    content: str
    difficulty: int
    duration_minutes: int
    ai_generated: bool = True
    created_at: datetime
    
    class Config:
        orm_mode = True
```

**Passo 2: Criar/Atualizar Model**
```python
# src/models/database/activity.py

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.database.base import Base

class Activity(Base):
    """Activity database model"""
    
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(200), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    
    difficulty = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    ai_generated = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<Activity(id={self.id}, subject={self.subject}, topic={self.topic})>"
```

**Passo 3: Implementar Service**
```python
# src/services/activity_service.py

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.models.database.activity import Activity
from src.schemas.activity import ActivityGenerateRequest
from src.services.nlp_service import NLPService
from src.services.student_service import StudentService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ActivityService:
    """Service for activity operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.nlp_service = NLPService()
        self.student_service = StudentService(db)
    
    async def generate_activity(
        self,
        request: ActivityGenerateRequest,
        created_by: str
    ) -> Activity:
        """
        Generate personalized activity using AI.
        
        Args:
            request: Activity generation request
            created_by: Creator identifier (hashed teacher ID)
        
        Returns:
            Generated Activity object
        
        Raises:
            StudentNotFoundError: If student doesn't exist
            NLPServiceError: If AI generation fails
        """
        # 1. Get student profile
        logger.info(f"Generating activity for student {request.student_id}")
        student = self.student_service.get_by_id(request.student_id)
        
        # 2. Generate content with NLP service
        logger.info(f"Calling NLP service for content generation")
        generated_content = await self.nlp_service.generate_activity_content(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            student_age=student.age,
            cognitive_profile=student.cognitive_profile,
            sensory_profile=student.sensory_profile
        )
        
        # 3. Create activity in database
        activity = Activity(
            student_id=request.student_id,
            subject=request.subject,
            topic=request.topic,
            title=generated_content['title'],
            content=generated_content['content'],
            difficulty=request.difficulty,
            duration_minutes=request.duration_minutes,
            created_by=created_by
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        logger.info(f"Activity generated successfully: {activity.id}")
        return activity
    
    def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
        """Get activity by ID"""
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")
        return activity
```

**Passo 4: Implementar Route/Endpoint**
```python
# src/api/routes/activities.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.api.dependencies.database import get_db
from src.api.dependencies.auth import get_current_user
from src.schemas.activity import ActivityGenerateRequest, ActivityResponse
from src.services.activity_service import ActivityService
from src.core.exceptions import StudentNotFoundError, NLPServiceError
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/activities", tags=["activities"])

@router.post("/generate", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def generate_activity(
    request: ActivityGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate personalized activity using AI.
    
    This endpoint uses GPT-4 to generate educational activities
    tailored to the student's cognitive and sensory profiles.
    
    **Parameters:**
    - **student_id**: UUID of the student
    - **subject**: Subject area (matematica, portugues, etc)
    - **topic**: Specific topic within the subject
    - **difficulty**: Difficulty level from 1 to 10
    - **duration_minutes**: Expected duration (10-120 minutes)
    
    **Returns:**
    - Generated activity with AI-created content
    
    **Raises:**
    - **404**: Student not found
    - **500**: AI generation failed
    """
    try:
        service = ActivityService(db)
        activity = await service.generate_activity(
            request,
            created_by=current_user["sub"]
        )
        
        logger.info(
            "Activity generated via API",
            extra={
                'activity_id': str(activity.id),
                'student_id': str(request.student_id),
                'user': current_user["sub"]
            }
        )
        
        return activity
    
    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except NLPServiceError as e:
        logger.error(f"NLP service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate activity content"
        )

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get activity by ID"""
    service = ActivityService(db)
    return service.get_by_id(activity_id)
```

**Passo 5: Adicionar Testes**
```python
# tests/unit/test_activity_service.py

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from src.services.activity_service import ActivityService
from src.schemas.activity import ActivityGenerateRequest

@pytest.fixture
def activity_request():
    return ActivityGenerateRequest(
        student_id=uuid4(),
        subject="matematica",
        topic="adicao",
        difficulty=3,
        duration_minutes=30
    )

@pytest.fixture
def mock_student():
    student = Mock()
    student.id = uuid4()
    student.age = 10
    student.cognitive_profile = {"memory": 7, "attention": 6}
    student.sensory_profile = {"visual": 2, "auditory": 1}
    return student

@pytest.mark.asyncio
async def test_generate_activity_success(
    db_session,
    activity_request,
    mock_student
):
    """Test successful activity generation"""
    # Arrange
    service = ActivityService(db_session)
    
    # Mock student service
    with patch.object(service.student_service, 'get_by_id', return_value=mock_student):
        # Mock NLP service
        with patch.object(
            service.nlp_service,
            'generate_activity_content',
            new_callable=AsyncMock,
            return_value={
                'title': 'Adição Divertida',
                'content': 'Conteúdo da atividade...'
            }
        ):
            # Act
            activity = await service.generate_activity(
                activity_request,
                created_by="teacher_hash"
            )
    
    # Assert
    assert activity.id is not None
    assert activity.student_id == activity_request.student_id
    assert activity.subject == "matematica"
    assert activity.topic == "adicao"
    assert activity.title == "Adição Divertida"
    assert activity.ai_generated is True
```

**Passo 6: Registrar Router no Main**
```python
# src/api/main.py

from fastapi import FastAPI
from src.api.routes import activities  # Import do novo router

app = FastAPI(title="EduAutismo IA API")

# Registrar router
app.include_router(activities.router)
```

---

## 6. Exemplos de Código

### 6.1 Integração com OpenAI (NLP Service)
```python
# src/services/nlp_service.py

import openai
from typing import Dict, Optional
import json

from src.core.config import settings
from src.core.exceptions import NLPServiceError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class NLPService:
    """Service for OpenAI GPT-4 integration"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    async def generate_activity_content(
        self,
        subject: str,
        topic: str,
        difficulty: int,
        student_age: int,
        cognitive_profile: Optional[Dict] = None,
        sensory_profile: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate educational activity content using GPT-4.
        
        Args:
            subject: Subject area
            topic: Specific topic
            difficulty: Difficulty level (1-10)
            student_age: Student's age
            cognitive_profile: Cognitive abilities (optional)
            sensory_profile: Sensory preferences (optional)
        
        Returns:
            Dictionary with 'title' and 'content'
        
        Raises:
            NLPServiceError: If generation fails
        """
        try:
            # Build context-aware prompt
            prompt = self._build_activity_prompt(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                student_age=student_age,
                cognitive_profile=cognitive_profile,
                sensory_profile=sensory_profile
            )
            
            logger.info(f"Calling OpenAI API for activity generation")
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            parsed_content = self._parse_activity_response(content)
            
            logger.info(
                "Activity content generated successfully",
                extra={
                    'subject': subject,
                    'topic': topic,
                    'tokens_used': response.usage.total_tokens
                }
            )
            
            return parsed_content
        
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise NLPServiceError(f"Failed to generate content: {str(e)}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error in NLP service: {str(e)}")
            raise NLPServiceError(f"Unexpected error: {str(e)}") from e
    
    def _build_activity_prompt(
        self,
        subject: str,
        topic: str,
        difficulty: int,
        student_age: int,
        cognitive_profile: Optional[Dict],
        sensory_profile: Optional[Dict]
    ) -> str:
        """Build detailed prompt for activity generation"""
        
        prompt = f"""
Crie uma atividade pedagógica personalizada com as seguintes características:

INFORMAÇÕES DO ALUNO:
- Idade: {student_age} anos
- Diagnóstico: Transtorno do Espectro Autista (TEA)
"""
        
        if cognitive_profile:
            prompt += f"""
PERFIL COGNITIVO (escala 1-10):
- Memória: {cognitive_profile.get('memory', 'N/A')}
- Atenção: {cognitive_profile.get('attention', 'N/A')}
- Velocidade de Processamento: {cognitive_profile.get('processing_speed', 'N/A')}
- Função Executiva: {cognitive_profile.get('executive_function', 'N/A')}
- Linguagem: {cognitive_profile.get('language', 'N/A')}
- Visual-Espacial: {cognitive_profile.get('visual_spatial', 'N/A')}
"""
        
        if sensory_profile:
            prompt += f"""
PERFIL SENSORIAL (escala 0-3, onde 3 = alta sensibilidade):
- Visual: {sensory_profile.get('visual', 'N/A')}
- Auditivo: {sensory_profile.get('auditory', 'N/A')}
- Tátil: {sensory_profile.get('tactile', 'N/A')}
- Vestibular: {sensory_profile.get('vestibular', 'N/A')}
- Proprioceptivo: {sensory_profile.get('proprioceptive', 'N/A')}
"""
        
        prompt += f"""
REQUISITOS DA ATIVIDADE:
- Matéria: {subject}
- Tópico: {topic}
- Nível de dificuldade: {difficulty}/10

INSTRUÇÕES:
1. Crie um título atrativo e claro
2. Desenvolva o conteúdo da atividade considerando:
   - O perfil cognitivo do aluno
   - Sensibilidades sensoriais
   - Estratégias específicas para TEA (rotina, previsibilidade, apoios visuais)
3. Inclua instruções passo a passo
4. Sugira adaptações se necessário
5. Formate em JSON com as chaves: "title" e "content"

A atividade deve ser engajante, apropriada para a idade, e respeitar as características do TEA.
"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for GPT-4"""
        return """
Você é um especialista em educação especial e pedagogia para alunos com Transtorno do Espectro Autista (TEA).
Sua função é criar atividades pedagógicas personalizadas, levando em consideração as características cognitivas
e sensoriais de cada aluno.

PRINCÍPIOS A SEGUIR:
1. Use linguagem clara e objetiva
2. Forneça instruções passo a passo
3. Inclua apoios visuais quando apropriado
4. Considere sensibilidades sensoriais
5. Mantenha previsibilidade e estrutura
6. Adapte ao nível de desenvolvimento do aluno
7. Seja respeitoso e inclusivo

FORMATO DE SAÍDA:
Sempre responda em formato JSON válido com as chaves "title" e "content".
"""
    
    def _parse_activity_response(self, content: str) -> Dict[str, str]:
        """Parse GPT-4 response to extract title and content"""
        try:
            # Try to parse as JSON
            parsed = json.loads(content)
            
            if 'title' not in parsed or 'content' not in parsed:
                raise ValueError("Missing required fields in response")
            
            return {
                'title': parsed['title'],
                'content': parsed['content']
            }
        
        except json.JSONDecodeError:
            # If not JSON, try to extract manually
            logger.warning("Response not in JSON format, attempting manual extraction")
            
            # Simple extraction logic
            lines = content.strip().split('\n')
            title = lines[0] if lines else "Atividade Personalizada"
            content_text = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return {
                'title': title,
                'content': content_text
            }
```

### 6.2 ML Model - Classificador Comportamental
```python
# src/models/ml/behavioral_classifier.py

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

class BehavioralClassifier:
    """
    ML model for behavioral profile classification.
    
    Classifies students into risk levels based on cognitive,
    sensory, and behavioral assessment data.
    """
    
    RISK_LEVELS = ['baixo', 'medio', 'alto', 'muito_alto']
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
    
    @classmethod
    def load(cls, model_path: str, version: str = 'production') -> 'BehavioralClassifier':
        """
        Load trained model from disk.
        
        Args:
            model_path: Base path to models directory
            version: Model version to load
        
        Returns:
            Loaded BehavioralClassifier instance
        """
        instance = cls()
        
        base_path = Path(model_path) / version
        
        # Load model
        model_file = base_path / 'model.pkl'
        instance.model = joblib.load(model_file)
        logger.info(f"Loaded model from {model_file}")
        
        # Load scaler
        scaler_file = base_path / 'scaler.pkl'
        instance.scaler = joblib.load(scaler_file)
        logger.info(f"Loaded scaler from {scaler_file}")
        
        # Load metadata
        metadata_file = base_path / 'metadata.json'
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            instance.feature_names = metadata['feature_names']
        
        logger.info(f"Behavioral classifier loaded: version={version}")
        
        return instance
    
    def predict_single(self, features: Dict[str, float]) -> Dict:
        """
        Predict risk level for a single student.
        
        Args:
            features: Dictionary with feature values
        
        Returns:
            Dictionary with prediction and confidence
        """
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
        
        # Select and order features
        X = df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get confidence (max probability)
        confidence = float(np.max(probabilities))
        
        return {
            'risk_level': self.RISK_LEVELS[prediction],
            'confidence': confidence,
            'probabilities': {
                level: float(prob)
                for level, prob in zip(self.RISK_LEVELS, probabilities)
            }
        }
    
    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Dict]:
        """Predict for multiple students"""
        return [self.predict_single(features) for features in features_list]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Sort by importance
        return dict(sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
```

### 6.3 Database Migrations (Alembic)
```python
# alembic/versions/001_create_students_table.py

"""Create students table

Revision ID: 001
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create students table"""
    op.create_table(
        'students',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('anonymous_code', sa.String(20), nullable=False, unique=True),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('grade_level', sa.String(50), nullable=False),
        sa.Column('diagnosis', sa.String(50), nullable=True),
        sa.Column('cognitive_profile', JSON, nullable=True),
        sa.Column('sensory_profile', JSON, nullable=True),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )
    
    # Create indexes
    op.create_index('ix_students_anonymous_code', 'students', ['anonymous_code'])
    op.create_index('ix_students_grade_level', 'students', ['grade_level'])
    op.create_index('ix_students_created_by', 'students', ['created_by'])

def downgrade():
    """Drop students table"""
    op.drop_index('ix_students_created_by')
    op.drop_index('ix_students_grade_level')
    op.drop_index('ix_students_anonymous_code')
    op.drop_table('students')
```

---

## 7. Testes e Validação

### 7.1 Estrutura de Testes
```bash
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── unit/                    # Testes unitários
│   ├── __init__.py
│   ├── test_student_service.py
│   ├── test_activity_service.py
│   ├── test_assessment_service.py
│   ├── test_nlp_service.py
│   └── test_ml_models.py
├── integration/             # Testes de integração
│   ├── __init__.py
│   ├── test_api_students.py
│   ├── test_api_activities.py
│   └── test_api_auth.py
└── fixtures/                # Dados de teste
    ├── __init__.py
    └── sample_data.py
```

### 7.2 Fixtures (conftest.py)
```python
# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.core.database import Base
from src.api.main import app
from src.api.dependencies.database import get_db

# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session for test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_student_data():
    """Sample student data for tests"""
    return {
        "age": 10,
        "grade_level": "fundamental_1_3ano",
        "diagnosis": "autismo_leve",
        "cognitive_profile": {
            "memory": 7,
            "attention": 6,
            "processing_speed": 7,
            "executive_function": 6,
            "language": 8,
            "visual_spatial": 7
        },
        "sensory_profile": {
            "visual": 2,
            "auditory": 2,
            "tactile": 1,
            "vestibular": 2,
            "proprioceptive": 1
        }
    }
```

### 7.3 Comandos de Teste
```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar testes específicos
pytest tests/unit/test_student_service.py
pytest tests/integration/test_api_students.py

# Executar com coverage
pytest --cov=src --cov-report=html

# Executar apenas testes marcados
pytest -m "not slow"

# Executar em paralelo
pytest -n auto

# Executar com output completo
pytest -vv -s

# Executar e parar no primeiro erro
pytest -x

# Executar testes que falharam na última execução
pytest --lf

# Executar em modo watch (requer pytest-watch)
ptw
```

---

## 8. Deploy e DevOps

### 8.1 Ambiente de Desenvolvimento
```bash
# 1. Clone e setup
git clone https://github.com/your-org/eduautismo-ia.git
cd eduautismo-ia

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 5. Iniciar banco de dados
docker-compose up -d postgres mongodb redis

# 6. Executar migrations
alembic upgrade head

# 7. Seed database (opcional)
python scripts/seed_database.py

# 8. Iniciar API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 9. Iniciar Web UI (outro terminal)
streamlit run src/web/app.py
```

### 8.2 Docker Build e Run
```bash
# Build image
docker build -t eduautismo-api:latest -f Dockerfile.api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENAI_API_KEY=sk-... \
  --name eduautismo-api \
  eduautismo-api:latest

# Ver logs
docker logs -f eduautismo-api

# Parar container
docker stop eduautismo-api

# Remover container
docker rm eduautismo-api
```

### 8.3 Deploy AWS (Resumo)
```bash
# 1. Provisionar infraestrutura
cd terraform/
terraform init
terraform workspace new production
terraform plan -out=tfplan
terraform apply tfplan

# 2. Build e push imagem
./scripts/build_and_push.sh

# 3. Deploy aplicação
./scripts/deploy.sh production latest

# 4. Verificar health
curl https://api.eduautismo.example.com/health
```

---

## 9. Troubleshooting

### 9.1 Problemas Comuns

#### Problema: Erro de conexão com banco de dados
```python
# Sintoma
sqlalchemy.exc.OperationalError: could not connect to server

# Solução
# 1. Verificar se o PostgreSQL está rodando
docker ps | grep postgres

# 2. Verificar variável DATABASE_URL
echo $DATABASE_URL

# 3. Testar conexão manualmente
psql -h localhost -U eduautismo_user -d eduautismo_db

# 4. Verificar configuração no código
# src/core/config.py
DATABASE_URL: str = "postgresql://user:pass@localhost:5432/dbname"
```

#### Problema: OpenAI API retorna erro 429 (Rate Limit)
```python
# Sintoma
openai.error.RateLimitError: Rate limit exceeded

# Solução
# Implementar retry com backoff exponencial
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_openai_with_retry():
    return await openai.ChatCompletion.acreate(...)
```

#### Problema: Testes falhando localmente
```bash
# Sintoma
ImportError: cannot import name 'X' from 'Y'

# Solução
# 1. Reinstalar dependências
pip install -r requirements-dev.txt

# 2. Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# 3. Limpar cache pytest
pytest --cache-clear

# 4. Verificar fixtures
pytest --fixtures
```

### 9.2 Logs e Debugging
```python
# Habilitar debug logging
# .env
LOG_LEVEL=DEBUG

# Ver logs estruturados
import logging
logging.basicConfig(level=logging.DEBUG)

# Usar pdb para debugging
import pdb; pdb.set_trace()

# Ou usar breakpoint() (Python 3.7+)
breakpoint()
```

---

## 10. Referências Rápidas

### 10.1 Comandos Essenciais
```bash
# Desenvolvimento
uvicorn src.api.main:app --reload              # Iniciar API
streamlit run src/web/app.py                   # Iniciar Web UI
pytest tests/ -v                               # Rodar testes
black src/ tests/                              # Formatar código
flake8 src/ tests/                             # Linter
mypy src/                                      # Type checking

# Database
alembic revision --autogenerate -m "message"   # Criar migration
alembic upgrade head                           # Aplicar migrations
alembic downgrade -1                           # Reverter migration
psql $DATABASE_URL                             # Conectar ao banco

# Docker
docker-compose up -d                           # Iniciar serviços
docker-compose logs -f api                     # Ver logs
docker-compose down                            # Parar serviços
docker-compose exec postgres psql -U user      # Acessar PostgreSQL

# Git
git checkout -b feature/nome                   # Criar branch
git add .                                      # Add changes
git commit -m "feat: description"              # Commit
git push origin feature/nome                   # Push

# AWS
aws ecs update-service --force-new-deployment  # Forçar redeploy
aws logs tail /ecs/eduautismo-production       # Ver logs
aws rds describe-db-instances                  # Ver databases
```

### 10.2 URLs Importantes
```yaml
Desenvolvimento:
  API: http://localhost:8000
  API_Docs: http://localhost:8000/docs
  Web_UI: http://localhost:8501

Staging:
  API: https://api-staging.eduautismo.example.com
  Web: https://staging.eduautismo.example.com

Production:
  API: https://api.eduautismo.example.com
  Web: https://eduautismo.example.com
  Monitoring: https://app.datadoghq.com

Documentação:
  GitHub: https://github.com/your-org/eduautismo-ia
  Confluence: https://your-org.atlassian.net/wiki
  API_Docs: https://docs.eduautismo.example.com
```

### 10.3 Contatos
```yaml
Desenvolvimento:
  Tech_Lead: tech-lead@example.com
  DevOps: devops@example.com
  Slack: #eduautismo-dev

Operações:
  On_Call: oncall@example.com
  PagerDuty: https://your-org.pagerduty.com
  Slack: #eduautismo-alerts

Negócio:
  Product_Owner: product@example.com
  Stakeholders: stakeholders@example.com
```

---

## 🎯 Checklist Final para AI Assistants

Quando ajudar no desenvolvimento, sempre:

- [ ] Ler este CLAUDE.md completamente antes de começar
- [ ] Seguir estrutura de código definida
- [ ] Usar type hints em todo código Python
- [ ] Adicionar docstrings (Google style)
- [ ] Implementar error handling adequado
- [ ] Adicionar logging estruturado
- [ ] Escrever testes (unitários e integração)
- [ ] Seguir padrões de nomenclatura
- [ ] Validar com Black, Flake8, MyPy
- [ ] Verificar coverage >80%
- [ ] Documentar decisões importantes
- [ ] Atualizar documentação quando necessário
- [ ] Considerar LGPD e segurança
- [ ] Testar localmente antes de commit
- [ ] Criar PR com descrição clara

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-01-15  
**Mantenedor**: Cleyber Silva  
**Contato**: cleyber.silva@live.com

---

*Este documento deve ser mantido atualizado conforme o projeto evolui.*