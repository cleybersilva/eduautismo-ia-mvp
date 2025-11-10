# Services Layer - EduAutismo IA

## Visão Geral

A camada de Services contém toda a lógica de negócio da aplicação. Os services são responsáveis por:

- Implementar regras de negócio
- Coordenar operações entre models e schemas
- Integrar com serviços externos (OpenAI)
- Gerenciar transações de banco de dados
- Aplicar validações de negócio
- Tratar exceções específicas
- Registrar logs de operações

## Arquitetura

```
Routes (FastAPI)
    ↓
Services (Business Logic)
    ↓
Models (Database ORM)
    ↓
PostgreSQL Database

Services também se comunicam com:
- NLP Service (OpenAI)
- Schemas (Validação)
- Exceptions (Tratamento de erros)
- Logger (Registro de eventos)
```

## Services Implementados

### 1. StudentService (`student_service.py`)

**Responsabilidade**: Gerenciamento de alunos

#### Métodos

##### `create_student(db, student_data, teacher_id) -> Student`

Cria novo aluno.

- **Calcula idade** automaticamente a partir da data de nascimento
- **Associa ao professor** (teacher_id)
- **Valida dados** via schema StudentCreate
- **Registra log** da criação

**Exemplo**:
```python
from backend.app.services import StudentService
from backend.app.schemas import StudentCreate

student_data = StudentCreate(
    name="João Silva",
    date_of_birth=date(2015, 5, 10),
    diagnosis="TEA Nível 1",
    interests=["dinossauros", "música"]
)

student = await StudentService.create_student(
    db=db,
    student_data=student_data,
    teacher_id=teacher_id
)
```

##### `get_student(db, student_id, teacher_id=None) -> Student`

Busca aluno por ID.

- **Verifica permissão** se teacher_id fornecido
- **Lança StudentNotFoundError** se não encontrado
- **Lança PermissionDeniedError** se professor não é o dono

**Exemplo**:
```python
student = await StudentService.get_student(
    db=db,
    student_id=student_id,
    teacher_id=current_user.id  # Verifica permissão
)
```

##### `list_students(db, teacher_id=None, skip=0, limit=20, is_active=None) -> tuple[List[Student], int]`

Lista alunos com paginação e filtros.

- **Retorna** (lista de alunos, total count)
- **Filtra por professor** se teacher_id fornecido
- **Filtra por status** se is_active fornecido
- **Ordena** por data de criação (mais recente primeiro)

**Exemplo**:
```python
students, total = await StudentService.list_students(
    db=db,
    teacher_id=current_user.id,
    skip=0,
    limit=20,
    is_active=True
)
```

##### `update_student(db, student_id, student_data, teacher_id=None) -> Student`

Atualiza dados do aluno.

- **Recalcula idade** se data de nascimento mudou
- **Atualiza apenas campos** fornecidos (exclude_unset)
- **Verifica permissão** antes de atualizar

**Exemplo**:
```python
update_data = StudentUpdate(
    interests=["dinossauros", "música", "robótica"]
)

student = await StudentService.update_student(
    db=db,
    student_id=student_id,
    student_data=update_data,
    teacher_id=current_user.id
)
```

##### `delete_student(db, student_id, teacher_id=None) -> None`

Desativa aluno (soft delete).

- **Não deleta** fisicamente do banco
- **Define is_active=False**
- **Mantém histórico** de atividades e avaliações

##### `get_student_profile(db, student_id, teacher_id=None) -> dict`

Retorna perfil formatado para IA.

- **Formato otimizado** para NLP service
- **Inclui** interesses, pontos fortes, desafios
- **Usado** na geração de atividades

##### `search_students(db, query, teacher_id=None, skip=0, limit=20) -> tuple[List[Student], int]`

Busca alunos por nome.

- **Case-insensitive** search
- **Busca parcial** (ILIKE)
- **Paginação** incluída

---

### 2. ActivityService (`activity_service.py`)

**Responsabilidade**: Gerenciamento de atividades e geração com IA

#### Métodos

##### `generate_activity(db, activity_data, teacher_id) -> Activity`

Gera atividade usando IA.

- **Busca perfil do aluno** para personalização
- **Chama NLP Service** com parâmetros
- **Cria atividade** com conteúdo gerado
- **Salva metadados** de geração
- **Marca como AI-generated**

**Fluxo**:
1. Valida que aluno existe
2. Verifica permissão do professor
3. Obtém perfil do aluno
4. Chama OpenAI para gerar conteúdo
5. Cria atividade no banco
6. Registra log

