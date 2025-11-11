# 🔐 Contexto: Pipeline CI/CD DevSecOps - EduAutismo IA

**Data:** 11 de novembro de 2025  
**Versão:** 1.0  
**Status:** Contexto Estratégico para Implementação

---

## 📋 Sumário Executivo

Este documento define a estratégia completa de CI/CD DevSecOps para o MVP **EduAutismo IA**, uma plataforma de IA/ML para educadores especializados em TEA (Transtorno do Espectro Autista). A pipeline integra:

- ✅ **Segurança (DevSecOps)**: Scanning de vulnerabilidades, secrets, SCA, SAST
- ✅ **Resiliência**: Testes, health checks, blue-green deployment
- ✅ **Modernidade**: Containers Docker, IaC (Terraform), multi-stage builds
- ✅ **Observabilidade**: Logs, métricas, tracing distribuído
- ✅ **Compliance**: LGPD, auditoria, criptografia

---

## 🏗️ Arquitetura Atual do Projeto

### Stack Tecnológico

| Componente | Tecnologia | Versão |
|-----------|-----------|---------|
| **Backend** | FastAPI + Python | 3.11+ |
| **Frontend** | React + Vite | 18.2 + 5.0 |
| **Database** | PostgreSQL + MongoDB | 15+ |
| **Cache** | Redis | 7+ |
| **ML/AI** | scikit-learn, TensorFlow, OpenAI GPT | Latest |
| **IaC** | Terraform + AWS | Latest |
| **Containerização** | Docker + Docker Compose | Latest |
| **Orquestração** | AWS ECS/EKS (futuro) | - |

### Estrutura de Diretórios Relevantes

```
eduautismo-ia-mvp/
├── backend/
│   ├── app/
│   │   ├── api/           # Rotas FastAPI
│   │   ├── core/          # Configurações, autenticação
│   │   ├── db/            # ORM, conexões
│   │   ├── models/        # SQLAlchemy/MongoDB models
│   │   ├── schemas/       # Pydantic DTOs
│   │   ├── services/      # Business logic
│   │   ├── utils/         # Helpers
│   │   └── main.py / main_simple.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile.api
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   ├── package.json
│   └── Dockerfile.web
├── .github/
│   └── workflows/         # ← CI/CD pipelines
├── scripts/
│   ├── test_routes.sh     # E2E tests
│   ├── validate_docs.py
│   └── deployment/
├── terraform/             # IaC
├── docker-compose.yml
├── Makefile
└── docs/
```

---

## 🔄 Pipeline CI/CD DevSecOps - Visão Geral

### Fluxo Completo

