# API Schemas - EduAutismo IA

## Visão Geral

Este diretório contém todos os schemas Pydantic V2 usados para validação de request/response da API. Os schemas garantem que os dados enviados e recebidos pela API estão no formato correto e seguem todas as regras de validação.

## Organização

```
schemas/
├── common.py        # Schemas reutilizáveis (paginação, responses, etc.)
├── user.py          # Schemas de usuário
├── student.py       # Schemas de aluno
├── activity.py      # Schemas de atividade
├── assessment.py    # Schemas de avaliação
└── __init__.py      # Exports centralizados
```

## Schemas Implementados

### Common Schemas (`common.py`)

#### Base Classes

- **`BaseSchema`** - Classe base com configuração comum
  - `from_attributes=True` - Permite ORM mode
  - `use_enum_values=True` - Usa valores de enum

- **`TimestampSchema`** - Campos de timestamp
  - `created_at: datetime`
  - `updated_at: datetime`

- **`UUIDSchema`** - Campo de ID UUID
  - `id: UUID`

- **`BaseResponseSchema`** - Response completo (UUID + timestamps)

#### Pagination

- **`PaginationParams`** - Parâmetros de paginação
  - `skip: int` (default=0, min=0)
  - `limit: int` (default=20, min=1, max=100)

- **`PaginatedResponse[T]`** - Response paginado genérico
  - `items: List[T]`
  - `total: int`
  - `skip: int`
  - `limit: int`
  - `has_more: bool`

#### API Responses

- **`MessageResponse`** - Resposta simples com mensagem
- **`SuccessResponse`** - Resposta de sucesso com dados opcionais
- **`ErrorResponse`** - Resposta de erro
- **`ValidationErrorResponse`** - Erro de validação (422)

#### Health Check

- **`HealthCheckResponse`** - Status básico
- **`DetailedHealthCheckResponse`** - Status com componentes
- **`ComponentHealth`** - Status de componente individual

#### Authentication

- **`Token`** - Response com access e refresh tokens
- **`TokenRefresh`** - Request para renovar token
- **`TokenResponse`** - Response após refresh

### User Schemas (`user.py`)

#### Request Schemas

- **`UserRegister`** - Registro de novo usuário
  - Validação de email único
  - Validação de senha forte (maiúscula, minúscula, número, especial)
  - Validação de telefone
  - Campo `role` com default `teacher`

- **`UserLogin`** - Login (OAuth2 compatible)
  - `username: EmailStr` (email)
  - `password: str`

- **`UserUpdate`** - Atualização de perfil
  - Todos os campos opcionais
  - Sem alteração de email/password

- **`PasswordReset`** - Solicitar reset de senha
  - `email: EmailStr`

- **`PasswordResetConfirm`** - Confirmar reset
  - `token: str`
  - `new_password: str` (com validação)

- **`PasswordChange`** - Trocar senha (autenticado)
  - `current_password: str`
  - `new_password: str` (com validação)

#### Response Schemas

- **`UserResponse`** - Resposta pública de usuário
  - Sem campos sensíveis (password, tokens)
  - Inclui role, status, perfil

- **`UserDetailResponse`** - Resposta detalhada
  - Herda UserResponse
  - Pode incluir campos admin

- **`UserListResponse`** - Usuário em listagem
  - Apenas campos essenciais

#### Admin Schemas

- **`UserAdminUpdate`** - Update com privilégios admin
  - Pode alterar `role`, `is_active`, `is_verified`

### Student Schemas (`student.py`)

#### Request Schemas

- **`StudentCreate`** - Criar novo aluno
  - Validação de idade (2-21 anos)
  - Validação de data de nascimento
  - Máximo de interesses
  - Estrutura de `learning_profile`

- **`StudentUpdate`** - Atualizar aluno
  - Todos os campos opcionais
  - Mesmas validações do create

#### Response Schemas

- **`StudentResponse`** - Resposta completa
  - Inclui learning profile
  - Calcula idade automaticamente
  - ID do teacher

- **`StudentListResponse`** - Aluno em listagem
  - Apenas campos essenciais
  - Sem learning profile

### Activity Schemas (`activity.py`)

#### Request Schemas

- **`ActivityGenerate`** - Gerar com IA
  - `student_id: UUID`
  - `activity_type: ActivityType`
  - `difficulty: DifficultyLevel`
  - `duration_minutes: int` (5-180)
  - `theme: Optional[str]`

- **`ActivityCreate`** - Criar manualmente
  - Todos os campos de conteúdo
  - Validação de listas não vazias
  - Arrays: objectives, materials, instructions

- **`ActivityUpdate`** - Atualizar atividade
  - Todos os campos opcionais
  - Pode alterar status de publicação

#### Response Schemas

- **`ActivityResponse`** - Resposta completa
  - Todo o conteúdo da atividade
  - Metadados de geração
  - IDs relacionados

- **`ActivityListResponse`** - Atividade em listagem
  - Campos essenciais para preview
  - Tipo, dificuldade, duração

#### Filter Schemas

