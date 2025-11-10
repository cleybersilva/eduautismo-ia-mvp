# Guia de Validação de Estrutura

## Visão Geral

O projeto EduAutismo IA inclui um sistema abrangente de validação de estrutura que garante que seu projeto mantenha a organização correta de diretórios e arquivos. Este sistema pode criar automaticamente arquivos ausentes com templates, facilitando a manutenção da consistência em toda a base de código.

## Início Rápido

```bash
# 1. Valide a estrutura e gere relatório
python scripts/check_structure.py --report-only

# 2. Crie todos os arquivos ausentes de Prioridade 1 (Críticos)
python scripts/check_structure.py --create-missing --priority 1

# 3. Crie todos os arquivos ausentes de Prioridade 1 e 2
python scripts/check_structure.py --create-missing --priority 2

# 4. Execute o fluxo completo de validação
./scripts/validate_structure.sh
```

## Sistema de Prioridades

Os arquivos são classificados em três níveis de prioridade:

### Prioridade 1: Crítico (Deve Ter)
Estes são arquivos essenciais sem os quais o projeto não pode funcionar:
- Arquivos `__init__.py` para todos os pacotes Python
- Arquivos de inicialização de pacotes
- Marcadores de módulos principais

**Exemplo:**
```bash
python scripts/check_structure.py --create-missing --priority 1
```

### Prioridade 2: Importante (Deveria Ter)
Estes arquivos fornecem funcionalidade principal e são necessários para uma aplicação completa:
- Modelos de banco de dados (Student, Activity, Assessment)
- Schemas Pydantic para validação
- Serviços de lógica de negócio
- Handlers de rotas da API
- Configuração de testes (conftest.py)
- Dependências de autenticação

**Exemplo:**
```bash
python scripts/check_structure.py --create-missing --priority 2
```

### Prioridade 3: Opcional (Bom Ter)
Arquivos de configuração e qualidade de vida:
- `pytest.ini` - Configuração de testes
- `.coveragerc` - Configurações de cobertura de código
- Utilitários adicionais

**Exemplo:**
```bash
python scripts/check_structure.py --create-missing --priority 3
```

## Ferramentas

### 1. check_structure.py

O script principal de validação com capacidades de geração de arquivos.

#### Uso

```bash
python scripts/check_structure.py [OPÇÕES]
```

#### Opções

- `--verbose`, `-v` - Mostrar informações detalhadas sobre todas as verificações
- `--create-missing` - Criar arquivos ausentes com templates
- `--priority N` - Nível máximo de prioridade para criar (1-3)
- `--report-only` - Apenas reportar, não criar nada
- `--project-root PATH` - Caminho para raiz do projeto (padrão: diretório atual)

#### Exemplos

```bash
# Apenas validar e reportar
python scripts/check_structure.py --report-only

# Criar apenas arquivos críticos
python scripts/check_structure.py --create-missing --priority 1

# Criar arquivos críticos + importantes com saída verbosa
python scripts/check_structure.py --create-missing --priority 2 --verbose

# Validação completa com arquivos opcionais
python scripts/check_structure.py --create-missing --priority 3
```

#### Saída

O script fornece:
- Porcentagem de conclusão de diretórios
- Porcentagem de conclusão de arquivos por prioridade
- Porcentagem geral de conclusão do projeto
- Lista detalhada de itens ausentes
- Indicador de status (Excelente/Bom/Razoável/Ruim)

**Exemplo de Saída:**
```
EduAutismo IA - Validador de Estrutura do Projeto
Raiz do projeto: /caminho/para/projeto
Data: 2025-11-09 22:30:00

======================================================================
Resumo da Validação da Estrutura do Projeto
======================================================================

Diretórios:
  Presentes: 38/38 (100.0%)

Arquivos:
  Presentes: 29/31 (93.5%)
  Ausentes: 2/31

  Ausentes por Prioridade:
    Prioridade 3 (Opcional): 2 arquivos

Conclusão Geral: 97.1%

Status: ✓ Excelente - Estrutura do projeto está completa
======================================================================
```

