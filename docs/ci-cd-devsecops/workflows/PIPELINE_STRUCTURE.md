# CI/CD Pipeline Structure

## Overview

A pipeline CI/CD está organizada em 5 workflows que executam sequencialmente com dependências de jobs dentro de cada workflow para garantir ordem de execução.

## Workflows & Dependências

### 1️⃣ **01-security-scan.yml** 🔒
**Objetivo**: Varredura de segurança completa

**Sequência de Jobs (Linear)**:
```
gitleaks
    ↓
trufflehog (needs: gitleaks)
    ↓
dependency-check (needs: trufflehog)
    ↓
license-scan (needs: dependency-check)
    ↓
sast-python (needs: license-scan)
    ↓
sast-javascript (needs: sast-python)
```

**O que cada job faz**:
- **gitleaks**: Scaneia segredos no código
- **trufflehog**: Busca por padrões de vazamento de dados
- **dependency-check**: Verifica vulnerabilidades em dependências Python e NPM
- **license-scan**: Verifica compliance de licenças
- **sast-python**: Análise estática de segurança com Bandit
- **sast-javascript**: Análise estática de segurança com ESLint

**Trigger**: Push/PR no main/develop + Daily (2 AM UTC)

---

### 2️⃣ **02-backend-tests.yml** 🧪
**Objetivo**: Testes e lint do backend Python

**Sequência de Jobs (Linear)**:
```
lint
    ↓
test (needs: lint)
```

**O que cada job faz**:
- **lint**: Black, isort, flake8, mypy
- **test**: Testes unitários, integração, coverage, migrations

**Trigger**: Push/PR no main/develop quando há mudanças em backend/**

---

### 3️⃣ **03-frontend-tests.yml** 🎨
**Objetivo**: Testes e lint do frontend React

**Sequência de Jobs (Linear)**:
```
lint
    ↓
test (needs: lint)
```

**O que cada job faz**:
- **lint**: ESLint e Prettier check
- **test**: Vitest, build verification, coverage

**Trigger**: Push/PR no main/develop quando há mudanças em frontend/**

---

### 4️⃣ **04-container-scan.yml** 🐳
**Objetivo**: Build e scan de imagens container

**Sequência de Jobs (Linear)**:
```
build
    ↓
scan (needs: build)
```

**O que cada job faz**:
- **build**: Build das imagens Docker (API + Web) com matriz
- **scan**: Trivy, Grype, SBOM (Syft) - com matriz (API + Web)

**Trigger**: Push/PR no main/develop quando há mudanças em Dockerfile.*, backend/**, frontend/**

---

### 5️⃣ **05-build-and-push.yml** 🚀
**Objetivo**: Build e push para registry

**Sequência de Jobs (Linear)**:
```
build-and-push
    ↓
generate-sbom (needs: build-and-push)
```

**O que cada job faz**:
- **build-and-push**: Build e push das imagens (API + Web)
- **generate-sbom**: Gera software bill of materials

**Trigger**: Push no main/develop (PR apenas para build local)

---

## 🎯 Ordem de Execução Global

Cada workflow roda independentemente, acionado por seus triggers específicos:

1. **01-security-scan.yml** → Começa imediatamente
2. **02-backend-tests.yml** → Começa imediatamente (paralelo com 01)
3. **03-frontend-tests.yml** → Começa imediatamente (paralelo com 01, 02)
4. **04-container-scan.yml** → Começa imediatamente (paralelo com 01, 02, 03)
5. **05-build-and-push.yml** → Começa imediatamente (paralelo com 01, 02, 03, 04)

> **Nota**: Para garantir execução SEQUENCIAL entre workflows (01 → 02 → 03 → 04 → 05), você pode:
> - Usar o arquivo `00-orchestrator.yml` com `workflow_call` (requer suporte)
> - Usar GitHub's branch protection rules + status checks
> - Implementar um workflow maestro que dispara os outros via API

---

## 🔄 Dentro de Cada Workflow

**Todas as dependências estão implementadas com `needs`**:

### Exemplo do 01-security-scan.yml:
```yaml
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps: ...

  trufflehog:
    runs-on: ubuntu-latest
    needs: gitleaks  # ← Espera gitleaks terminar com sucesso
    steps: ...

  dependency-check:
    runs-on: ubuntu-latest
    needs: trufflehog  # ← Espera trufflehog terminar com sucesso
    steps: ...
```

### Exemplo do 02-backend-tests.yml:
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - Lint with Black
      - Sort imports with isort
      - Lint with flake8
      - Type checking with mypy

  test:
    runs-on: ubuntu-latest
    needs: lint  # ← Testes só rodam após lint passar
    steps:
      - Validate Alembic migrations
      - Run Unit Tests
      - Run Integration Tests
      - Merge coverage reports
```

---

## ✅ Verificação de Sucesso

Cada job só começa após o anterior completar COM SUCESSO:
- ✅ Se anterior = SUCCESS → Job atual executa
- ❌ Se anterior = FAILURE → Job atual é pulado (pipeline falha)
- ⏭️ Se anterior = SKIPPED → Depende da configuração `if:`

---

## 📊 Matriz de Estratégia

Alguns jobs usam `matrix` para paralelizar:

### 04-container-scan.yml - Build job:
```yaml
strategy:
  matrix:
    image:
      - name: "api", file: "Dockerfile.api"
      - name: "web", file: "Dockerfile.web"
```
**Resultado**: 2 jobs paralelos (api + web)

### 04-container-scan.yml - Scan job:
```yaml
strategy:
  matrix:
    image:
      - name: "api", file: "Dockerfile.api"
      - name: "web", file: "Dockerfile.web"
```
**Resultado**: 2 jobs paralelos (scan api + scan web), mas só após BUILD completar

---

## 🚀 Como Melhorar (Opcional)

### Opção 1: Usar Orchestrator com `workflow_call`
Criar um workflow maestro que dispara os 5 workflows em sequência usando `workflow_call`.

### Opção 2: Usar Repository Dispatch
Cada workflow dispara o próximo via `repository_dispatch` event.

### Opção 3: Usar GitHub Environments
Configurar protections que só permitem deploy após todos os testes passarem.

---

## 📝 Resumo das Mudanças Implementadas

✅ **01-security-scan.yml**: 6 jobs com 5 dependências sequenciais
✅ **02-backend-tests.yml**: 2 jobs (lint + test), test depende de lint
✅ **03-frontend-tests.yml**: 2 jobs (lint + test), test depende de lint
✅ **04-container-scan.yml**: 2 jobs (build + scan), scan depende de build
✅ **05-build-and-push.yml**: 2 jobs (build-and-push + generate-sbom), SBOM depende de build

**Total**: 14 jobs com 13 dependências sequenciais

---

## 🔗 Referências

- [GitHub Actions: Using jobs in a workflow](https://docs.github.com/en/actions/using-jobs)
- [GitHub Actions: Defining outputs for jobs](https://docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs)
- [GitHub Actions: Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
