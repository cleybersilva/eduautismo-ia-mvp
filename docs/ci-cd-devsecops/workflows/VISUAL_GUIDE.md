# 📊 CI/CD Pipeline - Visual Guide & Timeline

## 🎯 Visualização Completa da Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Sequential Pipeline                    │
│                                                                           │
│  Push to main/develop                                                    │
│         ↓                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 01-SECURITY-SCAN (Parallel checks within sequential steps)       │   │
│  │                                                                   │   │
│  │  Stage 1: gitleaks               ✓ Done                          │   │
│  │     ↓ needs: gitleaks                                            │   │
│  │  Stage 2: trufflehog             ✓ Done                          │   │
│  │     ↓ needs: trufflehog                                          │   │
│  │  Stage 3: dependency-check       ✓ Done                          │   │
│  │     ↓ needs: dependency-check                                    │   │
│  │  Stage 4: license-scan           ✓ Done                          │   │
│  │     ↓ needs: license-scan                                        │   │
│  │  Stage 5: sast-python            ✓ Done                          │   │
│  │     ↓ needs: sast-python                                         │   │
│  │  Stage 6: sast-javascript        ✓ Done                          │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ↓ all done                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 02-BACKEND-TESTS (Sequential: Lint then Test)                   │   │
│  │                                                                   │   │
│  │  Job 1: lint                     ✓ Done                          │   │
│  │   └─ Black format check                                          │   │
│  │   └─ isort import check                                          │   │
│  │   └─ flake8 style check                                          │   │
│  │   └─ mypy type check                                             │   │
│  │   └─ Alembic migration validation                                │   │
│  │     ↓ needs: lint                                                │   │
│  │  Job 2: test                     ✓ Done                          │   │
│  │   └─ Unit Tests + Integration Tests + Coverage                  │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ↓ all done                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 03-FRONTEND-TESTS (Sequential: Lint then Test)                  │   │
│  │                                                                   │   │
│  │  Job 1: lint                     ✓ Done                          │   │
│  │   └─ ESLint check                                                │   │
│  │   └─ Prettier format check                                       │   │
│  │     ↓ needs: lint                                                │   │
│  │  Job 2: test                     ✓ Done                          │   │
│  │   └─ Vitest unit tests                                           │   │
│  │   └─ Production build verification                               │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ↓ all done                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 04-CONTAINER-SCAN (Sequential: Build then Scan)                 │   │
│  │                                                                   │   │
│  │  Job 1: build                    ✓ Done                          │   │
│  │   ├─ Build api image (parallel)                                 │   │
│  │   └─ Build web image (parallel)                                 │   │
│  │     ↓ needs: build                                               │   │
│  │  Job 2: scan                     ✓ Done                          │   │
│  │   ├─ Scan api  (parallel)                                       │   │
│  │   │  ├─ Trivy vulnerability                                     │   │
│  │   │  ├─ Trivy config                                            │   │
│  │   │  ├─ Grype scan                                              │   │
│  │   │  └─ Syft SBOM                                               │   │
│  │   └─ Scan web  (parallel)                                       │   │
│  │      ├─ Trivy vulnerability                                     │   │
│  │      ├─ Trivy config                                            │   │
│  │      ├─ Grype scan                                              │   │
│  │      └─ Syft SBOM                                               │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ↓ all done                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 05-BUILD-AND-PUSH (Sequential: Build then Generate SBOM)        │   │
│  │                                                                   │   │
│  │  Job 1: build-and-push           ✓ Done                          │   │
│  │   ├─ Build and push api (parallel)                              │   │
│  │   └─ Build and push web (parallel)                              │   │
│  │     ↓ needs: build-and-push                                      │   │
│  │  Job 2: generate-sbom            ✓ Done                          │   │
│  │   ├─ Generate SBOM for api                                      │   │
│  │   └─ Generate SBOM for web                                      │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ↓ all done                                   │
│  ✅ PIPELINE COMPLETE                                                    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Timeline Estimada

