# 🎼 GitHub Actions Workflows - Quick Reference

## 📊 Estrutura Consolidada

```
.github/workflows/
├── 00-orchestrator.yml          ← MASTER orchestrator
├── 01-security-scan.yml         ← Security checks
├── 02-backend-tests.yml         ← Python tests
├── 03-frontend-tests.yml        ← React tests
├── 04-container-scan.yml        ← Container security
└── 05-build-and-push.yml        ← Registry push
```

---

## 🔄 Fluxo de Execução Sequencial

```
Push para main/develop
         ↓
   00-orchestrator.yml
         ↓
   ┌─────────────────────┐
   │ 🧪 Backend Tests    │
   │ (02-backend-tests)  │
   └─────────────────────┘
         ↓
    ✅ Sucesso?
    │
    ├─ Não → ❌ HALT
    │
    └─ Sim ↓
   ┌─────────────────────┐
   │ 🚀 Build & Push     │
   │ (05-build-and-push) │
   └─────────────────────┘
         ↓
    ✅ Sucesso?
    │
    ├─ Não → ❌ HALT
    │
    └─ Sim ↓
   ┌─────────────────────┐
   │ ✅ Pipeline Status  │
   │ (orchestrator-end)  │
   └─────────────────────┘
         ↓
    🎉 COMPLETO
```

---

## 📋 Workflows Detalhados

### 1️⃣ `00-orchestrator.yml` 🎼
**Propósito**: Orquestrador principal
**Triggers**: 
- Push em `main`, `develop`
- Pull requests

**Jobs**:
- `backend-tests` → chama 02-backend-tests.yml
- `build-and-push` → chama 05-build-and-push.yml (após backend)
- `pipeline-status` → reporta resultado final

**Dependências**:
```yaml
backend-tests:
  uses: ./.github/workflows/02-backend-tests.yml

build-and-push:
  needs: backend-tests  # ← AGUARDA backend
  if: success() && github.event_name == 'push'
  uses: ./.github/workflows/05-build-and-push.yml
```

---

### 2️⃣ `01-security-scan.yml` 🔒
**Propósito**: Scanning de segurança
**Triggers**: Push em `main`, `develop`

**Jobs** (sequenciais):
1. `gitleaks` - Secret detection
2. `trufflehog` - Alternative secret scan
3. `dependency-check` - Dependency scanning
4. `license-scan` - License compliance
5. `sast-python` - Python SAST (Bandit)
6. `sast-javascript` - JS SAST (ESLint)

**Características**:
- Cada job depende do anterior (`needs:`)
- Continue-on-error onde apropriado
- Upload SARIF para GitHub Security

---

### 3️⃣ `02-backend-tests.yml` 🧪
**Propósito**: Testes Python do backend
**Triggers**: 
- Push em `backend/**`
- Chamada pelo orchestrator

**Jobs** (sequenciais):
1. `lint` - Black, isort, flake8, mypy
2. `test` - Unit + Integration tests + Coverage

**Características**:
- Postgres + Redis services
- Alembic migration validation
- Codecov integration
- Coverage reporting
- PR comments com resultados

**Importante**: Dispara 05-build-and-push ao suceder!

---

### 4️⃣ `03-frontend-tests.yml` 🎨
**Propósito**: Testes React do frontend
**Triggers**: Push em `frontend/**`

**Jobs** (sequenciais):
1. `lint` - ESLint + Prettier
2. `test` - Vitest + Build verification

**Características**:
- Node 18 cache
- Coverage reports
- Build verification

---

### 5️⃣ `04-container-scan.yml` 🐳
**Propósito**: Scanning de segurança de containers
**Triggers**: Push em `Dockerfile.*`

**Jobs** (sequenciais):
1. `build` - Build images (matrix: api, web)
2. `scan` - Scan images com Trivy, Grype, Syft

**Características**:
- Trivy: Vulnerability + Config scan
- Grype: Container security scan
- Syft: SBOM generation (SPDX + CycloneDX)
- **NEW**: Fallback SBOM if Syft fails
- SARIF uploads para GitHub Security

**Importante**: Syft tem tratamento com 3 estratégias de fallback!

---

### 6️⃣ `05-build-and-push.yml` 🚀
**Propósito**: Build e push de containers
**Triggers**: Push em `main`, `develop`

**Jobs** (sequenciais):
1. `build-and-push` - Build + Push (matrix: api, web)
2. `generate-sbom` - Gera SBOM de dependencies

**Características**:
- Docker buildx com cache
- Metadata tagging (semver, branch, SHA)
- GHCR registry push
- Python + Node SBOM generation