**Exemplo**:
```python
from backend.app.services import ActivityService
from backend.app.schemas import ActivityGenerate

activity_data = ActivityGenerate(
    student_id=student_id,
    activity_type=ActivityType.COGNITIVE,
    difficulty=DifficultyLevel.MEDIUM,
    duration_minutes=30,
    theme="dinossauros"
)

activity = await ActivityService.generate_activity(
    db=db,
    activity_data=activity_data,
    teacher_id=current_user.id
)
```

##### `create_activity(db, activity_data, teacher_id) -> Activity`

Cria atividade manualmente.

- **Sem uso de IA**
- **Todos os campos** fornecidos pelo professor
- **Valida** via schema ActivityCreate

**Exemplo**:
```python
activity_data = ActivityCreate(
    student_id=student_id,
    title="Descobrindo Dinossauros",
    description="Atividade sobre tipos de dinossauros...",
    activity_type=ActivityType.COGNITIVE,
    difficulty=DifficultyLevel.MEDIUM,
    duration_minutes=30,
    objectives=["Identificar 3 tipos de dinossauros"],
    materials=["Cartões com imagens", "Lápis de cor"],
    instructions=["Passo 1...", "Passo 2..."]
)

activity = await ActivityService.create_activity(
    db=db,
    activity_data=activity_data,
    teacher_id=current_user.id
)
```

##### `get_activity(db, activity_id, teacher_id=None) -> Activity`

Busca atividade por ID.

- **Verifica permissão** via student do activity
- **Lança exceções** se não encontrado ou sem permissão

##### `list_activities(db, student_id=None, teacher_id=None, activity_type=None, difficulty=None, skip=0, limit=20) -> tuple[List[Activity], int]`

Lista atividades com múltiplos filtros.

- **Filtros combinados** (AND logic)
- **Apenas atividades publicadas**
- **Ordenação** por data de criação

**Exemplo**:
```python
activities, total = await ActivityService.list_activities(
    db=db,
    student_id=student_id,
    activity_type=ActivityType.COGNITIVE,
    difficulty=DifficultyLevel.MEDIUM,
    skip=0,
    limit=20
)
```

##### `update_activity(db, activity_id, activity_data, teacher_id=None) -> Activity`

Atualiza atividade.

- **Partial update** (exclude_unset)
- **Pode alterar** status de publicação

##### `delete_activity(db, activity_id, teacher_id=None) -> None`

Despublica atividade (soft delete).

- **Define is_published=False**
- **Mantém no banco** para histórico

##### `get_activities_by_theme(db, theme, teacher_id=None, skip=0, limit=20) -> tuple[List[Activity], int]`

Busca atividades por tema.

- **Case-insensitive** search
- **Busca parcial** no campo theme

---

### 3. AssessmentService (`assessment_service.py`)

**Responsabilidade**: Gerenciamento de avaliações e análise de progresso

#### Métodos

##### `create_assessment(db, assessment_data, teacher_id) -> Assessment`

Cria avaliação de atividade.

- **Valida** activity e student existem
- **Verifica permissão** do professor
- **Associa avaliador** (assessed_by_id)

**Exemplo**:
```python
from backend.app.services import AssessmentService
from backend.app.schemas import AssessmentCreate

assessment_data = AssessmentCreate(
    activity_id=activity_id,
    student_id=student_id,
    completion_status=CompletionStatus.COMPLETED,
    engagement_level=EngagementLevel.HIGH,
    difficulty_rating=DifficultyRating.APPROPRIATE,
    actual_duration_minutes=28,
    notes="Aluno demonstrou ótimo engajamento..."
)

assessment = await AssessmentService.create_assessment(
    db=db,
    assessment_data=assessment_data,
    teacher_id=current_user.id
)
```

##### `get_assessment(db, assessment_id, teacher_id=None) -> Assessment`

Busca avaliação por ID.

##### `list_assessments(db, student_id=None, activity_id=None, teacher_id=None, completion_status=None, skip=0, limit=20) -> tuple[List[Assessment], int]`

Lista avaliações com filtros.

- **Múltiplos filtros** disponíveis
- **Ordenação** por data de criação

**Exemplo**:
```python
assessments, total = await AssessmentService.list_assessments(
    db=db,
    student_id=student_id,
    completion_status=CompletionStatus.COMPLETED,
    skip=0,
    limit=20
)
```

##### `update_assessment(db, assessment_id, assessment_data, teacher_id=None) -> Assessment`

Atualiza avaliação.

##### `delete_assessment(db, assessment_id, teacher_id=None) -> None`

