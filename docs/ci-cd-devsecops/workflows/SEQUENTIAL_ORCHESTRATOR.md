# 🎼 Sequential CI/CD Orchestrator - Documentação

## 📋 Visão Geral

O novo orchestrador (`00-sequential-orchestrator.yml`) garante que os workflows sejam **executados em sequência rigorosa**, onde cada stage só inicia após o anterior completar com **sucesso total**.

---

## 🔄 Fluxo de Execução

```
Push para main/develop
         ↓
    [Trigger 00-sequential-orchestrator.yml]
         ↓
┌─────────────────────────────────────┐
│ Stage 1: Backend Tests              │
│ 🧪 02-backend-tests.yml             │
│                                     │
│ Jobs:                               │
│ ├─ lint (Black, isort, flake8, mypy)
│ └─ test (Unit + Integration)        │
│                                     │
│ Status: ⏳ Running...               │
└─────────────────────────────────────┘
         ↓
    ✅ Sucesso?
         │
    ┌─→ Não → ❌ HALT (teste falhou)
    │
    Yes
    │
    ↓
┌─────────────────────────────────────┐
│ Stage 2: Build & Push               │
│ 🚀 05-build-and-push.yml            │
│                                     │
│ Jobs:                               │
│ ├─ build-and-push (api, web matrix) │
│ └─ generate-sbom                    │
│                                     │
│ Status: ⏳ Running...               │
└─────────────────────────────────────┘
         ↓
    ✅ Sucesso?
         │
    ┌─→ Não → ❌ HALT (build falhou)
    │
    Yes
    │
    ↓
┌─────────────────────────────────────┐
│ Final: Pipeline Status Report       │
│ ✅ 00-sequential-orchestrator.yml   │
│                                     │
│ Jobs:                               │
│ └─ pipeline-status                  │
│                                     │
│ Actions:                            │
│ ├─ Determina status total           │
│ ├─ Gera relatório                   │
│ └─ Exit code apropriado             │
└─────────────────────────────────────┘
         ↓
    ✅ PIPELINE COMPLETA COM SUCESSO
```

---

## 🎯 Como Funciona

### 1️⃣ **Trigger**
- Push em `main` ou `develop` dispara `00-sequential-orchestrator.yml`
- PR também trigga (modo read-only, sem push)

### 2️⃣ **Stage 1: Backend Tests**
```yaml
backend-tests:
  uses: ./.github/workflows/02-backend-tests.yml
  secrets: inherit
```
- Executa workflow `02-backend-tests.yml`
- Contém jobs sequenciais: `lint` → `test`
- Se falhar: pipeline **PARA** aqui

### 3️⃣ **Stage 2: Build & Push**
```yaml
build-and-push:
  if: success() && github.event_name == 'push'
  needs: backend-tests
  uses: ./.github/workflows/05-build-and-push.yml
```

**Condições**:
- ✅ `needs: backend-tests` - Aguarda Stage 1 completar
- ✅ `if: success()` - Só roda se Stage 1 teve sucesso
- ✅ `github.event_name == 'push'` - Só em push (não em PR)

### 4️⃣ **Final: Pipeline Status**
```yaml
pipeline-status:
  needs: [backend-tests, build-and-push]
  if: always()
```

- Executa **sempre** (mesmo se falhar)
- Reporta status de todos os stages
- Exit code apropriado (0 = sucesso, 1 = falha)

---

## 🚀 Comportamentos por Evento

### 📝 Push para main/develop

```
✅ Stage 1: Backend Tests - EXECUTA
   ↓
   ✅ Passou?
   │
   ├─ Sim → ✅ Stage 2: Build & Push - EXECUTA
   │              ↓
   │              ✅ Passou?
   │              │
   │              ├─ Sim → ✅ Pipeline Status - SUCESSO
   │              └─ Não → ❌ Pipeline Status - FALHA
   │
   └─ Não → ❌ Stage 2 - SKIPPED (devido a needs)
               ↓
               ❌ Pipeline Status - FALHA
```

### 🔀 Pull Request

```
⚠️  Stage 1: Backend Tests - EXECUTA
   ↓
   ✅ Passou?
   │
   ├─ Sim → ⏭️  Stage 2: Build & Push - SKIPPED
   │              (condition: github.event_name == 'push')
   │              ↓
   │              ⏳ Pipeline Status - AGUARDA
   │
   └─ Não → ❌ Stage 2 - SKIPPED
               ↓
               ❌ Pipeline Status - FALHA
```

---

## 📊 Status Check Matrix

