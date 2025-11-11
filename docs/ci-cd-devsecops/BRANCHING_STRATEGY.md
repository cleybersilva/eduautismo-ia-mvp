# Estratégia de Branching e Deploy

## 🌳 Estrutura de Branches

```
main (production)
  ↑
  └── staging (homologação)
        ↑
        └── dev (desenvolvimento)
              ↑
              └── feature/* (features)
              └── bugfix/* (correções)
              └── hotfix/* (emergências)
```

## 📋 Tipos de Branches

### 1. Feature Branches (`feature/*`)
- **Propósito**: Desenvolvimento de novas funcionalidades
- **Origem**: Criada a partir de `dev`
- **Destino**: Merge para `dev`
- **Nomenclatura**: `feature/nome-da-funcionalidade`
- **Exemplos**:
  - `feature/user-authentication`
  - `feature/activity-generator`
  - `feature/student-dashboard`

### 2. Bugfix Branches (`bugfix/*`)
- **Propósito**: Correção de bugs não críticos
- **Origem**: Criada a partir de `dev`
- **Destino**: Merge para `dev`
- **Nomenclatura**: `bugfix/descricao-do-bug`
- **Exemplos**:
  - `bugfix/login-validation`
  - `bugfix/report-generation`

### 3. Hotfix Branches (`hotfix/*`)
- **Propósito**: Correções urgentes em produção
- **Origem**: Criada a partir de `main`
- **Destino**: Merge para `main`, `staging` e `dev`
- **Nomenclatura**: `hotfix/descricao-urgente`
- **Exemplos**:
  - `hotfix/security-vulnerability`
  - `hotfix/critical-api-error`

### 4. Dev Branch
- **Propósito**: Branch de integração para desenvolvimento
- **Proteção**: Requer PR + 1 aprovação
- **Deploy**: Automático para ambiente dev
- **Testes**: Pipeline completo executado

### 5. Staging Branch
- **Propósito**: Branch de homologação/QA
- **Proteção**: Requer PR + 1 aprovação + testes passando
- **Deploy**: Automático para ambiente staging
- **Testes**: Pipeline completo + smoke tests

### 6. Main Branch
- **Propósito**: Branch de produção
- **Proteção**: Requer PR + 2 aprovações + testes passando
- **Deploy**: Manual com aprovação
- **Testes**: Pipeline completo + validação manual

## 🔄 Fluxo de Trabalho

### Desenvolvimento de Feature

```bash
# 1. Criar feature branch a partir de dev
git checkout dev
git pull origin dev
git checkout -b feature/minha-funcionalidade

# 2. Desenvolver e commitar
git add .
git commit -m "feat: adiciona nova funcionalidade"

# 3. Push para remote
git push origin feature/minha-funcionalidade

# 4. Criar PR para dev
# - Pipeline de feature branch executa automaticamente
# - Aguardar aprovação
# - Merge para dev

# 5. Pipeline de dev executa
# - Deploy automático para ambiente dev
```

### Promoção Dev → Staging

```bash
# 1. Garantir que dev está estável
git checkout dev
git pull origin dev

# 2. Criar PR de dev para staging
# Via GitHub UI ou:
gh pr create --base staging --head dev \
  --title "Deploy to Staging - $(date +%Y-%m-%d)" \
  --body "Promoting stable dev to staging"

# 3. Aguardar aprovação e merge
# 4. Pipeline de staging executa
# 5. Deploy automático para ambiente staging
```

### Promoção Staging → Production

```bash
# 1. Garantir que staging está estável
git checkout staging
git pull origin staging

# 2. Criar PR de staging para main
gh pr create --base main --head staging \
  --title "Release to Production - v$(date +%Y.%m.%d)" \
  --body "Promoting tested staging to production"

# 3. Aguardar 2 aprovações e merge
# 4. Pipeline de main executa
# 5. Deploy MANUAL para produção
gh workflow run 06-deploy-environment.yml \
  -f environment=production \
  -f image_tag=main-latest
```

### Hotfix Urgente

```bash
# 1. Criar hotfix a partir de main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. Fazer correção
git add .
git commit -m "hotfix: corrige vulnerabilidade crítica"

# 3. Push e criar PR para main
git push origin hotfix/critical-fix
gh pr create --base main --head hotfix/critical-fix

# 4. Após merge em main, backport para staging e dev
git checkout staging
git merge main
git push origin staging

git checkout dev
git merge staging
git push origin dev
```