Deleta avaliação (hard delete).

- **Remoção física** do banco
- **Use com cuidado**

##### `analyze_student_progress(db, student_id, teacher_id=None, time_period=None) -> dict`

Analisa progresso do aluno usando IA. **⭐ FEATURE PRINCIPAL**

- **Busca até 50** avaliações mais recentes
- **Chama NLP Service** para análise
- **Retorna insights** gerados por IA

**Retorna**:
```python
{
    "student_id": UUID,
    "summary": "Resumo geral do progresso...",
    "strengths": ["Ponto forte 1", "Ponto forte 2"],
    "areas_for_improvement": ["Área 1", "Área 2"],
    "patterns_observed": ["Padrão 1", "Padrão 2"],
    "recommendations": ["Recomendação 1", "Recomendação 2"]
}
```

**Exemplo**:
```python
progress = await AssessmentService.analyze_student_progress(
    db=db,
    student_id=student_id,
    teacher_id=current_user.id,
    time_period="last month"
)

print(progress["summary"])
print(progress["recommendations"])
```

##### `get_student_statistics(db, student_id, teacher_id=None) -> dict`

Calcula estatísticas do aluno.

- **Total de atividades** criadas
- **Total de avaliações**
- **Atividades completadas**
- **Taxa de conclusão** (%)
- **Engajamento médio** (0-4)

**Retorna**:
```python
{
    "total_activities": 25,
    "total_assessments": 20,
    "completed_activities": 18,
    "completion_rate": 90.0,
    "average_engagement": 3.2  # 0=none, 4=very_high
}
```

---

### 4. NLPService (`nlp_service.py`)

**Responsabilidade**: Integração com OpenAI

#### Métodos Principais

##### `generate_activity(student_profile, activity_type, difficulty, duration_minutes, theme=None) -> GeneratedActivity`

Gera atividade com IA.

- **Structured output** com Pydantic
- **Prompts especializados** para TEA
- **Logging de tokens** e latência

##### `analyze_progress(student_profile, assessments, time_period=None) -> ProgressAnalysis`

Analisa progresso com IA.

- **Identifica padrões** nas avaliações
- **Gera recomendações** personalizadas
- **Summary narrativo**

##### `generate_recommendations(student_profile, recent_activities, progress_summary=None) -> List[Recommendation]`

Gera recomendações.

- **3-5 recomendações** práticas
- **Priorizadas** (high, medium, low)
- **Categorizadas** (activity, strategy, resource)

##### `test_connection() -> bool`

Testa conexão com OpenAI.

- **Usado em health checks**
- **Verifica API key** válida

---

## Padrões e Boas Práticas

### 1. Tratamento de Erros

Todos os services usam exceções customizadas:

```python
from backend.app.core.exceptions import (
    StudentNotFoundError,
    PermissionDeniedError,
    OpenAIError,
)

try:
    student = await StudentService.get_student(db, student_id, teacher_id)
except StudentNotFoundError:
    # Retornar 404
    pass
except PermissionDeniedError:
    # Retornar 403
    pass
```

### 2. Logging

Todas as operações importantes são logadas:

```python
logger.info(f"Student created: {student.id} by teacher {teacher_id}")
logger.error(f"Error creating student: {e}")
```

### 3. Permissões

Verificação de permissões em dois níveis:

1. **Opcional** - `teacher_id=None` (admin pode ver tudo)
2. **Obrigatória** - `teacher_id` sempre verificado

```python
# Verifica apenas se teacher_id fornecido
student = await StudentService.get_student(db, student_id, teacher_id=None)

# Sempre verifica
student = await StudentService.get_student(db, student_id, teacher_id=current_user.id)
```

### 4. Transações

Todas as escritas são transacionadas:

```python
try:
    db.add(student)
    await db.commit()
    await db.refresh(student)
except Exception as e:
    await db.rollback()
    raise
```

### 5. Paginação

Sempre retornar `(items, total)`:

```python
students, total = await StudentService.list_students(
    db=db,
    skip=0,
    limit=20
)

# Para criar PaginatedResponse
return PaginatedResponse.create(
    items=students,
    total=total,
    skip=0,
    limit=20
)
```

## Usando Services em Routes

### Exemplo Completo

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db import get_db
from backend.app.services import StudentService
from backend.app.schemas import (
    StudentCreate,
    StudentResponse,
    PaginatedResponse,
    PaginationParams,
)
from backend.app.api.deps import get_current_user
from backend.app.models import User