### 2. validate_structure.sh

Fluxo completo de validação com múltiplas verificações.

#### Uso

```bash
./scripts/validate_structure.sh [OPÇÕES]
```

#### Opções

- `--fix` - Criar automaticamente arquivos ausentes (Prioridade 1 por padrão)
- `--priority N` - Definir nível de prioridade para criação (1-3)
- `--help`, `-h` - Mostrar mensagem de ajuda

#### Recursos

1. **Verificação de Versão Python** - Verifica se Python 3 está instalado
2. **Validação de Estrutura** - Executa check_structure.py
3. **Verificação de Estrutura de Pacotes** - Verifica arquivos `__init__.py`
4. **Verificação de Arquivos Críticos** - Valida arquivos essenciais do projeto
5. **Validação de Sintaxe** - Verifica arquivos Python para erros de sintaxe
6. **Status do Git** - Mostra alterações não commitadas se estiver em um repositório git

#### Exemplos

```bash
# Apenas validar (sem alterações)
./scripts/validate_structure.sh

# Criar arquivos críticos automaticamente
./scripts/validate_structure.sh --fix

# Criar arquivos críticos + importantes
./scripts/validate_structure.sh --fix --priority 2
```

## Templates de Arquivos

Ao criar arquivos ausentes, o sistema usa templates inteligentes baseados no tipo de arquivo:

### Modelos (SQLAlchemy)

```python
"""
Modelo Student para EduAutismo IA.

Este módulo define o modelo de banco de dados para student.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base


class Student(Base):
    """Modelo de banco de dados Student."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # TODO: Adicione campos específicos do modelo aqui
```

### Schemas (Pydantic)

```python
"""
Schemas Pydantic de Student para validação de request/response.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    """Schema base para Student com atributos compartilhados."""
    # TODO: Adicione campos base aqui
    pass


class StudentCreate(BaseModel):
    """Schema para criar um novo student."""
    model_config = ConfigDict(from_attributes=True)
    # TODO: Adicione campos de criação aqui
    pass


class StudentResponse(StudentInDB):
    """Schema para resposta da API de student."""
    model_config = ConfigDict(from_attributes=True)
```

### Serviços (Lógica de Negócio)

```python
"""
Serviço de lógica de negócio de Student.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """Classe de serviço para lógica de negócio de Student."""

    @staticmethod
    def create(db: Session, student_data: StudentCreate) -> Student:
        """Criar um novo student."""
        db_obj = Student(**student_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, student_id: int) -> Optional[Student]:
        """Obter um student por ID."""
        return db.query(Student).filter(Student.id == student_id).first()

    # ... mais métodos
```

### Rotas (FastAPI)

```python
"""
Rotas da API de Student.
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
    """Criar um novo student."""
    return StudentService.create(db, student_data)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """Obter um student por ID."""
    student = StudentService.get(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student não encontrado"
        )
    return student

# ... mais endpoints
```

### Testes

```python
"""
Testes unitários para student_service.

Este módulo contém testes unitários para o módulo student_service.
"""

import pytest
from fastapi.testclient import TestClient


class TestStudentServiceUnit:
    """Classe de teste para testes unitários de student_service."""

    def test_student_service_placeholder(self):
        """
        Teste placeholder para student_service.

        TODO: Implementar testes unitários reais
        """
        # TODO: Adicionar implementação do teste
        assert True  # Asserção placeholder
```

## Processo de Validação Passo a Passo

### Passo 1: Verificar Estrutura Atual

Primeiro, entenda o estado atual do seu projeto:

```bash
# Veja árvore de diretórios
tree -L 3 -I '__pycache__|*.pyc|venv|.git|node_modules'

# Ou use find
find . -type f -name "*.py" | grep -E "(backend/app/|tests/)" | sort

# Execute validação básica
python scripts/check_structure.py --report-only
```

