# 🎯 Pipeline Orchestrator - Sequencial## 🎯 Pipeline Orchestrator - Sequencial



## Visão Geral### Visão Geral



O novo **00-pipeline-orchestrator.yml** controla a execução sequencial de todos os jobs da pipeline CI/CD com as seguintes garantias:O novo **00-pipeline-orchestrator.yml** controla a execução sequencial de todos os jobs da pipeline CI/CD com as seguintes garantias:



1. **Dependências explícitas** entre stages1. **Dependências explícitas** entre stages

2. **Falha em cadeia** - se um stage falha, os subsequentes não executam2. **Falha em cadeia** - se um stage falha, os subsequentes não executam

3. **Paralelismo controlado** - stages que não dependem uns dos outros rodam em paralelo3. **Paralelismo controlado** - stages que não dependem uns dos outros rodami em paralelo

4. **Status final centralizado** - relatório consolidado no final4. **Status final centralizado** - relatório consolidado no final



## Fluxo de Execução### Fluxo de Execução



``````

┌─────────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────────┐

│                  🎯 Pipeline Start                          ││                  🎯 Pipeline Start                          │

└────────────────────┬────────────────────────────────────────┘└────────────────────┬────────────────────────────────────────┘

                     │                     │

        ┌────────────▼────────────┐        ┌────────────▼────────────┐

        │   Stage 1: Backend      │        │   Stage 1️⃣: Backend    │

        │   Tests & Lint         │        │   Tests & Lint         │

        └────────────┬────────────┘        └────────────┬────────────┘

                     │ ✅ success() → continue                     │ ✅ success() → continue

                     │ ❌ failure()  → STOP all                     │ ❌ failure()  → STOP all

                     │                     │

        ┌────────────▼────────────────────────────────────┐        ┌────────────▼────────────────────────────────────┐

        │                                                  │        │                                                  │

   ┌────▼────────────┐              ┌────────────────────┐   ┌────▼────────────┐              ┌────────────────────┐

   │ Stage 2:        │              │  Stage 3:        │   │ Stage 2️⃣:      │              │  Stage 3️⃣:       │

   │ Frontend Tests  │              │  Security Scan    │   │ Frontend Tests  │              │  Security Scan    │

   │ (if: push only) │              │                   │   │ (if: push only) │              │                   │

   └────┬────────────┘              └────────┬───────────┘   └────┬────────────┘              └────────┬───────────┘

        │                                     │        │                                     │

        │  (dependencies: backend-tests)      │        │  (dependencies: backend-tests)      │

        │                                     │        │                                     │

        └────────────┬──────────────────────┘        └────────────┬──────────────────────┘

                     │ Both must pass                     │ Both must pass

                     │                     │

        ┌────────────▼────────────────────────┐        ┌────────────▼────────────────────────┐

        │   Stage 4: Build & Push Images      │        │   Stage 4️⃣: Build & Push Images    │

        │   (if: push only)                   │        │   (if: push only)                   │

        └────────────┬────────────────────────┘        └────────────┬────────────────────────┘

                     │                     │

        ┌────────────▼────────────────────────┐        ┌────────────▼────────────────────────┐

        │   Stage 5: Container Scan & SBOM    │        │   Stage 5️⃣: Container Scan & SBOM  │

        │   (if: push only)                   │        │   (if: push only)                   │

        └────────────┬────────────────────────┘        └────────────┬────────────────────────┘

                     │                     │

        ┌────────────▼────────────────────────┐        ┌────────────▼────────────────────────┐

        │  ✅ Final Status Report              │        │  ✅ Final Status Report              │

        └────────────────────────────────────┘        └────────────────────────────────────┘

``````



## Stages Detalhados### Stages Detalhados



### Stage 1 - Backend Tests & Lint#### 🔵 Stage 1️⃣ Backend Tests & Lint

- **Sempre executa**: em push e pull_request

- **Sempre executa**: em push e pull_request- **Verifica**: 

- **Verifica**:  - Black formatter (line-length=120)

  - Black formatter (line-length=120)  - isort imports

  - isort imports  - flake8 style

  - flake8 style  - mypy type checking

  - mypy type checking  - pytest unit tests

  - pytest unit tests  - pytest integration tests

  - pytest integration tests- **Resultado**: `success` = vai para stage 2-3, `failure` = pipeline para

- **Resultado**: `success` = vai para stage 2-3, `failure` = pipeline para

#### 🟢 Stage 2️⃣ Frontend Tests

### Stage 2 - Frontend Tests- **Executa se**: `success() && github.event_name != 'pull_request'`

