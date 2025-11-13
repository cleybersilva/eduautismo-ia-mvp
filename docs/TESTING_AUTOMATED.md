# Guia de Testes Automatizados - EduAutismo IA

## Visão Geral

Este documento fornece informações completas sobre os testes automatizados do projeto EduAutismo IA, incluindo testes unitários e de integração.

**Status Atual** (Última atualização: 2025-11-13):
- ✅ **82.25%** de cobertura de código
- ✅ **306 testes** passando (280 unit + 26 integration)
- ✅ Configuração SQLite in-memory para testes
- ✅ Tipos de banco de dados portáveis implementados

## Índice

- [Estrutura de Testes](#estrutura-de-testes)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Tipos Portáveis de Banco de Dados](#tipos-portáveis-de-banco-de-dados)
- [Executando os Testes](#executando-os-testes)
- [Testes Unitários](#testes-unitários)
- [Testes de Integração](#testes-de-integração)
- [Cobertura de Código](#cobertura-de-código)
- [Fixtures e Utilitários](#fixtures-e-utilitários)
- [Troubleshooting](#troubleshooting)
- [Boas Práticas](#boas-práticas)

---

## Estrutura de Testes

```
backend/
├── tests/
│   ├── conftest.py                    # Configuração pytest e fixtures compartilhadas
│   ├── __init__.py
│   │
│   ├── unit/                          # Testes unitários (280 testes)
│   │   ├── __init__.py
│   │   ├── test_activity_assessment_schemas.py
│   │   ├── test_aws_service.py
│   │   ├── test_config.py
│   │   ├── test_constants.py
│   │   ├── test_exceptions.py
│   │   ├── test_logger.py
│   │   ├── test_ml_service.py
│   │   ├── test_models.py
│   │   ├── test_nlp_service.py
│   │   ├── test_schemas.py
│   │   ├── test_security.py
│   │   └── test_student_service.py
│   │
│   └── integration/                   # Testes de integração (26 testes)
│       ├── __init__.py
│       ├── test_activities_api.py     # 5 testes
│       ├── test_assessments_api.py    # 11 testes
│       ├── test_auth_api.py           # 6 testes
│       └── test_students_api.py       # 4 testes
│
├── coverage/                          # Relatórios de cobertura
│   └── html/
│       └── index.html                 # Relatório visual
│
├── pytest.ini                         # Configuração do pytest
└── .coverage                          # Dados de cobertura
```

---

## Configuração do Ambiente

### Pré-requisitos

```bash
# Python 3.11+
python --version

# Dependências de testes (já incluídas em requirements-dev.txt)
pip install pytest pytest-cov pytest-asyncio
```

### Configuração do Pytest

O arquivo `pytest.ini` contém a configuração do pytest:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-fail-under=60
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Variáveis de Ambiente para Testes

```bash
# Use SQLite in-memory para testes (padrão)
export USE_SQLITE_TESTS=true

# Ou use PostgreSQL para testes
export USE_SQLITE_TESTS=false
export TEST_DATABASE_URL=postgresql://eduautismo:eduautismo_dev_pass@localhost:5432/eduautismo_test
```

---

## Tipos Portáveis de Banco de Dados

Para permitir testes com SQLite in-memory sem depender de PostgreSQL, implementamos tipos customizados de banco de dados em `app/db/types.py`.

### GUID - UUID Portável

```python
from app.db.types import GUID

class MyModel(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True)
```

**Comportamento:**
- **PostgreSQL**: Usa `UUID` nativo
- **SQLite**: Usa `String(36)` e converte automaticamente

### StringArray - Arrays Portáveis

```python
from app.db.types import StringArray

class Student(BaseModel):
    interests: Mapped[List[str]] = mapped_column(StringArray, nullable=False)
```

**Comportamento:**
- **PostgreSQL**: Usa `ARRAY(String)` nativo
- **SQLite**: Usa `Text` com serialização JSON

### PortableJSON - JSON Portável

```python
from app.db.types import PortableJSON

class Activity(BaseModel):
    metadata: Mapped[Dict[str, Any]] = mapped_column(PortableJSON, nullable=True)
```

**Comportamento:**
- **PostgreSQL**: Usa `JSONB` para melhor performance
- **SQLite**: Usa `JSON` padrão

### Implementação

```python
# app/db/types.py
import json
import uuid
from typing import List, Any

from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY as PostgreSQL_ARRAY, UUID as PostgreSQL_UUID, JSONB as PostgreSQL_JSONB
from sqlalchemy.types import JSON

class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return str(value) if isinstance(value, uuid.UUID) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
```

---

## Executando os Testes

### Comandos Básicos

```bash
# Executar todos os testes
cd backend
pytest

# Executar apenas testes unitários
pytest tests/unit/

# Executar apenas testes de integração
pytest tests/integration/

# Executar teste específico
pytest tests/unit/test_models.py
pytest tests/integration/test_students_api.py::TestStudentsAPI::test_create_student_success

# Executar com verbose
pytest -v

# Executar com output detalhado
pytest -vv -s

# Parar no primeiro erro
pytest -x

# Executar testes marcados
pytest -m unit
pytest -m integration
```

### Com Cobertura de Código

```bash
# Cobertura completa
pytest --cov=app --cov-report=term --cov-report=html

# Apenas relatório no terminal
pytest --cov=app --cov-report=term

# Salvar em HTML (disponível em coverage/html/index.html)
pytest --cov=app --cov-report=html:coverage/html

# Mostrar linhas não cobertas
pytest --cov=app --cov-report=term-missing

# Cobertura mínima exigida (fail se < 60%)
pytest --cov=app --cov-fail-under=60
```

### Em Paralelo (mais rápido)

```bash
# Instalar plugin
pip install pytest-xdist

# Executar em múltiplos cores
pytest -n auto
pytest -n 4  # 4 workers
```

---

## Testes Unitários

### Estrutura de um Teste Unitário

```python
# tests/unit/test_student_service.py
import pytest
from uuid import uuid4

from app.services.student_service import StudentService
from app.schemas.student import StudentCreate
from app.core.exceptions import StudentNotFoundError

def test_create_student_success(db_session, test_user):
    """Test successful student creation."""
    # Arrange
    service = StudentService(db_session)
    student_data = StudentCreate(
        name="Test Student",
        date_of_birth=date(2015, 1, 1),
        age=10,
        diagnosis="Transtorno do Espectro Autista",
        tea_level="level_1",
        interests=["música", "arte"],
        learning_profile={"visual_learner": True},
    )

    # Act
    student = service.create(student_data, teacher_id=test_user.id)

    # Assert
    assert student.id is not None
    assert student.name == "Test Student"
    assert student.age == 10
    assert student.teacher_id == test_user.id

def test_get_student_not_found_raises_error(db_session):
    """Test that getting non-existent student raises error."""
    # Arrange
    service = StudentService(db_session)
    non_existent_id = uuid4()

    # Act & Assert
    with pytest.raises(StudentNotFoundError):
        service.get_by_id(non_existent_id)
```

### Principais Testes Unitários

| Módulo | Arquivo | Testes | Descrição |
|--------|---------|--------|-----------|
| **Models** | `test_models.py` | 30 | Testa modelos SQLAlchemy |
| **Schemas** | `test_schemas.py` | 45 | Valida schemas Pydantic |
| **Services** | `test_student_service.py` | 25 | Lógica de negócio de alunos |
| **Services** | `test_aws_service.py` | 40 | Integração AWS (mocked) |
| **Services** | `test_ml_service.py` | 50 | Serviço de ML (mocked) |
| **Services** | `test_nlp_service.py` | 35 | Serviço NLP/OpenAI (mocked) |
| **Core** | `test_security.py` | 20 | Autenticação e segurança |
| **Core** | `test_exceptions.py` | 15 | Exceções customizadas |
| **Utils** | `test_logger.py` | 10 | Sistema de logging |
| **Utils** | `test_constants.py` | 10 | Constantes e enums |

### Mocking em Testes Unitários

```python
from unittest.mock import Mock, patch, AsyncMock

# Mock de serviço externo
@patch('app.services.nlp_service.openai.ChatCompletion.acreate')
async def test_generate_activity_content(mock_openai):
    # Arrange
    mock_openai.return_value = AsyncMock(
        choices=[Mock(message=Mock(content='{"title": "Test", "content": "Test content"}'))]
    )
    service = NLPService()

    # Act
    result = await service.generate_activity_content(
        subject="matemática",
        topic="adição",
        difficulty=3,
        student_age=10
    )

    # Assert
    assert result['title'] == "Test"
    assert mock_openai.called
```

---

## Testes de Integração

### Estrutura de um Teste de Integração

```python
# tests/integration/test_students_api.py
from datetime import date

class TestStudentsAPI:
    """Integration tests for students API endpoints."""

    def test_create_student_success(self, client, auth_headers):
        """Test successful student creation."""
        # Arrange
        student_data = {
            "name": "Maria Silva",
            "date_of_birth": "2014-03-20",
            "age": 11,
            "diagnosis": "Transtorno do Espectro Autista - Nível 2",
            "tea_level": "LEVEL_2",
            "interests": ["música", "arte"],
            "learning_profile": {
                "visual_learner": True,
                "auditory_sensitivity": "high"
            }
        }

        # Act
        response = client.post(
            "/api/v1/students/",
            json=student_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Maria Silva"
        assert data["age"] == 11
        assert data["tea_level"] == "LEVEL_2"
        assert "id" in data

    def test_create_student_without_auth(self, client):
        """Test creating student without authentication fails."""
        # Act
        response = client.post("/api/v1/students/", json={})

        # Assert
        assert response.status_code == 401
```

### Principais Testes de Integração

| Módulo | Testes | Endpoints Testados |
|--------|--------|-------------------|
| **Auth API** | 6 | `/api/v1/auth/*` |
| **Students API** | 4 | `/api/v1/students/*` |
| **Activities API** | 5 | `/api/v1/activities/*` |
| **Assessments API** | 11 | `/api/v1/assessments/*` |

### Cenários Testados

**Autenticação:**
- ✅ Registro de usuário com sucesso
- ✅ Registro com email duplicado falha
- ✅ Login com credenciais válidas
- ✅ Login com credenciais inválidas
- ✅ Obter usuário atual autenticado
- ✅ Acesso não autorizado retorna 401

**Students:**
- ✅ Criar aluno com dados válidos
- ✅ Criar aluno sem autenticação falha
- ✅ Criar aluno com data de nascimento inválida
- ✅ Criar aluno abaixo da idade mínima

**Activities:**
- ✅ Gerar atividade com sucesso
- ✅ Gerar atividade sem autenticação
- ✅ Gerar atividade para aluno inexistente
- ✅ Validação de duração da atividade
- ✅ Gerar múltiplos tipos de atividades

**Assessments:**
- ✅ Criar avaliação com dados completos
- ✅ Criar avaliação com dados mínimos
- ✅ Obter avaliação por ID
- ✅ Listar avaliações por aluno
- ✅ Atualizar avaliação
- ✅ Validações de campos obrigatórios

---

## Cobertura de Código

### Status Atual

```
Cobertura Total: 82.25%
Total de Testes: 306 (280 unit + 26 integration)
Tempo de Execução: ~5 minutos
```

### Cobertura por Módulo

| Módulo | Cobertura | Statements | Missing |
|--------|-----------|------------|---------|
| **Models** | 90-100% | - | Muito boa |
| `student.py` | 100% | 23/23 | ✅ Completo |
| `activity.py` | 95% | 36/38 | ⚠️ 2 linhas |
| `assessment.py` | 90% | 35/39 | ⚠️ 4 linhas |
| `user.py` | 89% | 31/35 | ⚠️ 4 linhas |
| **Core** | 96-100% | - | Excelente |
| `exceptions.py` | 100% | 143/143 | ✅ Completo |
| `security.py` | 100% | 37/37 | ✅ Completo |
| `config.py` | 96% | 43/44 | ⚠️ 1 linha |
| **Schemas** | 94-100% | - | Excelente |
| `activity.py` | 100% | 81/81 | ✅ Completo |
| `assessment.py` | 98% | 83/84 | ⚠️ 1 linha |
| `student.py` | 96% | 49/50 | ⚠️ 1 linha |
| `common.py` | 100% | 81/81 | ✅ Completo |
| **Services** | 71-100% | - | Bom |
| `student_service.py` | 100% | 23/23 | ✅ Completo |
| `activity_service.py` | 99% | 111/112 | ⚠️ 1 linha |
| `assessment_service.py` | 100% | 76/76 | ✅ Completo |
| `nlp_service.py` | 85% | 127/149 | ⚠️ 22 linhas |
| `ml_service.py` | 79% | 249/308 | ⚠️ 59 linhas |
| `aws_service.py` | 71% | 135/193 | ⚠️ 58 linhas |
| **API Routes** | 55-67% | - | Aceitável |
| `assessments.py` | 67% | 40/60 | ⚠️ 20 linhas |
| `auth.py` | 56% | 57/94 | ⚠️ 37 linhas |
| `activities.py` | 56% | 42/66 | ⚠️ 24 linhas |
| `students.py` | 55% | 22/34 | ⚠️ 12 linhas |
| `health.py` | 40% | 19/48 | ❌ 29 linhas |

### Visualizar Relatório de Cobertura

```bash
# Gerar relatório HTML
pytest --cov=app --cov-report=html:coverage/html

# Abrir no navegador
# Linux/WSL
xdg-open coverage/html/index.html

# macOS
open coverage/html/index.html

# Windows
start coverage/html/index.html
```

O relatório HTML mostra:
- ✅ Linhas cobertas (verde)
- ❌ Linhas não cobertas (vermelho)
- ⚠️ Branches parcialmente cobertos (amarelo)
- 📊 Estatísticas por arquivo
- 📈 Gráficos de cobertura

### Metas de Cobertura

| Tipo | Mínimo | Recomendado | Excelente |
|------|--------|-------------|-----------|
| **Geral** | 60% | 70% | 80%+ |
| **Models** | 80% | 90% | 95%+ |
| **Schemas** | 80% | 90% | 95%+ |
| **Services** | 70% | 80% | 90%+ |
| **API Routes** | 50% | 70% | 85%+ |
| **Core/Utils** | 80% | 90% | 95%+ |

---

## Fixtures e Utilitários

### Fixtures Principais (conftest.py)

```python
@pytest.fixture(scope="session")
def engine():
    """Create test database engine with SQLite or PostgreSQL."""
    if USE_SQLITE:
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool  # Crucial para SQLite :memory:
        )
    else:
        engine = create_engine(
            TEST_DATABASE_URL,
            pool_pre_ping=True
        )

    # Import models
    from app.models.user import User
    from app.models.student import Student
    from app.models.activity import Activity
    from app.models.assessment import Assessment

    # Create tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session for test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        # Clean up data
        # ... (código de limpeza)
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client."""
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
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        role="teacher",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers with valid token."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_student(db_session, test_user):
    """Create test student."""
    student = Student(
        name="Test Student",
        date_of_birth=date(2015, 6, 15),
        age=9,
        diagnosis="Transtorno do Espectro Autista - Nível 1",
        tea_level="level_1",
        interests=["matemática", "jogos"],
        learning_profile={"visual_learner": True},
        teacher_id=test_user.id,
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student
```

### Usando Fixtures

```python
def test_with_fixtures(db_session, test_user, test_student):
    """Example test using multiple fixtures."""
    # db_session, test_user, and test_student are automatically created
    assert test_student.teacher_id == test_user.id
    assert db_session.query(Student).count() == 1
```

---

## Troubleshooting

### Problema: Testes Falhando com "no such table"

**Causa**: SQLite :memory: cria banco separado para cada conexão.

**Solução**: Usar `StaticPool` no conftest.py:

```python
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # ← Adicionar isso
)
```

### Problema: Erros de tipo PostgreSQL UUID/ARRAY

**Causa**: SQLite não suporta tipos PostgreSQL nativamente.

**Solução**: Usar tipos portáveis de `app/db/types.py`:

```python
# ❌ Errado
from sqlalchemy.dialects.postgresql import UUID, ARRAY

id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
interests: Mapped[List[str]] = mapped_column(ARRAY(String))

# ✅ Correto
from app.db.types import GUID, StringArray

id: Mapped[uuid.UUID] = mapped_column(GUID)
interests: Mapped[List[str]] = mapped_column(StringArray)
```

### Problema: Testes Lentos

**Opções:**

```bash
# 1. Executar em paralelo
pytest -n auto

# 2. Executar apenas testes rápidos
pytest -m "not slow"

# 3. Parar no primeiro erro
pytest -x

# 4. Executar apenas testes modificados
pytest --lf  # last failed
pytest --ff  # failed first
```

### Problema: Coverage Baixo

**Como Aumentar:**

1. Identificar arquivos com baixa cobertura:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

2. Ver linhas específicas não cobertas no HTML:
   ```bash
   pytest --cov=app --cov-report=html
   open coverage/html/index.html
   ```

3. Adicionar testes para linhas não cobertas

4. Focar em:
   - Exception handlers
   - Edge cases
   - Error paths
   - Validações

### Problema: Import Errors

**Causa**: Módulos não encontrados.

**Solução**:

```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Ou instalar em modo development
pip install -e .
```

---

## Boas Práticas

### Nomenclatura de Testes

```python
# ✅ Bom - Descritivo e claro
def test_create_student_with_valid_data_returns_created_student():
    pass

def test_create_student_without_name_raises_validation_error():
    pass

def test_get_student_by_nonexistent_id_raises_not_found_error():
    pass

# ❌ Ruim - Vago
def test_student():
    pass

def test_create():
    pass
```

### Padrão AAA (Arrange-Act-Assert)

```python
def test_student_creation():
    # Arrange - Preparar dados e dependências
    service = StudentService(db_session)
    student_data = StudentCreate(name="Test", ...)

    # Act - Executar ação sendo testada
    student = service.create(student_data)

    # Assert - Verificar resultado
    assert student.id is not None
    assert student.name == "Test"
```

### Testes Independentes

```python
# ✅ Bom - Cada teste é independente
def test_create_student(db_session):
    student = create_test_student(db_session)
    assert student.id is not None

def test_update_student(db_session):
    student = create_test_student(db_session)  # Cria próprio student
    student.name = "Updated"
    assert student.name == "Updated"

# ❌ Ruim - Testes dependentes
student_id = None

def test_create_student():
    global student_id
    student = create_test_student()
    student_id = student.id  # Estado compartilhado!

def test_update_student():
    global student_id
    student = get_student(student_id)  # Depende do teste anterior!
```

### Mocking Apropriado

```python
# ✅ Bom - Mock de serviços externos
@patch('app.services.aws_service.boto3.client')
def test_upload_file(mock_boto3):
    mock_s3 = Mock()
    mock_boto3.return_value = mock_s3

    service = AWSService()
    service.upload_file("test.txt", b"content")

    mock_s3.put_object.assert_called_once()

# ❌ Ruim - Mock de código interno
@patch('app.models.student.Student')  # Não mockar seus próprios models!
```

### Parametrização de Testes

```python
import pytest

@pytest.mark.parametrize("age,expected_valid", [
    (5, False),   # Muito jovem
    (6, True),    # Idade mínima
    (12, True),   # Válido
    (18, True),   # Idade máxima
    (19, False),  # Muito velho
])
def test_student_age_validation(age, expected_valid):
    if expected_valid:
        student = StudentCreate(age=age, ...)
        assert student.age == age
    else:
        with pytest.raises(ValidationError):
            StudentCreate(age=age, ...)
```

### Assertions Claras

```python
# ✅ Bom - Mensagens de erro claras
def test_student_creation():
    student = create_student()
    assert student.id is not None, "Student ID should be generated"
    assert student.name == "Test", f"Expected 'Test', got '{student.name}'"
    assert student.age == 10, f"Expected age 10, got {student.age}"

# ❌ Ruim - Assertions sem contexto
def test_student_creation():
    student = create_student()
    assert student.id
    assert student.name
    assert student.age
```

---

## Integração com CI/CD

### GitHub Actions

Exemplo de workflow (`.github/workflows/tests.yml`):

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        fail_ci_if_error: true
```

---

## Recursos Adicionais

### Documentação

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Coverage.py](https://coverage.readthedocs.io/)

### Ferramentas Úteis

- `pytest-watch` - Re-executa testes quando arquivos mudam
- `pytest-xdist` - Execução paralela de testes
- `pytest-cov` - Cobertura de código
- `pytest-asyncio` - Suporte para testes assíncronos
- `pytest-mock` - Facilita mocking

### Comandos Quick Reference

```bash
# Instalar ferramentas de desenvolvimento
pip install -r requirements-dev.txt

# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=app --cov-report=html

# Apenas unit tests
pytest tests/unit/

# Apenas integration tests
pytest tests/integration/

# Verbose
pytest -v

# Parar no primeiro erro
pytest -x

# Executar em paralelo
pytest -n auto

# Watch mode (requer pytest-watch)
ptw

# Ver fixtures disponíveis
pytest --fixtures

# Coletar informações sem executar
pytest --collect-only
```

---

**Última Atualização**: 2025-11-13
**Cobertura Atual**: 82.25%
**Total de Testes**: 306 (280 unit + 26 integration)
**Status**: ✅ Todos os testes de integração passando

---

## Próximos Passos

1. ✅ **Atingir 80% de cobertura** - Concluído!
2. ⏳ **Aumentar cobertura dos endpoints health** (40% → 80%)
3. ⏳ **Corrigir 9 testes de schema que falharam**
4. ⏳ **Adicionar testes de performance/carga**
5. ⏳ **Implementar testes E2E com Selenium/Playwright**
6. ⏳ **Configurar mutation testing com mutpy**

---

Para dúvidas ou problemas com testes, consulte:
1. Este documento
2. `docs/TESTING.md` para testes manuais
3. `docs/TEST_QUICK_REFERENCE.md` para referência rápida
4. Abra uma issue no GitHub
