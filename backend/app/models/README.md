# Database Models - EduAutismo IA

## Visão Geral

Este diretório contém todos os modelos de banco de dados do projeto, implementados com SQLAlchemy ORM e suporte assíncrono.

## Modelos Implementados

### 1. User (`user.py`)

**Descrição**: Representa usuários do sistema (professores, administradores, pais, terapeutas).

**Campos principais**:
- `email` - Email único (autenticação)
- `hashed_password` - Senha hash (bcrypt)
- `full_name` - Nome completo
- `role` - Papel no sistema (admin, teacher, parent, therapist)
- `is_active` - Status da conta
- `is_verified` - Email verificado
- `last_login` - Último login
- `reset_token` - Token de recuperação de senha
- `verification_token` - Token de verificação de email

**Relacionamentos**:
- `students` - Lista de alunos associados (1:N)

**Propriedades úteis**:
- `is_admin` - Verifica se é admin
- `is_teacher` - Verifica se é professor
- `update_last_login()` - Atualiza timestamp do último login

### 2. Student (`student.py`)

**Descrição**: Representa alunos com TEA (Transtorno do Espectro Autista).

**Campos principais**:
- `name` - Nome do aluno
- `date_of_birth` - Data de nascimento
- `age` - Idade atual
- `diagnosis` - Diagnóstico detalhado
- `tea_level` - Nível de suporte TEA (1, 2 ou 3)
- `interests` - Lista de interesses (ARRAY)
- `learning_profile` - Perfil de aprendizagem (JSON)
  - `strengths` - Pontos fortes
  - `challenges` - Desafios
  - `preferences` - Preferências de aprendizado
- `teacher_id` - Professor responsável

**Relacionamentos**:
- `teacher` - Professor responsável (N:1)
- `activities` - Atividades geradas (1:N)
- `assessments` - Avaliações recebidas (1:N)

**Métodos úteis**:
- `age_calculated` - Calcula idade atual a partir da data de nascimento
- `get_strengths()` - Retorna pontos fortes do perfil
- `get_challenges()` - Retorna desafios do perfil
- `to_profile_dict()` - Converte para dict para serviços de IA

### 3. Activity (`activity.py`)

**Descrição**: Representa atividades educacionais personalizadas.

**Campos principais**:
- `title` - Título da atividade
- `description` - Descrição detalhada
- `activity_type` - Tipo (cognitive, social, motor, sensory, communication, etc.)
- `difficulty` - Nível de dificuldade (very_easy, easy, medium, hard, very_hard)
- `duration_minutes` - Duração estimada
- `objectives` - Lista de objetivos (ARRAY)
- `materials` - Materiais necessários (ARRAY)
- `instructions` - Instruções passo a passo (ARRAY)
- `adaptations` - Adaptações sugeridas (ARRAY)
- `visual_supports` - Suportes visuais (ARRAY)
- `success_criteria` - Critérios de sucesso (ARRAY)
- `theme` - Tema/tópico
- `generated_by_ai` - Gerada por IA?
- `generation_metadata` - Metadados da geração (JSON)

**Relacionamentos**:
- `student` - Aluno alvo (N:1)
- `created_by` - Usuário criador (N:1)
- `assessments` - Avaliações da atividade (1:N)

**Métodos úteis**:
- `to_dict()` - Converte para dict para processamento

### 4. Assessment (`assessment.py`)

**Descrição**: Representa avaliações de atividades completadas.

**Campos principais**:
- `completion_status` - Status (not_started, in_progress, completed, abandoned, needs_assistance)
- `engagement_level` - Nível de engajamento (none, low, medium, high, very_high)
- `difficulty_rating` - Avaliação de dificuldade (too_easy, appropriate, too_hard, etc.)
- `actual_duration_minutes` - Tempo real gasto
- `notes` - Observações do professor
- `strengths_observed` - Pontos fortes observados
- `challenges_observed` - Dificuldades observadas
- `recommendations` - Recomendações para futuro
- `skills_demonstrated` - Habilidades demonstradas (JSON)
- `objectives_met` - Objetivos alcançados (JSON)

**Relacionamentos**:
- `activity` - Atividade avaliada (N:1)
- `student` - Aluno avaliado (N:1)
- `assessed_by` - Avaliador (N:1)

**Propriedades úteis**:
- `is_successful` - Atividade foi completada com sucesso?
- `needs_adjustment` - Dificuldade precisa ajuste?
- `to_dict()` - Converte para dict para análise de IA

## Diagrama de Relacionamentos

```
┌─────────────┐
│    User     │
│  (Teacher)  │
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────┐        1:N        ┌─────────────┐
│   Student   │◄─────────────────►│  Activity   │
└──────┬──────┘                   └──────┬──────┘
       │                                 │
       │ 1:N                             │ 1:N
       │                                 │
       ▼                                 ▼
┌─────────────────────────────────────────────┐
│              Assessment                     │
│  (Relacionado com Student e Activity)      │
└─────────────────────────────────────────────┘
```

## Base Classes

### BaseModel

Classe base para todos os modelos, fornece:
- `id` (UUID) - Chave primária
- `created_at` (DateTime) - Data de criação
- `updated_at` (DateTime) - Data de atualização
- `to_dict()` - Conversão para dicionário
- `__tablename__` - Geração automática do nome da tabela

### Mixins

- **UUIDMixin** - Adiciona campo `id` UUID
- **TimestampMixin** - Adiciona campos `created_at` e `updated_at`

## Tipos de Dados Especiais

### PostgreSQL Arrays
Usado para listas:
```python
interests: Mapped[List[str]] = mapped_column(ARRAY(String))
```

