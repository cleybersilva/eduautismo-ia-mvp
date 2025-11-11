# Pipeline de Ambientes - Dev → Staging → Production

## 🎯 Visão Geral

O pipeline segue uma progressão sequencial através de três ambientes:

```
dev → staging → production
```

## 🔄 Fluxo de Trabalho

### 1. Desenvolvimento (dev)
- **Branch**: `dev`
- **Trigger**: Push ou PR para `dev`
- **Ambiente**: Desenvolvimento local/AWS Dev
- **Backend Terraform**: Local
- **Aprovação**: Não requerida
- **Deploy**: Automático após pipeline passar

### 2. Homologação (staging)
- **Branch**: `staging`
- **Trigger**: Merge de `dev` → `staging`
- **Ambiente**: AWS Staging
- **Backend Terraform**: S3 + DynamoDB
- **Aprovação**: Não requerida
- **Deploy**: Automático após pipeline passar

### 3. Produção (main)
- **Branch**: `main`
- **Trigger**: Merge de `staging` → `main`
- **Ambiente**: AWS Production
- **Backend Terraform**: S3 + Replicação Cross-Region
- **Aprovação**: **REQUERIDA** (manual)
- **Deploy**: Manual via workflow_dispatch

## 📋 Stages do Pipeline

Cada ambiente executa os mesmos 5 stages:

1. 🔒 **Security Scan** - Verificação de segredos e vulnerabilidades
2. 🧪 **Backend Tests** - Testes unitários e integração
3. 🎨 **Frontend Tests** - Testes frontend
4. 🐳 **Container Scan** - Scan de imagens Docker
5. 🚀 **Build & Push** - Build e push para registry

## 🏷️ Tags de Imagens

As imagens Docker são tagueadas por ambiente:

```
ghcr.io/org/repo-api:dev-latest
ghcr.io/org/repo-api:staging-latest
ghcr.io/org/repo-api:production-latest
ghcr.io/org/repo-api:main-abc1234
```

## 🚀 Processo de Promoção

### Dev → Staging

```bash
# 1. Garantir que dev está estável
git checkout dev
git pull origin dev

# 2. Criar PR de dev para staging
git checkout staging
git pull origin staging
git merge dev
git push origin staging

# 3. Pipeline executa automaticamente
# 4. Após sucesso, imagem staging-latest está disponível
```

### Staging → Production

```bash
# 1. Garantir que staging está estável
git checkout staging
git pull origin staging

# 2. Criar PR de staging para main
git checkout main
git pull origin main
git merge staging
git push origin main

# 3. Pipeline executa automaticamente
# 4. Deploy manual requerido via GitHub Actions
```

## 🔐 Aprovações e Proteções

### Branch Protection Rules

**dev**:
- Require PR: ❌
- Require reviews: 0
- Require status checks: ✅

**staging**:
- Require PR: ✅
- Require reviews: 1
- Require status checks: ✅
- Require branch up-to-date: ✅

**main**:
- Require PR: ✅
- Require reviews: 2
- Require status checks: ✅
- Require branch up-to-date: ✅
- Require deployment approval: ✅

## 📊 Monitoramento por Ambiente

| Ambiente | Logs | Metrics | Alerts | Retention |
|----------|------|---------|--------|-----------|
| dev | CloudWatch | Basic | ❌ | 7 dias |
| staging | CloudWatch | Standard | ⚠️ | 30 dias |
| production | CloudWatch + Datadog | Full | ✅ | 90 dias |

## 🔄 Rollback

### Dev
```bash
git revert <commit-hash>
git push origin dev
```

### Staging
```bash
git revert <commit-hash>
git push origin staging
# Ou redeploy de tag anterior
```

### Production
```bash
# 1. Via GitHub Actions - Deploy workflow
# 2. Selecionar tag anterior
# 3. Executar deploy manual

# Ou via Git
git revert <commit-hash>
git push origin main
# Requer aprovação manual
```

## 🎯 Checklist de Deploy

### Para Staging
- [ ] Todos os testes passaram em dev
- [ ] Code review aprovado
- [ ] Documentação atualizada
- [ ] Migrations testadas

### Para Production
- [ ] Todos os testes passaram em staging
- [ ] 2+ code reviews aprovados
- [ ] Smoke tests executados em staging
- [ ] Runbook de rollback preparado
- [ ] Stakeholders notificados
- [ ] Janela de manutenção agendada (se necessário)
- [ ] Backup do estado atual realizado

## 📚 Comandos Úteis

### Ver status do pipeline
```bash
gh run list --workflow=00-orchestrator.yml --branch=dev
gh run list --workflow=00-orchestrator.yml --branch=staging
gh run list --workflow=00-orchestrator.yml --branch=main
```

### Disparar deploy manual
```bash
gh workflow run 06-deploy-environment.yml \
  -f environment=production \
  -f image_tag=main-abc1234
```

### Ver logs de deploy
```bash
gh run view <run-id> --log
```

## 🚨 Troubleshooting

### Pipeline falhou em dev
- Verificar logs do stage que falhou
- Corrigir localmente
- Push para dev novamente

### Pipeline falhou em staging
- Verificar se dev está estável
- Verificar diferenças de configuração
- Testar localmente com env vars de staging

### Pipeline falhou em production
- **NÃO** fazer push direto para main
- Corrigir em dev
- Promover através de staging
- Ou fazer hotfix branch e merge direto (emergência)

## 📚 Recursos Adicionais

- [🧪 Como Testar](./TESTING_GUIDE.md) - Guia completo de testes por ambiente
- [🌳 Estratégia de Branching](./BRANCHING_STRATEGY.md) - Fluxo de branches e PRs
- [📋 Template de PR](../../.github/PULL_REQUEST_TEMPLATE.md) - Template padrão

---

**Última atualização**: 2025-01-15