```
T+0min    ├─ Start: Push to main/develop
          │
T+0min    ├─→ [01] Gitleaks scan               (5-10 min)
T+5min    │   └─→ [02] TruffleHog scan        (10-15 min)
T+15min   │       └─→ [03] Dependency Check   (5-10 min)
T+20min   │           └─→ [04] License Scan   (3-5 min)
T+23min   │               └─→ [05] SAST Python (5-10 min)
T+28min   │                   └─→ [06] SAST JS (5-10 min)
T+33min   │
          ├─→ [02] Backend Tests (parallel com security)
          │        Lint (5 min) + Test (10 min) = 15 min
          │   → Artifacts: coverage.xml, test-results.json
          │
          ├─→ [03] Frontend Tests (parallel com security)
          │        Lint (5 min) + Test (10 min) = 15 min
          │   → Artifacts: test-results.json, coverage.json
          │
          ├─→ [04] Container Scan (after security)
          │        Build (10 min) → Scan (20 min) = 30 min
          │   → Artifacts: trivy-api.json, grype-api.json, etc
          │
          └─→ [05] Build & Push (parallel com security)
               Build (10 min) → SBOM (5 min) = 15 min
               → Artifacts: SBOM (api, web), images pushed

T+45min   ✅ PIPELINE COMPLETA
```

---

## 🔀 Fluxo de Decisão

```
┌─────────────────────────────────────────────────────────┐
│                   Push Detection                         │
│              (branch: main, develop)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ✓ yes
                     │
          ┌──────────▼──────────┐
          │  Trigger Workflows  │
          └──────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    [01-Sec]   [02-Back]    [03-Front]
        │            │            │
        │            ▼            ▼
        │        Lint → Test   Lint → Test
        │            │            │
        ├────────────┼────────────┤
        │            │            │
        └────┬───────┴────────────┘
             │
             ▼
         [04-Container]
             │
          Build → Scan
             │
             ▼
         [05-Build-Push]
             │
        Build → SBOM
             │
             ▼
        ✅ All Green
             │
        ├─ Merge enabled ✓
        ├─ Artifacts available ✓
        └─ SBOM published ✓
```

---

## 🚦 Status Check Matrix

```
┌─────────────────┬──────────┬─────────────┬──────────────┐
│ Workflow        │ Jobs     │ Status      │ Time (est)   │
├─────────────────┼──────────┼─────────────┼──────────────┤
│ 01-Security     │ 6        │ Sequential  │ 30-60 min    │
│ ├─ Gitleaks     │ 1        │ ✅ pass    │ 5-10 min     │
│ ├─ TruffleHog   │ 1        │ ✅ pass    │ 10-15 min    │
│ ├─ Dep-Check    │ 1        │ ✅ pass    │ 5-10 min     │
│ ├─ License      │ 1        │ ✅ pass    │ 3-5 min      │
│ ├─ SAST-Python  │ 1        │ ✅ pass    │ 5-10 min     │
│ └─ SAST-JS      │ 1        │ ✅ pass    │ 5-10 min     │
│                 │          │             │              │
│ 02-Backend      │ 2        │ Sequential  │ 15-25 min    │
│ ├─ Lint         │ 1        │ ✅ pass    │ 5 min        │
│ └─ Test         │ 1        │ ✅ pass    │ 10-20 min    │
│                 │          │             │              │
│ 03-Frontend     │ 2        │ Sequential  │ 15-25 min    │
│ ├─ Lint         │ 1        │ ✅ pass    │ 5 min        │
│ └─ Test         │ 1        │ ✅ pass    │ 10-20 min    │
│                 │          │             │              │
│ 04-Container    │ 2        │ Sequential  │ 30-40 min    │
│ ├─ Build        │ 2 (par)  │ ✅ pass    │ 10 min       │
│ └─ Scan         │ 2 (par)  │ ✅ pass    │ 20-30 min    │
│                 │          │             │              │
│ 05-Build-Push   │ 2        │ Sequential  │ 15-25 min    │
│ ├─ Push         │ 2 (par)  │ ✅ pass    │ 10 min       │
│ └─ SBOM         │ 1        │ ✅ pass    │ 5-15 min     │
└─────────────────┴──────────┴─────────────┴──────────────┘

Total: 14 jobs, 13 dependencies
Parallelization points: 
  - Container Scan: build & scan are parallel pairs (api, web)
  - Build-Push: push jobs are parallel (api, web)
```

---

## 🎯 Pontos de Entrada (Triggers)

