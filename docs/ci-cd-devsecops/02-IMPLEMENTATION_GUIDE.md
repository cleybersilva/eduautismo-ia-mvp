# 🚀 Guia de Implementação: CI/CD DevSecOps

**Projeto:** EduAutismo IA  
**Data:** 11 de novembro de 2025  

---

## 📋 Checklist de Implementação

### Fase 1: Setup Inicial (1-2 horas)

- [ ] **Revisar documentação completa**
  ```bash
  cat docs/CI_CD_DEVSECOPS_CONTEXT.md
  ```

- [ ] **Verificar estrutura de diretórios**
  ```bash
  ls -la .github/workflows/
  ls -la backend/
  ls -la frontend/
  ```

- [ ] **Criar arquivo `.env.example` (if not exists)**
  ```bash
  cp .env .env.example
  # Remove all secrets from .env.example
  ```

### Fase 2: Configurar Secrets no GitHub (30 min)

1. **Ir para Settings do Repositório**
   - GitHub → Seu Repo → Settings → Secrets and variables → Actions

2. **Adicionar secrets necessários:**

   ```
   GITHUB_TOKEN          ← Auto (não precisa adicionar)
   REGISTRY_USERNAME     ← Seu username GitHub
   REGISTRY_PASSWORD     ← GitHub token com repo + packages scope
   SLACK_WEBHOOK         ← URL do webhook Slack (opcional)
   CODECOV_TOKEN         ← Token Codecov (opcional mas recomendado)
   SENTRY_DSN           ← DSN Sentry (opcional)
   ```

3. **Criar GitHub Token para Registry:**
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Selecionar escopos: `repo`, `packages`, `write:packages`
   - Copiar token para `REGISTRY_PASSWORD`

### Fase 3: Validar Workflows Localmente (1 hora - OPCIONAL)

```bash
# Instalar GitHub CLI
# https://cli.github.com/

# Instalar act (GitHub Actions emulator)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Testar workflow de segurança
act push --workflow .github/workflows/01-security-scan.yml

# Testar workflow de backend
act push --workflow .github/workflows/02-backend-tests.yml -s GITHUB_TOKEN=$(gh auth token)
```

### Fase 4: Fazer Push dos Arquivos (30 min)

```bash
# 1. Criar branch
git checkout -b feat/ci-cd-devsecops

# 2. Adicionar todos arquivos
git add .github/workflows/
git add docs/CI_CD_DEVSECOPS_CONTEXT.md
git add DEVSECOPS_SUMMARY.md
git add .gitleaks.toml
git add .bandit
git add backend/pytest.ini
git add codecov.yml

# 3. Commit
git commit -m "ci: Add DevSecOps pipeline with GitHub Actions

- Add 5 main workflows (security, tests, container, build, deploy)
- Add Gitleaks, Bandit, Trivy, and container scanning
- Add automated testing (pytest, vitest, coverage)
- Add SBOM generation and compliance reporting
- Add blue-green deployment support
- Refs: docs/CI_CD_DEVSECOPS_CONTEXT.md"

# 4. Push
git push origin feat/ci-cd-devsecops

# 5. Abrir PR (via GitHub ou CLI)
gh pr create --title "ci: Add DevSecOps CI/CD Pipeline" \
  --body "Implementa pipeline completa de CI/CD com segurança, testes e observabilidade. Veja docs/CI_CD_DEVSECOPS_CONTEXT.md"
```

### Fase 5: Review & Merge (1 hora)

1. **GitHub Actions irão rodar automaticamente na PR**
2. **Revisar resultados** (Actions tab)
3. **Corrigir qualquer erro** (se houver)
4. **Fazer merge** para main

```bash
gh pr merge <PR_NUMBER> --auto --squash
```

### Fase 6: Configurar Branch Protection (30 min)

1. **GitHub → Settings → Branches → Add Rule**

2. **Configurar proteção para `main`:**
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Restrict who can push to matching branches (admins only)

3. **Status checks obrigatórios:**
   - ✅ Security: Secrets Scanning
   - ✅ Test: Backend Tests
   - ✅ Test: Frontend Tests
   - ✅ Security: Container Scan
   - ✅ Build: Push to Registry

---

## 🔧 Configurações por Ferramenta

### Gitleaks

**Arquivo:** `.gitleaks.toml` (já criado)