## 🔐 Proteções de Branch

### Configuração no GitHub

**Feature Branches**:
```yaml
- Require PR: ❌
- Require reviews: 0
- Require status checks: ✅
- Delete after merge: ✅
```

**Dev**:
```yaml
- Require PR: ✅
- Require reviews: 1
- Require status checks: ✅
  - security-scan
  - backend-tests
  - frontend-tests
  - container-scan
- Require branch up-to-date: ✅
- Allow force push: ❌
- Allow deletions: ❌
```

**Staging**:
```yaml
- Require PR: ✅
- Require reviews: 1
- Require status checks: ✅
  - All checks from dev
- Require branch up-to-date: ✅
- Allow force push: ❌
- Allow deletions: ❌
- Restrict pushes: Only from dev
```

**Main**:
```yaml
- Require PR: ✅
- Require reviews: 2
- Require status checks: ✅
  - All checks from staging
- Require branch up-to-date: ✅
- Allow force push: ❌
- Allow deletions: ❌
- Restrict pushes: Only from staging or hotfix/*
- Require deployment approval: ✅
```

## 📊 Pipeline por Branch

| Branch Type | Security | Tests | Container Scan | Build | Deploy |
|-------------|----------|-------|----------------|-------|--------|
| feature/* | ✅ | ✅ | ✅ | ❌ | ❌ |
| bugfix/* | ✅ | ✅ | ✅ | ❌ | ❌ |
| hotfix/* | ✅ | ✅ | ✅ | ✅ | Manual |
| dev | ✅ | ✅ | ✅ | ✅ | Auto (dev) |
| staging | ✅ | ✅ | ✅ | ✅ | Auto (staging) |
| main | ✅ | ✅ | ✅ | ✅ | Manual (prod) |

## 🎯 Checklist de PR

### Para Dev
- [ ] Feature branch CI passou
- [ ] Código revisado por 1 pessoa
- [ ] Testes unitários adicionados
- [ ] Documentação atualizada

### Para Staging
- [ ] Dev está estável (sem bugs conhecidos)
- [ ] Todas as features testadas em dev
- [ ] Migrations testadas
- [ ] Smoke tests preparados

### Para Main (Production)
- [ ] Staging testado completamente
- [ ] 2+ code reviews
- [ ] QA sign-off
- [ ] Runbook de rollback preparado
- [ ] Stakeholders notificados
- [ ] Changelog atualizado
- [ ] Release notes preparadas

## 🚨 Regras de Ouro

1. **NUNCA** commitar direto em `main`, `staging` ou `dev`
2. **SEMPRE** criar feature branch para mudanças
3. **SEMPRE** passar pelo fluxo: feature → dev → staging → main
4. **NUNCA** fazer merge de main para dev (exceto hotfix)
5. **SEMPRE** deletar feature branches após merge
6. **SEMPRE** manter branches atualizadas com base

## 📝 Convenção de Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

**Exemplos**:
```bash
feat(auth): adiciona autenticação JWT
fix(api): corrige validação de email
docs(readme): atualiza instruções de instalação
test(student): adiciona testes unitários
```

## 🔄 Comandos Úteis

### Criar feature branch
```bash
git checkout dev
git pull origin dev
git checkout -b feature/nome-feature
```

### Atualizar feature com dev
```bash
git checkout feature/nome-feature
git fetch origin
git rebase origin/dev
```

### Limpar branches locais
```bash
git fetch --prune
git branch --merged | grep -v "\*\|main\|dev\|staging" | xargs -n 1 git branch -d
```

### Ver status de branches
```bash
git branch -a
git log --oneline --graph --all --decorate
```

## 📚 Recursos Adicionais

- [🧪 Como Testar](./TESTING_GUIDE.md) - Guia completo de testes por ambiente
- [🚀 Pipeline de Ambientes](./PIPELINE_ENVIRONMENTS.md) - Fluxo dev → staging → production
- [📋 Template de PR](../../.github/PULL_REQUEST_TEMPLATE.md) - Template padrão de Pull Request

---

**Última atualização**: 2025-01-15