**Importante**: Dispara via `workflow_dispatch`!

---

## 🎯 Cenários de Execução

### Cenário 1: Push Normal
```
Push para main
     ↓
00-orchestrator dispara
     ↓
02-backend-tests executa
     ↓
✅ Sucesso?
     ↓
     Sim → 05-build-and-push dispara
     ↓
     ✅ Sucesso → Pipeline Status: SUCCESS
```

### Cenário 2: Backend Tests Falha
```
Push para main
     ↓
00-orchestrator dispara
     ↓
02-backend-tests FALHA
     ↓
05-build-and-push SKIPPED (needs falhou)
     ↓
Pipeline Status: FAILURE
```

### Cenário 3: Pull Request
```
PR criado
     ↓
00-orchestrator dispara
     ↓
02-backend-tests executa
     ↓
05-build-and-push SKIPPED (condition: push only)
     ↓
Pipeline Status: PARTIAL (tests OK, no build)
```

---

## 🔧 Principais Melhorias

### ✅ Syft SBOM Error Handling v2

**Problema**: Syft falhava com exit code 1
**Solução**:
1. Verificar Docker image existe
2. Tentar docker: direct method
3. Fallback: docker-archive:// method
4. Fallback final: Minimal SBOM JSON
5. Continue-on-error: Não bloqueia pipeline

**Resultado**: SBOM sempre gerado (ou fallback)

---

### ✅ Orquestração Sequencial

**Problema**: Workflows rodavam em paralelo/desordena
**Solução**: 
- Orchestrator controla ordem
- `needs:` especifica dependências
- `if: success()` garante sucesso antes

**Resultado**: Ordem garantida, falhas rápidas

---

## 📊 Status Checks

Todos os workflows têm:
- ✅ `continue-on-error: true` onde apropriado
- ✅ Logging detalhado
- ✅ Upload de artifacts
- ✅ PR comments com resultados
- ✅ SARIF uploads para GitHub Security
- ✅ Concurrency control (cancel-in-progress)

---

## 🚀 Como Testar Localmente

### 1. Verificar Syntax
```bash
# Validate YAML
yamllint .github/workflows/*.yml

# Validate Actions
# (use https://github.com/rhysd/actionlint)
actionlint .github/workflows/00-orchestrator.yml
```

### 2. Simular Localmente
```bash
# Usar act (simula GitHub Actions locally)
act push -b main -w .github/workflows/02-backend-tests.yml
```

### 3. Monitorar no GitHub
```
Repositório → Actions → Ver workflow executando
```

---

## 📚 Documentação Relacionada

- `docs/ci-cd-devsecops/workflows/SEQUENTIAL_ORCHESTRATOR.md` - Orchestrator detalhado
- `docs/ci-cd-devsecops/workflows/SYFT_SBOM_ERROR_HANDLING_V2.md` - Syft improvements
- `docs/ci-cd-devsecops/workflows/PIPELINE_STRUCTURE.md` - Estrutura geral
- `docs/ci-cd-devsecops/workflows/VISUAL_GUIDE.md` - Visualizações

---

## ✨ Próximas Melhorias (Opcional)

### 1. Adicionar Frontend & Container Scan à Orquestração
```yaml
container-scan:
  needs: [backend-tests, frontend-tests]
  uses: ./.github/workflows/04-container-scan.yml
```

### 2. Adicionar Security Scan ao Início
```yaml
security-scan:
  uses: ./.github/workflows/01-security-scan.yml

backend-tests:
  needs: security-scan
```

### 3. Adicionar Deployment Stages
```yaml
deploy-staging:
  needs: build-and-push
  uses: ./.github/workflows/06-deploy-staging.yml
  if: github.ref == 'refs/heads/develop'
```

---

## ⚡ Performance Tipicamente

| Stage | Tempo | Status |
|-------|-------|--------|
| Backend Tests (lint) | ~5 min | ✅ Fast |
| Backend Tests (test) | ~10 min | ✅ Standard |
| Build & Push | ~10 min | ✅ Standard |
| Total | ~25-30 min | ✅ Acceptable |

---

## 🎓 Resumo

✅ **6 workflows** bem estruturados
✅ **Sequência garantida** (orchestrator)
✅ **Fallback robusto** (Syft SBOM)
✅ **Documentação completa** (5 docs)
✅ **Pronto para produção** (2025)

**Status**: 🟢 **COMPLETO E OPERACIONAL**

---

**Última atualização**: 11 de novembro de 2025
**Localização**: `.github/workflows/`
**Documentação**: `docs/ci-cd-devsecops/workflows/`