- **`ActivityFilterParams`** - Filtros de query
  - Por tipo, dificuldade, tema
  - Por aluno, geração AI

### Assessment Schemas (`assessment.py`)

#### Request Schemas

- **`AssessmentCreate`** - Criar avaliação
  - `activity_id`, `student_id`
  - Status, engajamento, dificuldade (enums)
  - Observações (máx 2000 chars)
  - Habilidades demonstradas (JSON)
  - Objetivos alcançados (JSON)

- **`AssessmentUpdate`** - Atualizar avaliação
  - Todos os campos opcionais

#### Response Schemas

- **`AssessmentResponse`** - Resposta completa
  - Todos os dados da avaliação
  - IDs relacionados (activity, student, assessor)

- **`AssessmentListResponse`** - Avaliação em listagem
  - Campos essenciais
  - Status, engajamento, dificuldade

#### Filter Schemas

- **`AssessmentFilterParams`** - Filtros
  - Por aluno, atividade
  - Por status, engajamento, dificuldade

#### Analysis Schemas

- **`ProgressAnalysisRequest`** - Solicitar análise
  - `student_id: UUID`
  - `time_period: Optional[str]`

- **`ProgressAnalysisResponse`** - Análise de progresso
  - Summary gerado por IA
  - Pontos fortes, áreas de melhoria
  - Padrões observados
  - Recomendações

## Validações Implementadas

### User

- ✅ Email válido (EmailStr do Pydantic)
- ✅ Senha forte (min 8 chars, maiúscula, minúscula, número, especial)
- ✅ Telefone (10-15 dígitos)
- ✅ Nome (min 2 chars)
- ✅ Bio (max 1000 chars)

### Student

- ✅ Idade entre 2 e 21 anos
- ✅ Data de nascimento não no futuro
- ✅ Máximo 20 interesses
- ✅ Remoção de interesses duplicados
- ✅ Estrutura de learning profile

### Activity

- ✅ Duração entre 5 e 180 minutos
- ✅ Listas não vazias (objectives, materials, instructions)
- ✅ Título min 3 chars, max 500
- ✅ Descrição min 10 chars
- ✅ Tags opcionais

### Assessment

- ✅ Notas max 2000 chars
- ✅ Duração >= 0
- ✅ Enums válidos (status, engajamento, dificuldade)
- ✅ JSON válido para skills/objectives

## Usando os Schemas

### Em Routes

```python
from fastapi import APIRouter, Depends
from backend.app.schemas import (
    UserRegister,
    UserResponse,
    PaginatedResponse,
    PaginationParams
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister) -> UserResponse:
    """Register new user."""
    # user_data já está validado!
    # Criar usuário no banco
    # ...
    return UserResponse.model_validate(user_obj)

@router.get("/users", response_model=PaginatedResponse[UserListResponse])
async def list_users(
    pagination: PaginationParams = Depends()
) -> PaginatedResponse[UserListResponse]:
    """List users with pagination."""
    users = get_users(skip=pagination.skip, limit=pagination.limit)
    total = count_users()

    return PaginatedResponse.create(
        items=users,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )
```

### Validação Manual

```python
from backend.app.schemas import StudentCreate
from pydantic import ValidationError

try:
    student_data = StudentCreate(
        name="João",
        date_of_birth=date(2015, 5, 10),
        diagnosis="TEA Nível 1",
        interests=["dinossauros", "música"]
    )
    # ✅ Dados válidos
except ValidationError as e:
    # ❌ Dados inválidos
    print(e.errors())
```

### Converter de ORM

```python
from backend.app.models import User
from backend.app.schemas import UserResponse

# ORM object → Schema
user_obj = await db.get(User, user_id)
user_response = UserResponse.model_validate(user_obj)

# Retornar na API
return user_response
```

### Paginação

```python
from backend.app.schemas import PaginatedResponse, StudentListResponse

students = await get_students(skip=0, limit=20)
total = await count_students()

response = PaginatedResponse.create(
    items=[StudentListResponse.model_validate(s) for s in students],
    total=total,
    skip=0,
    limit=20
)

# Response automático:
# {
#   "items": [...],
#   "total": 100,
#   "skip": 0,
#   "limit": 20,
#   "has_more": true
# }
```

## Exemplos de Request/Response

### POST /api/v1/auth/register

**Request**:
```json
{
  "email": "teacher@escola.com",
  "password": "SecurePassword123!",
  "full_name": "Maria Silva Santos",
  "role": "teacher",
  "institution": "Escola Municipal João Paulo"
}
```

