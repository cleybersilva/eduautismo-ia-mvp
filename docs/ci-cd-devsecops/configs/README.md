# ⚙️ Configurações - CI/CD DevSecOps

Arquivos de configuração para ferramentas de segurança, testes e análise estática.

---

## 📁 Arquivos de Configuração

### 🔐 Segurança

#### `.gitleaks.toml`
**Objetivo:** Detectar secrets (tokens, chaves API, credenciais) no repositório

**O que detecta:**
- Chaves AWS (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- Tokens OpenAI
- JWT tokens
- URLs de banco de dados
- Chaves privadas
- Tokens GitHub, GitLab, Bitbucket
- Credenciais Twilio, SendGrid, etc.

**Como usar:**
```bash
# Scanning local
gitleaks detect --source . --verbose

# Pre-commit check
gitleaks detect --source . --exit-code 1

# CI/CD (GitHub Actions)
# Executado automaticamente em: 01-security-scan.yml
```

**Saiba mais:** [GitHub Gitleaks](https://github.com/gitleaks/gitleaks)

---

#### `codecov.yml`
**Objetivo:** Configurar thresholds de cobertura e reporting no Codecov

**Configurações principais:**
- Coverage target: 85% backend, 75% frontend
- Require coverage increase em PRs
- Falha se cair abaixo dos limites
- Integration com GitHub Reviews

**Como usar:**
```bash
# Enviar cobertura
codecov --file coverage.xml

# Verificar status
curl https://codecov.io/api/v2/repos/{owner}/{repo}/coverage
```

**Saiba mais:** [Codecov Documentation](https://docs.codecov.io)

---

### 🧪 Testes

#### `pytest.ini` (cópia)
**Localização original:** `backend/pytest.ini`

**Configurações principais:**
- Test discovery patterns
- Coverage mínima: 85%
- Test timeout: 30 segundos
- Markers customizados (unit, integration, e2e)
- Report format: xml, json, html

**Como usar:**
```bash
# Rodar testes com config
pytest

# Com cobertura
pytest --cov=app --cov-report=xml

# Relatório HTML
pytest --cov=app --cov-report=html
```

**Saiba mais:** [Pytest Documentation](https://docs.pytest.org)

---

#### `.bandit` (para documentação)
**Objetivo:** SAST (Static Application Security Testing) para Python

**O que testa:**
- SQL Injection
- Hardcoded passwords
- Insecure cryptography
- Insecure random generation
- TLS/SSL configuration
- Parameterized SQL queries

**Padrão de uso:**
```bash
# Rodar análise
bandit -r app/ -f json -o bandit-report.json

# Com exclusões
bandit -r app/ --skip B101,B601
```

**Recomendação:** Manter configuração no backend/ (já aplicado em workflows)

---

## 🔗 Integração com Workflows

### Stage 1: Security Scan
```
01-security-scan.yml
├── Gitleaks (secrets detection) → usa .gitleaks.toml
├── Bandit (SAST Python)
├── Safety (dependency scanning)
└── License compliance
```

### Stage 2: Backend Tests
```
02-backend-tests.yml
├── Pytest (unit/integration) → usa pytest.ini
├── Coverage report → usa codecov.yml
└── Linting + formatting
```

### Stage 3: Frontend Tests
```
03-frontend-tests.yml
├── Vitest (unit/component tests)
├── ESLint + Prettier
└── Build validation
```

---

## 📊 Métricas e Limites

| Métrica | Backend | Frontend | CI Fail |
|---------|---------|----------|---------|
| **Coverage** | 85% | 75% | Sim |
| **Security (Critical)** | 0 | 0 | Sim |
| **Security (High)** | 0 | 0 | Sim |
| **Lint Errors** | 0 | 0 | Sim |
| **Build Status** | Sucesso | Sucesso | Sim |

---

## 🚀 Como Usar Estas Configurações

### Primeira Vez (Setup)
1. Copie `codecov.yml` para raiz do repositório
2. Mova `.gitleaks.toml` para raiz (para pre-commit)
3. Mantenha `pytest.ini` em `backend/`
4. Push dos workflows em `.github/workflows/`

### Desenvolvimento Local
```bash
# Backend
cd backend
pytest --cov=app  # Usa pytest.ini automaticamente

# Verificar secrets antes de commit
gitleaks detect --source . --verbose

# SAST Python
bandit -r app/
```

### CI/CD Pipeline
Todas as configurações são usadas automaticamente nos workflows:
- `01-security-scan.yml` → Gitleaks, Bandit
- `02-backend-tests.yml` → Pytest, Codecov
- `03-frontend-tests.yml` → Vitest, ESLint
- `04-container-scan.yml` → Trivy

---

## ✅ Validação

### Checklist de Implementação

- [ ] `.gitleaks.toml` em raiz do repositório
- [ ] `codecov.yml` em raiz do repositório
- [ ] `pytest.ini` em `backend/`
- [ ] Workflows em `.github/workflows/01-05`
- [ ] Pre-commit hook configurado (opcional)
- [ ] Codecov token em GitHub Secrets
- [ ] GitLeaks token em GitHub Secrets (opcional)

### Testar Configurações

```bash
# Testar Gitleaks
cd /mnt/d/ENGINEER/VS_Code/eduautismo-ia-mvp
gitleaks detect --config docs/ci-cd-devsecops/configs/.gitleaks.toml

# Testar Pytest
cd backend
pytest -v --collect-only

# Testar Bandit
bandit -r app/ --ini docs/ci-cd-devsecops/configs/.bandit
```

---

## 📚 Documentação Relacionada

Veja também:
- `02-IMPLEMENTATION_GUIDE.md` - Guia completo de implementação
- `01-DEVSECOPS_SUMMARY.md` - Resumo das ferramentas
- `03-README.md` - Referência rápida

---

## 🔄 Manutenção

### Atualizações Recomendadas

**Trimestral:**
- Revisar limites de coverage (ajustar conforme crescimento)
- Avaliar novas regras de segurança
- Testar exclusões do Gitleaks

**Semestral:**
- Atualizar versões das ferramentas
- Revisar relatórios de segurança
- Otimizar performance do pipeline

---

## 📞 Suporte

Para dúvidas sobre configurações específicas:
1. Consulte `02-IMPLEMENTATION_GUIDE.md`
2. Veja documentação oficial das ferramentas
3. Procure erros no `WORKFLOW_ORDER_VERIFICATION.md`

---

**Versão:** 1.0  
**Atualizado:** 11 de novembro de 2025