| Evento | Stage 1 | Stage 2 | Status Final | Deploy? |
|--------|---------|---------|--------------|---------|
| Push (sucesso completo) | ✅ | ✅ | ✅ SUCESSO | ✅ |
| Push (Stage 1 falha) | ❌ | ⏭️ SKIPPED | ❌ FALHA | ❌ |
| Push (Stage 2 falha) | ✅ | ❌ | ❌ FALHA | ❌ |
| PR (Stage 1 passa) | ✅ | ⏭️ SKIPPED | ✅ (parcial) | ❌ |
| PR (Stage 1 falha) | ❌ | ⏭️ SKIPPED | ❌ FALHA | ❌ |

---

## 🔍 Verificar Execução no GitHub Actions

### 1. Abrir Actions
```
repositório → Actions → workflows
```

### 2. Ver Execução Sequencial
```
00-sequential-orchestrator (iniciado)
  │
  ├─ backend-tests (⏳ em progresso)
  │   └─ lint → test
  │
  └─ build-and-push (⏳ aguardando backend-tests)
      └─ build-and-push → generate-sbom
```

### 3. Visualizar Dependency Graph
- Clicar em workflow em execução
- Ver "Jobs" com setas de dependência
- `backend-tests` → `build-and-push` (com seta)

---

## 📝 Logs Esperados

### Quando Backend Tests passam:
```
✅ Backend Tests completed successfully!
🚀 Dispatching Build & Push workflow...
✅ Build & Push workflow dispatched!
```

### Quando Build & Push completa:
```
✅ Build & Push completed successfully!
📊 Artifacts generated:
  - Container images (api, web)
  - SBOM reports (SPDX format)
🎉 Pipeline stage 5 of 5 complete!
```

### No Final (pipeline-status):
```
🎼 Sequential Pipeline Execution Report
======================================

Stage 1: Backend Tests
  Status: success
  ✅ Passed - Proceeding to next stage

Stage 2: Build & Push
  Status: success
  ✅ Passed - Ready for deployment

✅ All stages completed successfully!
🎉 Pipeline execution complete
```

---

## ⚠️ Tratamento de Falhas

### Se Backend Tests falha:
1. Job `test` falha
2. Orchestrator detecta `needs.backend-tests.result == 'failure'`
3. Job `build-and-push` é **pulado** (skipped) automaticamente
4. `pipeline-status` reporta falha
5. Build **não é feito**

### Se Build & Push falha:
1. Job `build-and-push` ou `generate-sbom` falha
2. `pipeline-status` reporta falha
3. Container **não é pushado** para registry
4. Próximas etapas (deployment) não executam

---

## 🔗 Integração com Workflows Individuais

Os workflows individuais podem **ainda ser disparados isoladamente**:

### Via Push direto (sem orchestrador)
```
backend-tests.yml:
  on:
    push:
      branches: [main, develop]
      paths:
        - "backend/**"
```

### Via workflow_dispatch (manual)
```
Ações → Selecionar workflow → Run workflow
```

### Via workflow_call (chamada por outro)
```yaml
backend-tests:
  uses: ./.github/workflows/02-backend-tests.yml
```

---

## 💡 Próximos Passos

### 1️⃣ Expandir para Frontend & Container Scan (opcional)
```yaml
frontend-tests:
  needs: backend-tests
  uses: ./.github/workflows/03-frontend-tests.yml

container-scan:
  needs: [frontend-tests, build-and-push]
  uses: ./.github/workflows/04-container-scan.yml
```

### 2️⃣ Adicionar Deployment Stage (opcional)
```yaml
deploy-staging:
  needs: build-and-push
  uses: ./.github/workflows/06-deploy-staging.yml
  if: github.ref == 'refs/heads/develop'

deploy-production:
  needs: [container-scan, deploy-staging]
  uses: ./.github/workflows/07-deploy-production.yml
  if: github.ref == 'refs/heads/main'
```

### 3️⃣ Adicionar Notifications (opcional)
```yaml
notify-slack:
  needs: pipeline-status
  if: always()
  uses: ./.github/workflows/08-notify-slack.yml
```

---

## 🎓 Resumo das Mudanças

| Arquivo | Mudança |
|---------|---------|
| `00-sequential-orchestrator.yml` | ✨ Novo (orquestrador) |
| `02-backend-tests.yml` | ✏️ Adicionado trigger para Build & Push |
| `05-build-and-push.yml` | ✏️ Adicionado `workflow_dispatch` input |

---

## ✨ Benefícios

✅ **Sequencial Garantido**: Nenhuma execução paralela não desejada
✅ **Falhas Rápidas**: Para imediatamente se houver erro
✅ **Fácil Manutenção**: Mudar ordem é trivial (edit `needs:`)
✅ **Visibilidade**: GitHub Actions UI mostra dependências claramente
✅ **Backward Compatible**: Workflows individuais ainda funcionam

---

**Documentação criada**: `docs/ci-cd-devsecops/workflows/SEQUENTIAL_ORCHESTRATOR.md`
**Status**: ✅ Implementado e Pronto
**Próximo**: Fazer push e testar primeiro fluxo completo!