**Testar localmente:**
```bash
# Instalar
brew install gitleaks  # macOS
# ou via Docker
docker run -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo

# Escanear
gitleaks detect --config .gitleaks.toml
```

### Bandit (Python SAST)

**Arquivo:** `.bandit` (já criado)

**Testar localmente:**
```bash
# Instalar
pip install bandit

# Escanear
bandit -r backend/app -c .bandit

# Gerar relatório
bandit -r backend/app -f json -o bandit-report.json
```

### Pytest

**Arquivo:** `backend/pytest.ini` (já criado)

**Testar localmente:**
```bash
cd backend

# Rodar todos os testes
pytest

# Rodar com cobertura
pytest --cov=app --cov-report=html

# Rodar teste específico
pytest tests/unit/test_auth.py -v

# Rodar apenas testes rápidos
pytest -m "not slow"
```

### Vitest (JavaScript)

**Testar localmente:**
```bash
cd frontend

# Rodar testes
npm run test

# Rodar com cobertura
npm run test -- --coverage

# Watch mode
npm run test -- --watch
```

### Docker & Trivy

**Testar localmente:**
```bash
# Build image
docker build -f Dockerfile.api -t eduautismo-api:test .

# Instalar Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Escanear imagem
./trivy image --severity HIGH,CRITICAL eduautismo-api:test

# Gerar SBOM
./trivy image --format cyclonedx -o sbom.json eduautismo-api:test
```

---

## 🐛 Troubleshooting

### Problema: Workflow não aparece na aba Actions

**Solução:**
```bash
# Verificar sintaxe YAML
yamllint .github/workflows/*.yml

# Ou validar com GitHub CLI
gh workflow list
```

### Problema: Tests falhando localmente mas passando na CI

**Solução:**
```bash
# Usar mesmo Python/Node que CI
pyenv install 3.11
pyenv local 3.11

# Instalar dependências exatamente como CI
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
cd frontend && npm ci
```

### Problema: "permission denied" no Trivy

**Solução:**
```bash
# Adicionar permissão execute
chmod +x ./trivy

# Ou use via Docker
docker run -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ...
```

### Problema: Coverage abaixo do threshold

**Solução:**
```bash
# Ver relatório de cobertura
coverage report
coverage html

# Abrir em navegador
open htmlcov/index.html

# Ajustar threshold em pytest.ini se necessário
# --cov-fail-under=80  (reduzir de 85 para 80)
```

---

## 📊 Monitorando a Pipeline

### GitHub Actions Dashboard

```bash
# Ver todos os workflows
gh workflow list

# Ver status de um workflow
gh workflow view 01-security-scan.yml

# Ver logs de um run
gh run list --workflow 02-backend-tests.yml
gh run view <RUN_ID> --log

# Reexecutar um workflow
gh run rerun <RUN_ID>

# Cancelar um workflow
gh run cancel <RUN_ID>
```

### Métricas para Acompanhar

```
1. Build Time: deve estar < 15 min
2. Test Coverage: deve estar > 85%
3. Security Findings: deve estar = 0 (Critical/High)
4. Success Rate: deve estar > 95%
5. MTTR (Mean Time To Recovery): < 10 min
```

### Criar Dashboard (Manual)

1. GitHub → Project → Add item type: "Workflow Metrics"
2. Configure automação para atualizar baseado em CI runs
3. Plotar gráficos de tendência

---

## 🔄 Fluxo de Desenvolvimento Diário

### Develop Localmente

```bash
# 1. Criar branch
git checkout -b feature/algo-novo

# 2. Fazer alterações
nano backend/app/api/routes.py
nano frontend/src/components/Button.jsx

# 3. Testar localmente (antes de push!)
cd backend && pytest -v  # 2-3 min
cd frontend && npm run test -- --run  # 1-2 min

# 4. Lint & Format
black backend/app
cd frontend && npm run lint
```

### Submeter PR

```bash
# 1. Push para o seu branch
git push origin feature/algo-novo

# 2. Criar PR
gh pr create --title "feat: Adicionar nova feature" \
  --body "Descrição da change"

# 3. Workflow executa automaticamente
# - Security scan (2 min)
# - Backend tests (3 min)
# - Frontend tests (2 min)
# - Container scan (1 min)
```

### Revisar Resultados

```bash
# Ver status dos workflows
gh run list --workflow 02-backend-tests.yml

# Se falhar, ver logs
gh run view <RUN_ID> --log

# Fazer push do fix
git add .
git commit -m "fix: Corrigir teste"
git push origin feature/algo-novo

# Workflow executa novamente automaticamente
```