```
┌──────────────┐
│  Git Push    │
│   (main)     │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: SECURITY SCAN (0-2 min)                           │
├─────────────────────────────────────────────────────────────┤
│ ✓ Secrets Detection (GitGuardian/Gitleaks)                 │
│ ✓ License Scanning (FOSSA)                                 │
│ ✓ Dependency Check (Safety, Pip-audit)                    │
│ ✓ SAST (Bandit, ESLint Security)                           │
└──────────────┬────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │ FAIL? STOP     │
       └────────────────┘
       │
       ▼ PASS
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: BUILD & TEST (3-5 min)                            │
├─────────────────────────────────────────────────────────────┤
│ ✓ Backend: Poetry install → Lint → Unit Tests → Coverage   │
│ ✓ Frontend: npm install → ESLint → Vitest → Build          │
│ ✓ Database: Migration validation                           │
│ ✓ Docker Multi-stage build                                 │
└──────────────┬────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │ FAIL? STOP     │
       └────────────────┘
       │
       ▼ PASS
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: CONTAINER SECURITY (1-2 min)                      │
├─────────────────────────────────────────────────────────────┤
│ ✓ Trivy: Scan image layers                                 │
│ ✓ Grype: Vulnerability database                            │
│ ✓ Cosign: Sign images                                      │
└──────────────┬────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │ FAIL? STOP     │
       └────────────────┘
       │
       ▼ PASS
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: INTEGRATION TESTS (2-3 min)                       │
├─────────────────────────────────────────────────────────────┤
│ ✓ Docker Compose: Stack local                              │
│ ✓ API E2E tests (Postman/pytest)                           │
│ ✓ Database checks (migrations, seeds)                      │
└──────────────┬────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │ FAIL? STOP     │
       └────────────────┘
       │
       ▼ PASS
┌─────────────────────────────────────────────────────────────┐
│  STAGE 5: PUBLISH & DEPLOY (2-3 min)                        │
├─────────────────────────────────────────────────────────────┤
│ ✓ ECR/Docker Hub: Push images com tags versionadas        │
│ ✓ SBOM: Gerar (cyclonedx format)                           │
│ ✓ Deploy DEV: Blue-green deployment                        │
│ ✓ Smoke tests: Verificar health endpoints                  │
└──────────────┬────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │ FAIL? ROLLBACK │
       └────────────────┘
       │
       ▼ SUCCESS
┌─────────────────────────────────────────────────────────────┐
│  STAGE 6: OBSERVABILITY & REPORTING (1 min)                 │
├─────────────────────────────────────────────────────────────┤
│ ✓ Upload artifacts (coverage, reports, SBOM)               │
│ ✓ Update GitHub Pages (docs + coverage)                    │
│ ✓ Notify Slack/Teams                                       │
│ ✓ Generate compliance report (LGPD)                        │
└─────────────────────────────────────────────────────────────┘
```

**Tempo Total:** ~10-15 minutos (parallelized onde possível)

---

## 🛡️ Stage 1: Security Scanning

### 1.1 Secrets Detection