### Passo 2: Analisar o Relatório

Observe a saída para entender:
- Quantos diretórios estão presentes/ausentes
- Quantos arquivos estão presentes/ausentes por prioridade
- Porcentagem geral de conclusão
- Itens específicos ausentes

### Passo 3: Criar Arquivos Ausentes

Baseado no relatório, crie arquivos incrementalmente:

```bash
# Comece com arquivos críticos
python scripts/check_structure.py --create-missing --priority 1

# Verifique criação
python scripts/check_structure.py --report-only

# Adicione arquivos importantes
python scripts/check_structure.py --create-missing --priority 2

# Verifique novamente
python scripts/check_structure.py --report-only
```

### Passo 4: Verificar Estrutura de Pacotes

Garanta que todos os pacotes Python tenham `__init__.py`:

```bash
# Verifique todos os arquivos __init__.py
find backend/app -name "__init__.py" -type f

# Deve mostrar todos os arquivos init de pacotes
```

### Passo 5: Validar Sintaxe Python

Verifique erros de sintaxe nos arquivos criados:

```bash
# Verifique arquivo específico
python -m py_compile backend/app/models/student.py

# Ou use flake8
flake8 backend/app/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Passo 6: Revisar e Personalizar

Todos os arquivos criados contêm comentários TODO. Substitua-os com implementação real:

1. **Modelos**: Adicione colunas SQLAlchemy
2. **Schemas**: Adicione campos Pydantic
3. **Serviços**: Adicione lógica de negócio
4. **Rotas**: Adicione endpoints
5. **Testes**: Adicione casos de teste

## Fluxos de Trabalho Comuns

### Configuração de Novo Projeto

```bash
# 1. Crie estrutura completa
python scripts/check_structure.py --create-missing --priority 2

# 2. Verifique
./scripts/validate_structure.sh

# 3. Instale dependências
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Corrigindo Estrutura Incompleta

```bash
# 1. Verifique o que está faltando
python scripts/check_structure.py --report-only

# 2. Crie arquivos ausentes
python scripts/check_structure.py --create-missing --priority 2

# 3. Execute validação completa
./scripts/validate_structure.sh
```

### Adicionando Novos Recursos

Ao adicionar um novo recurso (ex: "Teacher"):

```bash
# Templates atuais suportam: student, activity, assessment
# Para novos recursos, crie arquivos manualmente seguindo o mesmo padrão

# Ou modifique check_structure.py para adicionar novos templates
```

## Integração com Fluxo de Desenvolvimento

### Hook Pre-commit

Adicione em `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Valide estrutura antes do commit
python scripts/check_structure.py --report-only
exit $?
```

### Integração CI/CD

Adicione ao GitHub Actions (`.github/workflows/validate.yml`):

```yaml
name: Validar Estrutura

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configurar Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Validar estrutura
        run: python scripts/check_structure.py --report-only
```

### Tarefa Make

Adicione ao `Makefile`:

```makefile
.PHONY: validate
validate:
	@echo "Validando estrutura do projeto..."
	@python scripts/check_structure.py --report-only

.PHONY: fix-structure
fix-structure:
	@echo "Criando arquivos ausentes..."
	@python scripts/check_structure.py --create-missing --priority 2
```

## Solução de Problemas

### Problema: Script não encontrado

```bash
# Certifique-se de estar na raiz do projeto
pwd
# Deve mostrar: /caminho/para/eduautismo-ia-mvp

# Torne o script executável
chmod +x scripts/check_structure.py
chmod +x scripts/validate_structure.sh
```

### Problema: Permissão negada

```bash
# Execute com python explicitamente
python3 scripts/check_structure.py

# Ou corrija permissões
chmod +x scripts/*.py scripts/*.sh
```

### Problema: Erros de importação em arquivos criados

Os arquivos gerados podem ter erros de importação inicialmente porque:
1. Dependências podem não estar instaladas
2. Arquivos referenciados podem ainda não existir