- **Dependência**: `needs: backend-tests`

- **Executa se**: `success() && github.event_name != 'pull_request'`- **Verifica**:

- **Dependência**: `needs: backend-tests`  - ESLint

- **Verifica**:  - Prettier formatting

  - ESLint  - Unit tests (Jest)

  - Prettier formatting  - Build success

  - Unit tests (Jest)- **Resultado**: `success` = vai para stage 4, `failure` = pipeline para

  - Build success

- **Resultado**: `success` = vai para stage 4, `failure` = pipeline para#### 🟡 Stage 3️⃣ Security Scan

- **Executa se**: `success()`

### Stage 3 - Security Scan- **Dependência**: `needs: backend-tests`

- **Paralelo com**: Stage 2️⃣ (não precisa esperar)

- **Executa se**: `success()`- **Verifica**:

- **Dependência**: `needs: backend-tests`  - Gitleaks (secrets)

- **Paralelo com**: Stage 2 (não precisa esperar)  - TruffleHog (credential scanning)

- **Verifica**:  - Bandit (Python security)

  - Gitleaks (secrets)  - Safety (dependency vulnerabilities)

  - TruffleHog (credential scanning)  - pip-audit (pip packages)

  - Bandit (Python security)- **Resultado**: `success` = vai para stage 4, `failure` = pipeline para

  - Safety (dependency vulnerabilities)

  - pip-audit (pip packages)#### 🔴 Stage 4️⃣ Build & Push

- **Resultado**: `success` = vai para stage 4, `failure` = pipeline para- **Executa se**: `success() && github.event_name == 'push'`

- **Dependências**: `needs: [backend-tests, security-scan]`

### Stage 4 - Build & Push- **Ação**: 

  - Faz build das imagens Docker (api + web)

- **Executa se**: `success() && github.event_name == 'push'`  - Faz push para registry

- **Dependências**: `needs: [backend-tests, security-scan]`  - Valida manifests

- **Ação**:- **Resultado**: `success` = vai para stage 5, `failure` = pipeline para

  - Faz build das imagens Docker (api + web)

  - Faz push para registry#### 🟠 Stage 5️⃣ Container Scan & SBOM

  - Valida manifests- **Executa se**: `success() && github.event_name == 'push'`

- **Resultado**: `success` = vai para stage 5, `failure` = pipeline para- **Dependência**: `needs: build-and-push`

- **Ação**:

### Stage 5 - Container Scan & SBOM  - Trivy vulnerability scanning

  - Grype security scanning

- **Executa se**: `success() && github.event_name == 'push'`  - Syft SBOM generation (3-tier fallback)

- **Dependência**: `needs: build-and-push`  - Generate reports

- **Ação**:- **Resultado**: `success` = pipeline OK, `failure` = pipeline FAIL

  - Trivy vulnerability scanning

  - Grype security scanning#### ✅ Status Final

  - Syft SBOM generation (3-tier fallback)- **Sempre executa**: mesmo se algum stage falhar

  - Generate reports- **Condicional**: `if: always()`

- **Resultado**: `success` = pipeline OK, `failure` = pipeline FAIL- **Relatório**: Mostra status de todos os stages

- **Falha final**: se algum stage falhou, o job retorna exit 1

### Status Final

### Lógica de Condições

- **Sempre executa**: mesmo se algum stage falhar

- **Condicional**: `if: always()````yaml

- **Relatório**: Mostra status de todos os stages# Stage 2, 3: Requerem sucesso do Stage 1

- **Falha final**: se algum stage falhou, o job retorna exit 1needs: backend-tests

if: success()

## Lógica de Condições

# Stage 2: Apenas em push (não em PR)

```yamlif: success() && github.event_name != 'pull_request'

# Stage 2, 3: Requerem sucesso do Stage 1

needs: backend-tests# Stage 3: Sempre que Stage 1 passar

if: success()if: success()



# Stage 2: Apenas em push (não em PR)# Stage 4: Sucesso de 1 e 3, apenas em push

if: success() && github.event_name != 'pull_request'needs: [backend-tests, security-scan]

if: success() && github.event_name == 'push'

# Stage 3: Sempre que Stage 1 passar

if: success()# Stage 5: Sucesso de 4, apenas em push

needs: build-and-push

# Stage 4: Sucesso de 1 e 3, apenas em pushif: success() && github.event_name == 'push'

needs: [backend-tests, security-scan]

if: success() && github.event_name == 'push'# Status: Sempre executa mesmo com falhas

if: always()

# Stage 5: Sucesso de 4, apenas em push```

needs: build-and-push