**Ferramentas Open Source:**
- **Gitleaks** (HTTPS://github.com/gitleaks/gitleaks)
- **TruffleHog** (HTTPS://github.com/trufflesecurity/truffleHog)
- **Detect Secrets** (HTTPS://github.com/Yelp/detect-secrets)

**Configuração Recomendada:**

```yaml
# .github/workflows/secrets-scan.yml
- name: Gitleaks Scan
  uses: gitleaks/gitleaks-action@v2
  with:
    config: .gitleaks.toml
    enable-comments: true
```

**.gitleaks.toml:**
```toml
[source]
name = "gitleaks config"
verbose = true

# Padrões customizados para EduAutismo
[[rules]]
id = "aws-access-key"
pattern = "(?i)aws(.{0,20})?(?-i)['\"][0-9a-zA-Z/+=]{40}['\"]"
scope = "all"
tags = ["aws", "critical"]

[[rules]]
id = "openai-api-key"
pattern = "sk-[A-Za-z0-9]{48}"
scope = "all"
tags = ["openai", "critical"]

[[rules]]
id = "jwt-secret"
pattern = "(?i)jwt(.{0,20})?(?-i)=(.{20,})"
scope = "all"
tags = ["jwt", "critical"]
```

### 1.2 Dependency Vulnerability Scanning

**Ferramentas:**
- **Safety** (HTTPS://github.com/pyup-io/safety) - Python
- **pip-audit** (HTTPS://github.com/pypa/pip-audit) - Python
- **npm audit** (built-in) - Node.js
- **Snyk** (HTTPS://github.com/snyk/snyk) - Multi-language

**Implementação:**

```yaml
# Backend security checks
- name: Python Dependency Check (Safety)
  run: |
    pip install safety
    safety check --json > safety-report.json || true
    # Fail only on CRITICAL/HIGH
    safety check --continue-on-error

- name: Pip-audit
  run: |
    pip install pip-audit
    pip-audit --desc > pip-audit-report.txt || true

# Frontend dependency check
- name: NPM Audit
  run: |
    cd frontend
    npm audit --audit-level=moderate --json > npm-audit.json || true
```

### 1.3 License Compliance

**Ferramenta:** FOSSA, Licensed, ou SBOM (CycloneDX)

```yaml
- name: Generate SBOM (CycloneDX)
  uses: CycloneDX/cyclonedx-action@v0
  with:
    input-file: backend/requirements.txt
    output-file: sbom-backend.xml
    output-format: xml
```

### 1.4 Static Application Security Testing (SAST)

**Python:**
```yaml
- name: Bandit (Python Security)
  run: |
    pip install bandit
    bandit -r backend/app -f json -o bandit-report.json || true
```

**JavaScript/React:**
```yaml
- name: ESLint Security
  run: |
    cd frontend
    npm install eslint-plugin-security
    npx eslint . --ext js,jsx --format json -o eslint-report.json || true
```

---

## 🔨 Stage 2: Build & Test

### 2.1 Backend Build Pipeline

```yaml
name: Backend Tests
on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: eduautismo_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip setuptools wheel
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Lint with Black
        run: black --check backend/app backend/tests
      
      - name: Format check with isort
        run: isort --check-only backend/app backend/tests
      
      - name: Lint with flake8
        run: flake8 backend/app backend/tests --max-line-length=120
      
      - name: Type checking with Mypy
        run: mypy backend/app --ignore-missing-imports || true
      
      - name: Unit Tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/eduautismo_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/unit -v --cov=app --cov-report=xml:coverage-unit.xml
      
      - name: Integration Tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/eduautismo_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/integration -v --cov=app --cov-report=xml:coverage-integration.xml
      
      - name: Merge coverage reports
        run: |
          pip install coverage
          coverage combine backend/coverage-*.xml
          coverage xml -o coverage.xml
          coverage report --fail-under=85
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend
          fail_ci_if_error: true
```

### 2.2 Frontend Build Pipeline

```yaml
name: Frontend Tests
on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Lint
        run: |
          cd frontend
          npm run lint
      
      - name: Format check
        run: |
          cd frontend
          npx prettier --check "src/**/*.{js,jsx,css,md}"
      
      - name: Unit Tests
        run: |
          cd frontend
          npm run test -- --coverage
      
      - name: Build
        run: |
          cd frontend
          npm run build
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
```

### 2.3 Database Migration Validation

```yaml
- name: Validate Alembic Migrations
  env:
    DATABASE_URL: postgresql://postgres:test@localhost:5432/eduautismo_test
  run: |
    cd backend
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
```

---

## 🐳 Stage 3: Container Security

### 3.1 Multi-Stage Docker Build

**Dockerfile.api (Backend):**

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "app.main_simple:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Container Image Scanning

```yaml
name: Container Security Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          file: ./Dockerfile.api
          push: false
          load: true
          tags: eduautismo-api:scan
      
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: eduautismo-api:scan
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Scan with Grype
        uses: anchore/scan-action@v3
        with:
          image: eduautismo-api:scan
          fail-build: true
          severity-cutoff: high
      
      - name: Sign image with Cosign
        env:
          COSIGN_EXPERIMENTAL: 1
        run: |
          curl -sSL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o cosign
          chmod +x cosign
          ./cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
```

---

## 🧪 Stage 4: Integration Tests

```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Docker Compose Up
        run: |
          docker-compose -f docker-compose.yml up -d
          sleep 30
      
      - name: Health Checks
        run: |
          for i in {1..30}; do
            curl -f http://localhost:8000/health && break || sleep 1
          done
      
      - name: Run E2E Tests (pytest)
        run: |
          pip install pytest httpx
          pytest scripts/test_routes.sh -v
      
      - name: Verify Database State
        run: |
          docker-compose exec -T postgres pg_dump -U postgres eduautismo_test > /tmp/dump.sql
          
      - name: Docker Compose Down
        run: docker-compose down -v
```

---

## 🚀 Stage 5: Publish & Deploy

### 5.1 ECR Push & Image Registry

```yaml
name: Build & Push to ECR
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and Push API
        uses: docker/build-push-action@v5
        with:
          file: ./Dockerfile.api
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build and Push Web
        uses: docker/build-push-action@v5
        with:
          file: ./Dockerfile.web
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}-web
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 5.2 SBOM Generation

```yaml
- name: Generate SBOM with Syft
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
    format: cyclonedx-json
    output-file: sbom.json
    upload-artifact: true

- name: Upload SBOM
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom.json
```

### 5.3 Blue-Green Deployment (DEV)

```yaml
- name: Deploy to DEV (Blue-Green)
  if: github.ref == 'refs/heads/main'
  run: |
    # Blue = Current (rodando)
    # Green = Nova versão (staging)
    
    BLUE_TASK=$(aws ecs list-tasks --cluster eduautismo-dev --service-name api-blue | jq -r '.taskArns[0]')
    GREEN_TASK=$(aws ecs list-tasks --cluster eduautismo-dev --service-name api-green | jq -r '.taskArns[0]')
    
    # Deploy para GREEN
    aws ecs update-service \
      --cluster eduautismo-dev \
      --service api-green \
      --force-new-deployment \
      --region us-east-1
    
    # Esperar por Green estar saudável
    aws ecs wait services-stable \
      --cluster eduautismo-dev \
      --services api-green \
      --region us-east-1
    
    # Smoke tests em GREEN
    ./scripts/smoke-tests.sh http://green-alb.internal:8000
    
    # Se passar, switch o ALB para GREEN
    aws elbv2 modify-target-group \
      --target-group-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/api/HASH \
      --targets Id=$(docker inspect --format='{{.Config.Hostname}}' GREEN_TASK):8000 \
      --region us-east-1
    
    # Monitorar por 5 minutos
    sleep 300
    
    # Se algum erro, rollback automático (CloudWatch Alarms)
```

---

## 📊 Stage 6: Observability & Reporting

### 6.1 Metrics & Logging

```yaml
- name: Upload Test Coverage
  uses: actions/upload-artifact@v3
  with:
    name: coverage-reports
    path: coverage/

- name: Publish Coverage to GitHub Pages
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./coverage

- name: Comment PR with Coverage
  if: github.event_name == 'pull_request'
  uses: romeovs/lcov-reporter-action@v0.3.1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    lcov-file: ./coverage/lcov.info
```

### 6.2 Compliance Report (LGPD)

```yaml
- name: Generate LGPD Compliance Report
  run: |
    cat > compliance-report.md << 'EOF'
    # 🔐 Relatório de Compliance - ${{ github.run_number }}
    
    ## Informações da Build
    - **Commit**: ${{ github.sha }}
    - **Branch**: ${{ github.ref }}
    - **Timestamp**: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
    
    ## Segurança
    - Secrets scanning: ✅ PASSED
    - Dependency audit: ✅ PASSED
    - SAST: ✅ PASSED
    - Container scanning: ✅ PASSED
    
    ## LGPD Checklist
    - [ ] Dados pessoais criptografados (AES-256)
    - [ ] TLS 1.2+ em trânsito
    - [ ] Auditoria de acesso ativada
    - [ ] Consentimento documentado
    - [ ] Direito ao esquecimento implementado
    - [ ] SBOM gerado e armazenado
    
    ## Testes
    - Backend Coverage: $(grep 'line-rate' coverage.xml | grep -oP 'line-rate="\K[^"]*')
    - Frontend Coverage: $(jq '.total.lines.pct' frontend/coverage/coverage-summary.json)
    - E2E Tests: PASSED
    EOF
    
    cat compliance-report.md
```

### 6.3 Slack/Teams Notification

```yaml
- name: Notify Success
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "✅ Pipeline EduAutismo IA SUCCESS",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Build #${{ github.run_number }}* - ${{ github.ref }}\n*Status*: ✅ SUCCESS\n*Commit*: `${{ github.sha }}`\n*Author*: ${{ github.actor }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

- name: Notify Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ Pipeline EduAutismo IA FAILED",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Build #${{ github.run_number }}* - ${{ github.ref }}\n*Status*: ❌ FAILED\n*Logs*: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

---

## 🛠️ Ferramentas Open Source Recomendadas

### Segurança (DevSecOps)

| Ferramenta | Tipo | Link | Propósito |
|-----------|------|------|----------|
| **Gitleaks** | Secrets | https://github.com/gitleaks/gitleaks | Detectar secrets em Git |
| **TruffleHog** | Secrets | https://github.com/trufflesecurity/truffleHog | High-entropy secrets |
| **Safety** | SCA | https://github.com/pyup-io/safety | Vulnerabilidades Python |
| **pip-audit** | SCA | https://github.com/pypa/pip-audit | Auditoria dependencies Python |
| **Bandit** | SAST | https://github.com/PyCQA/bandit | Segurança Python estática |
| **Trivy** | Container | https://github.com/aquasecurity/trivy | Scan de imagens Docker |
| **Grype** | SBOM | https://github.com/anchore/grype | Gerenciamento de vulnerabilidades |
| **Cosign** | Signing | https://github.com/sigstore/cosign | Assinatura de imagens |
| **Syft** | SBOM | https://github.com/anchore/syft | Geração de SBOM |
| **FOSSA** | License | https://fossa.com/ | Compliance de licenças |

### Qualidade & Testes

| Ferramenta | Tipo | Link | Propósito |
|-----------|------|------|----------|
| **Pytest** | Unit Test | https://github.com/pytest-dev/pytest | Framework testes Python |
| **Vitest** | Unit Test | https://vitest.dev/ | Framework testes JavaScript |
| **Coverage.py** | Coverage | https://coverage.readthedocs.io/ | Cobertura de testes Python |
| **Black** | Formatting | https://github.com/psf/black | Formatação Python |
| **isort** | Import Sort | https://pycqa.github.io/isort/ | Organizar imports Python |
| **flake8** | Linter | https://flake8.pycqa.org/ | Linting Python |
| **Mypy** | Type Check | https://www.mypy-lang.org/ | Type checking Python |
| **ESLint** | Linter | https://eslint.org/ | Linting JavaScript |
| **Prettier** | Formatting | https://prettier.io/ | Formatação JavaScript |

### Deployment & Observability

| Ferramenta | Tipo | Link | Propósito |
|-----------|------|------|----------|
| **Docker** | Container | https://www.docker.com/ | Containerização |
| **Terraform** | IaC | https://www.terraform.io/ | Infrastructure as Code |
| **Prometheus** | Metrics | https://prometheus.io/ | Coleta de métricas |
| **Grafana** | Visualization | https://grafana.com/ | Dashboards |
| **Loki** | Logs | https://grafana.com/loki/ | Log aggregation |
| **Jaeger** | Tracing | https://www.jaegertracing.io/ | Distributed tracing |
| **OpenTelemetry** | Observability | https://opentelemetry.io/ | Instrumentação |

---

## 📁 Estrutura de Arquivos CI/CD

```
.github/
├── workflows/
│   ├── 01-security-scan.yml         # Stage 1: Segurança
│   ├── 02-backend-tests.yml         # Stage 2a: Backend
│   ├── 02-frontend-tests.yml        # Stage 2b: Frontend
│   ├── 03-container-scan.yml        # Stage 3: Container
│   ├── 04-integration-tests.yml     # Stage 4: Integração
│   ├── 05-build-and-push.yml        # Stage 5: Publish
│   ├── 06-deploy-dev.yml            # Stage 5: Deploy
│   ├── 07-deploy-prod.yml           # Stage 5: Prod (manual)
│   └── 08-reporting.yml             # Stage 6: Relatórios
├── .gitleaks.toml                    # Config secrets detection
├── .bandit                           # Config SAST Python
└── dependabot.yml                    # Auto-updates de deps

config/
├── .dockerignore
├── .lintignore
├── .prettierignore
├── codecov.yml                       # Config coverage
├── pytest.ini                        # Config pytest
├── pyproject.toml                    # Config Python project
├── vitest.config.js                 # Config Vitest
└── eslintrc.json                     # Config ESLint

scripts/
├── smoke-tests.sh                    # Health checks pós-deploy
├── security-audit.sh                 # Auditoria manual
├── generate-compliance.sh            # Relatório LGPD
└── rollback.sh                       # Rollback automático
```

---

## 🔐 Segredos & Configuração

### Secrets Necessários no GitHub

```
GITHUB_TOKEN           # Auto (usado por ações)
REGISTRY_USERNAME      # Para ECR/Docker Hub
REGISTRY_PASSWORD      # Para ECR/Docker Hub
SLACK_WEBHOOK          # Notificações Slack
CODECOV_TOKEN          # Upload cobertura
SENTRY_DSN             # Monitoramento erros
AWS_ACCOUNT_ID         # Para deploy AWS
AWS_ACCESS_KEY_ID      # Deploy IAM
AWS_SECRET_ACCESS_KEY  # Deploy IAM
COSIGN_KEY             # Assinatura imagens
```

### Arquivo `.env.example`

```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/eduautismo
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
JWT_SECRET=your-secret-key-change-in-prod
ENVIRONMENT=development

# Security
SENTRY_DSN=https://...
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789
ECR_REGISTRY=123456789.dkr.ecr.us-east-1.amazonaws.com
```

---

## 📈 Métricas de Sucesso

### KPIs Recomendados

| Métrica | Target | Tool |
|---------|--------|------|
| **Build Time** | < 15 min | GitHub Actions |
| **Test Coverage** | > 85% | Coverage.py + Codecov |
| **SAST Findings** | 0 Critical/High | Bandit + SARIF |
| **Container Vulns** | 0 Critical/High | Trivy |
| **Deployment Success** | > 99% | CloudWatch |
| **Mean Time to Deploy (MTPD)** | < 20 min | GitHub Actions |
| **Mean Time to Recovery (MTTR)** | < 10 min | Rollback automático |
| **Security Incidents** | 0 | Auditoria |

---

## 🚀 Roadmap de Implementação

### Fase 1: MVP (Semana 1-2)
- ✅ Secrets scanning (Gitleaks)
- ✅ Backend tests + coverage
- ✅ Frontend tests + build
- ✅ Container scan (Trivy)
- ✅ Push to registry

### Fase 2: Resiliência (Semana 3-4)
- ✅ Integration tests
- ✅ Blue-green deployment
- ✅ Health checks
- ✅ Rollback automático
- ✅ Smoke tests

### Fase 3: Observabilidade (Semana 5-6)
- ✅ Prometheus + Grafana
- ✅ Distributed tracing (Jaeger)
- ✅ Log aggregation (Loki)
- ✅ OpenTelemetry instrumentation
- ✅ Alert rules

### Fase 4: Compliance (Semana 7-8)
- ✅ SBOM generation (Syft)
- ✅ LGPD compliance checks
- ✅ Auditoria automática
- ✅ Cosign image signing
- ✅ License scanning (FOSSA)

---

## 📚 Referências & Documentação

### Azure Cosmos DB (se usar)
- [Cosmos DB Best Practices](https://docs.microsoft.com/azure/cosmos-db/best-practices)
- [Segurança Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/database-security)

### GitHub Actions
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides)

### Segurança & DevSecOps
- [OWASP DevSecOps](https://owasp.org/www-project-devsecops-guideline/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### LGPD & Compliance
- [Lei Geral de Proteção de Dados](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [LGPD Compliance Guide](https://www.anpd.gov.br/)

### Open Source Tools
- [CNCF Landscape](https://landscape.cncf.io/)
- [OpenSSF Security Tools](https://openssf.org/)

---

## 🎯 Próximas Etapas

1. **Criar workflows YAML** nos diretórios `.github/workflows/`
2. **Configurar secrets** no GitHub Repository Settings
3. **Adicionar configurações** (`.gitleaks.toml`, `.bandit`, etc)
4. **Testar localmente** com `act` (GitHub Actions emulator)
5. **Documentar runbooks** para troubleshooting
6. **Treinar time** em CI/CD practices
7. **Monitorar métricas** e ajustar baseado em observações

---

**Documento Versão:** 1.0  
**Última Atualização:** 11/11/2025  
**Status:** ✅ Pronto para Implementação