**Soluções:**
```bash
# Instale dependências
cd backend
pip install -r requirements.txt

# Crie dependências ausentes
python ../scripts/check_structure.py --create-missing --priority 2

# Atualize imports em main.py ou config.py conforme necessário
```

### Problema: Erros de sintaxe após criação

Se arquivos tiverem erros de sintaxe:
```bash
# Verifique arquivo específico
python -m py_compile backend/app/models/student.py

# Corrija o arquivo manualmente
# O template fornece uma estrutura funcional, erros de sintaxe provavelmente vêm de edições manuais
```

## Melhores Práticas

1. **Comece com Prioridade 1**: Sempre crie arquivos críticos primeiro
2. **Revise TODOs**: Verifique todos os comentários TODO em arquivos gerados
3. **Personalize Templates**: Modifique templates em `check_structure.py` para atender suas necessidades
4. **Validação Regular**: Execute validação antes de commits
5. **Controle de Versão**: Commite arquivos gerados imediatamente com mensagens claras
6. **Atualizações Incrementais**: Adicione arquivos de Prioridade 2 e 3 conforme necessário, não todos de uma vez
7. **Teste Cedo**: Execute testes após criar arquivos de teste para garantir que a estrutura está correta

## Referência de Arquivos

### Criados por Prioridade 1
- Todos os arquivos `__init__.py` em:
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

### Criados por Prioridade 2
- **Modelos**: `student.py`, `activity.py`, `assessment.py`
- **Schemas**: `student.py`, `activity.py`, `assessment.py`
- **Serviços**: `student_service.py`, `activity_service.py`, `assessment_service.py`
- **Rotas**: `students.py`, `activities.py`, `assessments.py`
- **Testes**: `conftest.py`, `test_student_service.py`, `test_students_api.py`
- **Dependências**: `auth.py`

### Criados por Prioridade 3
- `backend/pytest.ini`
- `backend/.coveragerc`

## Uso Avançado

### Templates Personalizados

Para adicionar templates personalizados, edite `scripts/check_structure.py`:

```python
# Na classe FileTemplates, adicione novo método
@staticmethod
def get_custom_template(name: str) -> str:
    return f'''"""Template personalizado para {name}."""
    # Seu template aqui
    '''

# Em _define_expected_files(), adicione definição de arquivo
FileDefinition(
    'caminho/para/arquivo.py',
    2,  # Prioridade
    templates.get_custom_template('MinhaClasse'),
    'Descrição do arquivo'
),
```

### Estendendo Validação

Para adicionar novas verificações de validação:

```python
# Na classe ProjectStructureValidator
def validate_custom_rule(self):
    """Adicione lógica de validação personalizada."""
    # Seu código de validação aqui
    pass
```

## Códigos de Saída

Os scripts usam códigos de saída para indicar status:

- `0`: Sucesso (≥ 95% conclusão)
- `1`: Aviso (≥ 70% conclusão)
- `2`: Erro (< 70% conclusão)

Use estes em CI/CD:
```bash
python scripts/check_structure.py --report-only
if [ $? -eq 2 ]; then
    echo "Problemas críticos de estrutura!"
    exit 1
fi
```

## Próximos Passos

Após validar sua estrutura:

1. **Configure Ambiente**
   ```bash
   cp backend/.env.example backend/.env
   # Edite backend/.env com suas configurações
   ```

2. **Configure Banco de Dados**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Instale Dependências**
   ```bash
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```

4. **Execute Testes**
   ```bash
   pytest backend/tests/
   ```

5. **Inicie Servidores de Desenvolvimento**
   ```bash
   # Backend
   uvicorn backend.app.main:app --reload

   # Frontend
   cd frontend && npm run dev
   ```

## Suporte

Para problemas ou questões:
- Verifique esta documentação
- Revise templates de arquivos gerados
- Verifique `CLAUDE.md` para orientação específica do projeto
- Revise `README.md` para informações gerais do projeto