if: success() && github.event_name == 'push'### Triggers



# Status: Sempre executa mesmo com falhasO orchestrator é disparado por:

if: always()

```1. **Push para main/develop**

   - Executa todos os 5 stages sequencialmente

## Triggers   - Finaliza com build & push se tudo passar



O orchestrator é disparado por:2. **Pull Request para main/develop**

   - Executa apenas Stage 1️⃣ (Backend Tests & Lint)

1. **Push para main/develop**   - Pula stages de build/push (security-scan não roda)

   - Executa todos os 5 stages sequencialmente   - Relatório de status

   - Finaliza com build & push se tudo passar

3. **Workflow Dispatch (manual)**

2. **Pull Request para main/develop**   - Mesma execução que push

   - Executa apenas Stage 1 (Backend Tests & Lint)   - Útil para re-run manual

   - Pula stages de build/push (security-scan não roda)

   - Relatório de status### Integrações com Workflows Chamados



3. **Workflow Dispatch (manual)**O orchestrator usa `uses` para chamar outros workflows:

   - Mesma execução que push

   - Útil para re-run manual```yaml

backend-tests:

## Integrações com Workflows Chamados  uses: ./.github/workflows/02-backend-tests.yml

  

O orchestrator usa `uses` para chamar outros workflows:frontend-tests:

  uses: ./.github/workflows/03-frontend-tests.yml

```yaml  needs: backend-tests

backend-tests:  

  uses: ./.github/workflows/02-backend-tests.ymlsecurity-scan:

  uses: ./.github/workflows/01-security-scan.yml

frontend-tests:  needs: backend-tests

  uses: ./.github/workflows/03-frontend-tests.yml  

  needs: backend-testsbuild-and-push:

  uses: ./.github/workflows/05-build-and-push.yml

security-scan:  needs: [backend-tests, security-scan]

  uses: ./.github/workflows/01-security-scan.yml  secrets: inherit

  needs: backend-tests  

container-scan:

build-and-push:  uses: ./.github/workflows/04-container-scan.yml

  uses: ./.github/workflows/05-build-and-push.yml  needs: build-and-push

  needs: [backend-tests, security-scan]```

  secrets: inherit

### Monitoramento

container-scan:

  uses: ./.github/workflows/04-container-scan.yml1. **GitHub Actions tab**: Veja status em tempo real

  needs: build-and-push2. **Status checks na PR**: Verificação automática

```3. **Final Report**: Resumo de todos os stages

4. **Security events**: Abas de segurança se houver findings

## Monitoramento

### Troubleshooting

1. **GitHub Actions tab**: Veja status em tempo real

2. **Status checks na PR**: Verificação automática**Se Stage 1 falhar:**

3. **Final Report**: Resumo de todos os stages```bash

4. **Security events**: Abas de segurança se houver findings# Verifique localmente

python -m black --check backend/app backend/tests --line-length=120

## Troubleshootingpython -m isort --check-only backend/app backend/tests

python -m flake8 backend/app backend/tests

### Se Stage 1 falharpython -m mypy backend/app backend/tests

pytest backend/tests/

```bash```

python -m black --check backend/app backend/tests --line-length=120

python -m isort --check-only backend/app backend/tests**Se Stage 3 falhar:**

python -m flake8 backend/app backend/tests```bash

python -m mypy backend/app backend/tests# Verifique secrets

pytest backend/tests/gitleaks detect --source=. --verbose

```

# Verifique dependências

### Se Stage 3 falharpip-audit

safety check

```bash```

gitleaks detect --source=. --verbose

pip-audit**Se Stage 4 falhar:**

safety check```bash

```# Verifique Docker localmente

docker build -t app:test .

### Se Stage 4 falhardocker push registry.com/app:test

```

```bash

docker build -t app:test .**Se Stage 5 falhar:**

docker push registry.com/app:test- Verifique SBOM generation (já tem fallback)

```- Verifique vulnerabilidades com Trivy/Grype localmente



### Se Stage 5 falhar### Próximas Melhorias



- Verifique SBOM generation (já tem fallback)- [ ] Adicionar notificações em Slack/Teams

- Verifique vulnerabilidades com Trivy/Grype localmente- [ ] Adicionar approval gates para push em produção

- [ ] Adicionar deployment stages (staging → production)

## Próximas Melhorias- [ ] Adicionar performance benchmarks

- [ ] Adicionar artifact retention policies

- Adicionar notificações em Slack/Teams
- Adicionar approval gates para push em produção
- Adicionar deployment stages (staging → production)
- Adicionar performance benchmarks
- Adicionar artifact retention policies