### Merge & Deploy

```bash
# Após aprovação, merge via GitHub UI ou CLI
gh pr merge <PR_NUMBER> --squash

# Workflows de deploy são acionados automaticamente
# - Build & Push (2 min)
# - Deploy DEV (3 min)
# - Smoke tests (1 min)
```

---

## 🎓 Treinamento do Time

### Para Desenvolvedores Backend

```markdown
1. Como os testes rodam
   - pytest roda automaticamente
   - Coverage deve estar > 85%
   - Falhar = bloqueado de fazer merge

2. Como debugar falhas
   - Ver logs em GitHub Actions
   - Reproduzir localmente com `pytest -v`
   - Usar markers: `@pytest.mark.unit`

3. Como adicionar novo teste
   - Criar arquivo em tests/unit/test_nova_feature.py
   - Usar fixtures em conftest.py
   - Rodá antes de push: `pytest`
```

### Para Desenvolvedores Frontend

```markdown
1. ESLint & Prettier rodam automaticamente
   - Não passar = bloqueado
   - Rodar local: `npm run lint`
   - Formatar: `npm run format`

2. Vitest para unit tests
   - Cobertura: > 75%
   - Rodá com: `npm run test -- --coverage`
   - Watch mode: `npm run test -- --watch`

3. Build validation
   - `npm run build` não pode falhar
   - Dist folder deve ter outputs otimizados
```

### Para DevOps/SRE

```markdown
1. Entender os 6 stages
   - Security → Tests → Container → Integration → Push → Deploy

2. Monitorar métricas
   - Build time trends
   - Failure rates por stage
   - Security findings over time

3. Maintenance tasks
   - Atualizar ferramentas (Trivy, etc)
   - Revisar e atualizar rules (Gitleaks, Bandit)
   - Manter branch protection rules

4. Incident response
   - Rollback procedure via Blue-Green
   - RCA (Root Cause Analysis) template
   - Alert thresholds
```

---

## 📈 KPIs a Acompanhar

### Semana 1 (Baseline)

- Tempo total pipeline: ~15 min
- Taxa de sucesso: ~70% (ajustes iniciais)
- Coverage: ~75-80%

### Semana 2-4 (Estabilização)

- Tempo pipeline: ~12-15 min
- Taxa sucesso: >90%
- Coverage: >85%
- Zero findings críticos

### Mês 2+ (Otimização)

- Tempo pipeline: <12 min
- Taxa sucesso: >95%
- Coverage: >88%
- Zero findings críticos/altos
- MTTR: <5 min

---

## 🔗 Recursos Úteis

### Documentação Oficial

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Gitleaks Documentation](https://gitleaks.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)

### Comunidades

- [OWASP DevSecOps](https://owasp.org/www-project-devsecops-guideline/)
- [Cloud Native Computing Foundation](https://www.cncf.io/)
- [GitHub Discussions](https://github.com/orgs/community/discussions)

### Tools Úteis

```bash
# Instalar ferramenta de validação YAML
pip install yamllint
yamllint .github/workflows/*.yml

# Pre-commit hook para local validation
pip install pre-commit
# Criar .pre-commit-config.yaml
```

---

## ✅ Próximos Passos Após Implementação

### Semana 1

- [ ] Todos workflows executando com sucesso
- [ ] Coverage > 85%
- [ ] Sem security findings críticos

### Semana 2

- [ ] Branch protection rules ativadas
- [ ] Time familiarizado com CI/CD flow
- [ ] Documentação interna atualizada

### Semana 3+

- [ ] Adicionar integração com Slack
- [ ] Configurar Prometheus + Grafana
- [ ] Implementar SLOs para pipeline

---

## 📞 Suporte

**Dúvidas sobre os workflows?**
- Ver arquivo `docs/CI_CD_DEVSECOPS_CONTEXT.md`
- Consultá arquivo específico de cada workflow

**Problemas de segurança?**
- Revisar relatórios em GitHub Security tab
- Consultar OWASP guidelines

**Problemas de performance?**
- Verificar duração de cada stage
- Paralelizar jobs se possível
- Cache optimization

---

**Status:** ✅ Pronto para Implementação  
**Estimado:** 2-3 semanas até full operação  
**Support:** Documentação em `docs/CI_CD_DEVSECOPS_CONTEXT.md`