**Response (201)**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "teacher@escola.com",
  "full_name": "Maria Silva Santos",
  "role": "teacher",
  "is_active": true,
  "is_verified": false,
  "institution": "Escola Municipal João Paulo",
  "created_at": "2025-01-10T10:00:00Z",
  "updated_at": "2025-01-10T10:00:00Z"
}
```

### POST /api/v1/students

**Request**:
```json
{
  "name": "João Silva",
  "date_of_birth": "2015-05-10",
  "diagnosis": "TEA Nível 1",
  "tea_level": "level_1",
  "interests": ["dinossauros", "música", "pintura"],
  "learning_profile": {
    "strengths": ["visual", "memória"],
    "challenges": ["comunicação verbal"],
    "preferences": ["atividades estruturadas"]
  }
}
```

**Response (201)**:
```json
{
  "id": "456e7890-e12b-34d5-a678-901234567890",
  "name": "João Silva",
  "date_of_birth": "2015-05-10",
  "age": 9,
  "diagnosis": "TEA Nível 1",
  "tea_level": "level_1",
  "interests": ["dinossauros", "música", "pintura"],
  "learning_profile": {
    "strengths": ["visual", "memória"],
    "challenges": ["comunicação verbal"],
    "preferences": ["atividades estruturadas"]
  },
  "is_active": true,
  "teacher_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-01-10T11:00:00Z",
  "updated_at": "2025-01-10T11:00:00Z"
}
```

### POST /api/v1/activities/generate

**Request**:
```json
{
  "student_id": "456e7890-e12b-34d5-a678-901234567890",
  "activity_type": "cognitive",
  "difficulty": "medium",
  "duration_minutes": 30,
  "theme": "dinossauros"
}
```

**Response (201)**:
```json
{
  "id": "789e0123-e45b-67d8-a901-234567890123",
  "title": "Descobrindo os Dinossauros",
  "description": "Atividade interativa sobre diferentes tipos de dinossauros...",
  "activity_type": "cognitive",
  "difficulty": "medium",
  "duration_minutes": 30,
  "objectives": [
    "Identificar 3 tipos diferentes de dinossauros",
    "Compreender características básicas"
  ],
  "materials": ["Cartões com imagens", "Lápis de cor"],
  "instructions": ["Passo 1...", "Passo 2..."],
  "theme": "dinossauros",
  "generated_by_ai": true,
  "student_id": "456e7890-e12b-34d5-a678-901234567890",
  "created_at": "2025-01-10T12:00:00Z",
  "updated_at": "2025-01-10T12:00:00Z"
}
```

## Tratamento de Erros

### Erro de Validação (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    },
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Value error, Senha deve conter pelo menos uma letra maiúscula"
    }
  ]
}
```

### Custom Error Response

```json
{
  "message": "Email já cadastrado",
  "details": {
    "error_code": "EMAIL_ALREADY_EXISTS",
    "email": "teacher@escola.com"
  }
}
```

## Pydantic V2 Features Usadas

- ✅ `ConfigDict` (substitui Config class)
- ✅ `model_validate()` (substitui `from_orm()`)
- ✅ `field_validator` (substitui `validator`)
- ✅ Type hints modernos (`List[str]`, `Optional[int]`)
- ✅ `Field()` para validações e metadata
- ✅ Generics (`PaginatedResponse[T]`)
- ✅ `EmailStr` para validação de email
- ✅ JSON Schema extra para examples

## Testing Schemas

```python
import pytest
from datetime import date
from backend.app.schemas import StudentCreate
from pydantic import ValidationError

def test_student_create_valid():
    """Test valid student creation."""
    data = StudentCreate(
        name="João Silva",
        date_of_birth=date(2015, 5, 10),
        diagnosis="TEA Nível 1",
        interests=["música"]
    )
    assert data.name == "João Silva"
    assert data.age is calculated correctly

def test_student_create_invalid_age():
    """Test student with invalid age."""
    with pytest.raises(ValidationError) as exc:
        StudentCreate(
            name="João Silva",
            date_of_birth=date(2023, 1, 1),  # Too young
            diagnosis="TEA"
        )
    assert "Idade deve ser pelo menos" in str(exc.value)

def test_student_create_too_many_interests():
    """Test student with too many interests."""
    with pytest.raises(ValidationError):
        StudentCreate(
            name="João Silva",
            date_of_birth=date(2015, 5, 10),
            diagnosis="TEA",
            interests=["interest"] * 25  # Max is 20
        )
```

## Boas Práticas

1. **Sempre use schemas em routes** - Nunca aceite dicts genéricos
2. **Separe Request e Response** - `UserCreate` vs `UserResponse`
3. **Use herança quando apropriado** - `BaseResponseSchema`
4. **Valide no schema, não no service** - Centralizar validações
5. **Use enums para valores fixos** - Type safety
6. **Documente com Field()** - Description e examples
7. **Use Optional para campos opcionais** - Clareza
8. **Crie schemas para filtros** - Reutilizáveis
9. **Valide custom logic com @field_validator** - Lógica de negócio
10. **Use Generics para reusabilidade** - `PaginatedResponse[T]`

## Status

✅ Common schemas - Completo
✅ User schemas - Completo
✅ Student schemas - Completo
✅ Activity schemas - Completo
✅ Assessment schemas - Completo
✅ Validações - Implementadas
✅ Documentação - Completa
⏳ Unit tests - Pendente

## Recursos Adicionais

- [Pydantic V2 Docs](https://docs.pydantic.dev/latest/)
- [FastAPI Schemas](https://fastapi.tiangolo.com/tutorial/response-model/)
- [JSON Schema](https://json-schema.org/)