### JSONB
Usado para dados estruturados flexíveis:
```python
learning_profile: Mapped[Dict[str, Any]] = mapped_column(JSONB)
```

### Enums
Tipos enumerados para valores fixos:
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
```

## Usando os Models

### Criar Registro

```python
from backend.app.models import User
from backend.app.db import get_db

async def create_user(db: AsyncSession):
    user = User(
        email="teacher@escola.com",
        hashed_password=hash_password("senha123"),
        full_name="Maria Silva",
        role=UserRole.TEACHER
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### Consultar Registros

```python
from sqlalchemy import select

# Buscar por ID
user = await db.get(User, user_id)

# Buscar com filtro
result = await db.execute(
    select(User).where(User.email == "teacher@escola.com")
)
user = result.scalar_one_or_none()

# Buscar todos
result = await db.execute(select(User))
users = result.scalars().all()

# Buscar com paginação
result = await db.execute(
    select(User).offset(0).limit(20)
)
users = result.scalars().all()
```

### Atualizar Registro

```python
user = await db.get(User, user_id)
user.full_name = "Maria Santos Silva"
await db.commit()
await db.refresh(user)
```

### Deletar Registro

```python
user = await db.get(User, user_id)
await db.delete(user)
await db.commit()
```

### Relacionamentos

```python
# Lazy loading (selectin)
user = await db.get(User, user_id)
students = user.students  # Já carregado automaticamente

# Eager loading com relacionamentos
result = await db.execute(
    select(Student)
    .options(selectinload(Student.activities))
    .where(Student.teacher_id == user_id)
)
students = result.scalars().all()
```

### Trabalhando com JSON

```python
# Criar student com learning_profile
student = Student(
    name="João",
    learning_profile={
        "strengths": ["visual", "memoria"],
        "challenges": ["comunicacao_verbal"],
        "preferences": ["atividades_visuais"]
    }
)

# Acessar dados JSON
strengths = student.learning_profile["strengths"]

# Usar métodos auxiliares
strengths = student.get_strengths()
```

## Migrations

### Aplicar Migrations

```bash
# Dentro do container
docker-compose exec api alembic upgrade head

# Ou com make
make db-migrate
```

### Criar Nova Migration

```bash
# Após modificar models
docker-compose exec api alembic revision --autogenerate -m "Descrição"

# Revisar arquivo gerado
vim backend/alembic/versions/XXXXX_descricao.py

# Aplicar
docker-compose exec api alembic upgrade head
```

### Reverter Migration

```bash
# Reverter última
docker-compose exec api alembic downgrade -1

# Reverter todas
docker-compose exec api alembic downgrade base
```

## Índices e Performance

### Índices Criados

1. **users.email** - Busca rápida por email (autenticação)
2. **students.name** - Busca por nome de aluno
3. **students.teacher_id** - Join com teacher
4. **activities.title** - Busca por título
5. **activities.activity_type** - Filtro por tipo
6. **activities.tags (GIN)** - Busca em arrays de tags
7. **students.interests (GIN)** - Busca em arrays de interesses
8. **assessments.completion_status** - Filtro por status

### Otimizações

- **Lazy loading com selectin** - Evita problema N+1
- **GIN indexes** - Para arrays e JSONB
- **Cascade delete** - Limpeza automática de relacionamentos
- **Pool de conexões** - Configurado no session.py

## Validações

Validações são feitas nos schemas Pydantic, não nos models:
- Models = Estrutura do banco de dados
- Schemas = Validação de entrada/saída da API

## Seed Data (Dados de Teste)

Para popular o banco com dados de teste:

```bash
# Criar script de seed
docker-compose exec api python backend/scripts/seed_database.py
```

## Testes

```python
import pytest
from backend.app.models import User

@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        email="test@test.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    assert user.id is not None
    assert user.email == "test@test.com"
```

## Boas Práticas

1. **Sempre use `get_db()` como dependency** - Gerencia sessões automaticamente
2. **Commit após mudanças** - `await db.commit()`
3. **Refresh após commit** - `await db.refresh(obj)` para obter valores gerados
4. **Use type hints** - `Mapped[str]` para melhor IDE support
5. **Relacionamentos com lazy="selectin"** - Evita N+1 queries
6. **Valide nos Schemas, não nos Models** - Separação de responsabilidades
7. **Use Enums para valores fixos** - Type safety
8. **JSONB para dados flexíveis** - Mas com estrutura conhecida
9. **Arrays para listas simples** - Mais eficiente que tabelas separadas
10. **Índices em campos de busca/filtro** - Performance

## Troubleshooting

### Erro: "relation does not exist"
```bash
# Aplicar migrations
alembic upgrade head
```

### Erro: "column does not exist"
```bash
# Recriar migration após mudanças
alembic revision --autogenerate -m "Update schema"
alembic upgrade head
```

### Erro: "asyncpg.exceptions.UniqueViolationError"
```python
# Verificar se email já existe antes de criar
existing = await db.execute(
    select(User).where(User.email == email)
)
if existing.scalar_one_or_none():
    raise ValueError("Email já cadastrado")
```

## Recursos Adicionais

- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [AsyncPG Docs](https://magicstack.github.io/asyncpg/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## Status Atual

✅ **User Model** - Completo
✅ **Student Model** - Completo
✅ **Activity Model** - Completo
✅ **Assessment Model** - Completo
✅ **Relationships** - Configurados
✅ **Indexes** - Otimizados
✅ **Initial Migration** - Criada
⏳ **Seed Data** - Pendente
⏳ **Integration Tests** - Pendente
