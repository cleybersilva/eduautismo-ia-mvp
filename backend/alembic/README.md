# Database Migrations - Alembic

Este diretório contém as migrations do banco de dados usando Alembic.

## Comandos Comuns

### Criar uma Nova Migration

```bash
# Migration automática (detecta mudanças nos models)
alembic revision --autogenerate -m "Descrição da mudança"

# Migration manual (arquivo vazio para editar)
alembic revision -m "Descrição da mudança"
```

### Aplicar Migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Aplicar uma migration específica
alembic upgrade <revision_id>

# Aplicar próxima migration
alembic upgrade +1
```

### Reverter Migrations

```bash
# Reverter última migration
alembic downgrade -1

# Reverter todas as migrations
alembic downgrade base

# Reverter para uma revision específica
alembic downgrade <revision_id>
```

### Visualizar Histórico

```bash
# Ver histórico de migrations
alembic history

# Ver histórico com detalhes
alembic history --verbose

# Ver current revision
alembic current

# Ver migrations pendentes
alembic show head
```

## Usando com Docker

```bash
# Executar migrations dentro do container
docker-compose exec api alembic upgrade head

# Criar nova migration
docker-compose exec api alembic revision --autogenerate -m "Descrição"

# Ver histórico
docker-compose exec api alembic history
```

## Usando com Makefile

```bash
# Aplicar migrations
make db-migrate

# Criar nova migration
make db-migration message="Descrição da mudança"

# Reverter última migration
make db-downgrade
```

## Estrutura de Diretórios

```
backend/alembic/
├── env.py                 # Configuração do ambiente Alembic
├── script.py.mako         # Template para novos scripts de migration
├── README.md              # Este arquivo
└── versions/              # Diretório de migrations
    ├── 20250109_initial.py
    ├── 20250110_add_students.py
    └── ...
```

## Boas Práticas

### 1. Sempre Revise Migrations Automáticas

Migrations geradas com `--autogenerate` devem ser revisadas antes de aplicar:

```bash
# Após criar migration
vim backend/alembic/versions/XXXXX_descricao.py
```

### 2. Teste Migrations Localmente

```bash
# Aplicar
alembic upgrade head

# Testar rollback
alembic downgrade -1

# Aplicar novamente
alembic upgrade head
```

### 3. Nomeie Descritivamente

```bash
# ✅ Bom
alembic revision --autogenerate -m "Add student_interests table"

# ❌ Ruim
alembic revision --autogenerate -m "Update"
```

### 4. Faça Commit das Migrations

```bash
git add backend/alembic/versions/XXXXX_*.py
git commit -m "Add migration: description"
```

### 5. Migrations Devem Ser Idempotentes

Certifique-se de que migrations podem ser aplicadas múltiplas vezes sem erro:

```python
# ✅ Bom - Verifica se existe antes de criar
def upgrade():
    if not op.get_bind().has_table('students'):
        op.create_table('students', ...)

# ❌ Ruim - Falha se executada duas vezes
def upgrade():
    op.create_table('students', ...)
```

## Exemplo de Migration

```python
"""Add student preferences

Revision ID: abc123def456
Revises: xyz789ghi012
Create Date: 2025-01-09 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = 'xyz789ghi012'


def upgrade():
    """Add preferences column to students table."""
    op.add_column(
        'students',
        sa.Column('preferences', sa.JSON(), nullable=True)
    )

    # Add index for better query performance
    op.create_index(
        'ix_students_preferences',
        'students',
        ['preferences'],
        postgresql_using='gin'
    )


def downgrade():
    """Remove preferences column."""
    op.drop_index('ix_students_preferences', table_name='students')
    op.drop_column('students', 'preferences')
```

## Troubleshooting

### Erro: "Can't locate revision identified by..."

```bash
# Resincronizar com banco de dados
alembic stamp head
```

### Erro: "Target database is not up to date"

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head
```

### Erro: "Multiple head revisions are present"

```bash
# Mesclar branches
alembic merge heads -m "Merge migration branches"
```

### Conflitos de Migration em Equipe

1. Sempre puxe as últimas mudanças antes de criar migration:
   ```bash
   git pull
   ```

2. Se houver conflitos, resolva e recrie a migration:
   ```bash
   # Deletar migration local
   rm backend/alembic/versions/XXXXX_sua_migration.py

   # Aplicar migrations do remote
   alembic upgrade head

   # Recriar sua migration
   alembic revision --autogenerate -m "Sua descrição"
   ```

## Database Schema Versioning

Cada migration tem um ID único (revision) que rastreia o estado do schema:

```
base → rev1 → rev2 → rev3 → head
       (initial) (add_users) (add_students) (current)
```

## Recursos Adicionais

- [Documentação Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

## Comandos Make Disponíveis

```bash
make db-migrate          # Aplicar migrations
make db-migration        # Criar nova migration
make db-downgrade        # Reverter última migration
make db-reset            # Resetar banco de dados (CUIDADO!)
make db-shell            # Abrir shell do PostgreSQL
```

Para mais informações sobre comandos Make, execute:
```bash
make help
```