```
┌──────────────────────────────────────────────────┐
│          GitHub Events Trigger                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  ✓ Push to main branch                          │
│  ✓ Push to develop branch                       │
│  ✓ Pull Request (opcional, via workflow_call)   │
│  ✓ Schedule (opcional, via schedule)            │
│  ✓ Manual trigger (opcional, via workflow_dispatch) │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📦 Artifacts Gerados

```
┌────────────────────────────────────────────────────┐
│           Artifacts & Outputs                      │
├────────────────────────────────────────────────────┤
│                                                    │
│ 01-Security-Scan                                  │
│ ├─ gitleaks-report.json                          │
│ ├─ trufflehog-report.json                        │
│ ├─ dependency-check-report.html                  │
│ ├─ license-scan-report.json                      │
│ ├─ bandit-report.json (SAST Python)              │
│ └─ eslint-report.json (SAST JS)                  │
│                                                    │
│ 02-Backend-Tests                                  │
│ ├─ coverage.xml                                  │
│ ├─ coverage.html                                 │
│ ├─ test-results.json                             │
│ └─ pytest-report.html                            │
│                                                    │
│ 03-Frontend-Tests                                 │
│ ├─ coverage.json                                 │
│ ├─ test-results.json                             │
│ └─ vitest-report.html                            │
│                                                    │
│ 04-Container-Scan                                 │
│ ├─ trivy-api-vulnerabilities.json                │
│ ├─ trivy-api-config.json                         │
│ ├─ grype-api-report.json                         │
│ ├─ syft-api-sbom.spdx.json                       │
│ ├─ trivy-web-vulnerabilities.json                │
│ ├─ trivy-web-config.json                         │
│ ├─ grype-web-report.json                         │
│ └─ syft-web-sbom.spdx.json                       │
│                                                    │
│ 05-Build-and-Push                                 │
│ ├─ Container Registry (Docker Hub / ECR / etc)   │
│ │  ├─ api:latest, api:tag                        │
│ │  └─ web:latest, web:tag                        │
│ ├─ sbom-api.cyclonedx.json                       │
│ └─ sbom-web.cyclonedx.json                       │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🔍 Como Monitorar

### Via GitHub Actions UI

1. Ir para repository → "Actions"
2. Selecionar workflow em execução
3. Observar jobs em sequência:
   - ✅ Verde = completado
   - 🟡 Amarelo = em execução
   - ❌ Vermelho = falhou

### Via Status Badge (Opcional)

```markdown
![Security Scan](https://github.com/OWNER/REPO/workflows/01-Security-Scan/badge.svg)
![Backend Tests](https://github.com/OWNER/REPO/workflows/02-Backend-Tests/badge.svg)
![Frontend Tests](https://github.com/OWNER/REPO/workflows/03-Frontend-Tests/badge.svg)
![Container Scan](https://github.com/OWNER/REPO/workflows/04-Container-Scan/badge.svg)
![Build & Push](https://github.com/OWNER/REPO/workflows/05-Build-and-Push/badge.svg)
```

### Via Logs (Terminal)

```bash
# Ver logs do último workflow
gh run list --workflow=01-security-scan.yml --limit 1

# Ver detalhes de execução específica
gh run view <run-id> --log
```

---

## ✅ Verificação Pós-Implementação

```
Checklist de validação:

□ Todos os 5 workflows têm `needs:` definido
□ Nenhum job depende de si mesmo (ciclo)
□ Workflow_call está definido em todos os workflows
□ Matrix strategy funciona para paralelizar (api, web)
□ Upload-artifact está v4 (não v3)
□ CodeQL está v3 (não v2)
□ Docker COPY paths estão corretos
□ Git push foi bem sucedido
□ Primeiro push dispara workflows automaticamente
□ Jobs executam em sequência (não paralelo no mesmo workflow)
□ Artifacts aparecem na UI do GitHub Actions
□ Branch protection + status checks funcionam
```

---

## 📝 Resumo Visual

**Antes** (sem dependências):
```
Jobs rodavam em paralelo → impredizível, falhas silenciosas possíveis
```

**Depois** (com needs:):
```
Jobs rodam em sequência garantida → confiável, rastreável, determinístico
```

**Resultado**:
✅ Pipeline sequencial, confiável, com máxima segurança e qualidade

---

## 🚀 Próximos Passos

1. ✅ Implementação completa
2. ✅ Testes locais (GitHub Actions UI)
3. ⏳ Monitorar primeiras execuções
4. ⏳ Ajustar timeouts se necessário
5. ⏳ Adicionar notificações (Slack, Teams, etc)
6. ⏳ Implementar orchestrator (opcional)

---

**Documento criado em**: `docs/ci-cd-devsecops/workflows/`
**Status**: ✅ Implementação Completa
**Próximo**: Clocar documentação original de `.github/` para arquivo