router = APIRouter()


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentResponse:
    """Create new student."""
    student = await StudentService.create_student(
        db=db,
        student_data=student_data,
        teacher_id=current_user.id,
    )
    return StudentResponse.model_validate(student)


@router.get("/students", response_model=PaginatedResponse[StudentResponse])
async def list_students(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[StudentResponse]:
    """List students."""
    students, total = await StudentService.list_students(
        db=db,
        teacher_id=current_user.id,  # Filter by current teacher
        skip=pagination.skip,
        limit=pagination.limit,
    )

    return PaginatedResponse.create(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentResponse:
    """Get student by ID."""
    student = await StudentService.get_student(
        db=db,
        student_id=student_id,
        teacher_id=current_user.id,  # Check permission
    )
    return StudentResponse.model_validate(student)
```

## Testando Services

```python
import pytest
from datetime import date
from backend.app.services import StudentService
from backend.app.schemas import StudentCreate

@pytest.mark.asyncio
async def test_create_student(db_session, teacher_user):
    """Test student creation."""
    student_data = StudentCreate(
        name="João Silva",
        date_of_birth=date(2015, 5, 10),
        diagnosis="TEA Nível 1",
        interests=["música"]
    )

    student = await StudentService.create_student(
        db=db_session,
        student_data=student_data,
        teacher_id=teacher_user.id
    )

    assert student.id is not None
    assert student.name == "João Silva"
    assert student.age == 9  # Calculated
    assert student.teacher_id == teacher_user.id


@pytest.mark.asyncio
async def test_get_student_permission_denied(db_session, student, other_teacher):
    """Test permission check."""
    with pytest.raises(PermissionDeniedError):
        await StudentService.get_student(
            db=db_session,
            student_id=student.id,
            teacher_id=other_teacher.id  # Different teacher
        )
```

## Fluxos Completos

### Fluxo 1: Criar Aluno e Gerar Atividade

```python
# 1. Criar aluno
student_data = StudentCreate(...)
student = await StudentService.create_student(db, student_data, teacher_id)

# 2. Gerar atividade personalizada
activity_data = ActivityGenerate(
    student_id=student.id,
    activity_type=ActivityType.COGNITIVE,
    difficulty=DifficultyLevel.MEDIUM,
    duration_minutes=30,
    theme="dinossauros"
)
activity = await ActivityService.generate_activity(db, activity_data, teacher_id)

# 3. Avaliar atividade
assessment_data = AssessmentCreate(
    activity_id=activity.id,
    student_id=student.id,
    completion_status=CompletionStatus.COMPLETED,
    engagement_level=EngagementLevel.HIGH,
    ...
)
assessment = await AssessmentService.create_assessment(db, assessment_data, teacher_id)

# 4. Analisar progresso
progress = await AssessmentService.analyze_student_progress(
    db, student.id, teacher_id
)
```

### Fluxo 2: Buscar e Filtrar Atividades

```python
# Buscar atividades de um aluno
activities, total = await ActivityService.list_activities(
    db=db,
    student_id=student_id,
    skip=0,
    limit=20
)

# Filtrar por tipo e dificuldade
cognitive_activities, total = await ActivityService.list_activities(
    db=db,
    student_id=student_id,
    activity_type=ActivityType.COGNITIVE,
    difficulty=DifficultyLevel.MEDIUM,
    skip=0,
    limit=10
)

# Buscar por tema
dino_activities, total = await ActivityService.get_activities_by_theme(
    db=db,
    theme="dinossauros",
    teacher_id=teacher_id,
    skip=0,
    limit=10
)
```

## Dependências

Services dependem de:

- ✅ Models (SQLAlchemy)
- ✅ Schemas (Pydantic)
- ✅ Exceptions (Custom)
- ✅ Logger (Logging)
- ✅ Constants (Enums)
- ✅ NLP Service (OpenAI)

## Status

✅ StudentService - Completo (9 métodos)
✅ ActivityService - Completo (7 métodos)
✅ AssessmentService - Completo (7 métodos)
✅ NLPService - Completo (4 métodos)
✅ Tratamento de erros - Implementado
✅ Logging - Implementado
✅ Permissões - Implementado
✅ Transações - Implementadas
✅ Documentação - Completa

⏳ Unit tests - Pendente
⏳ Integration tests - Pendente

## Próximos Passos

1. **Routes Implementation** - Usar services nas routes
2. **Unit Tests** - Testar cada método
3. **Integration Tests** - Testar fluxos completos
4. **Caching** - Adicionar cache em leituras
5. **Background Tasks** - Análises assíncronas

## Recursos Adicionais

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Models](https://docs.pydantic.dev/latest/)
