# 🚀 Deploy Guide - Campo needs_review

**Versão:** 1.0
**Data de Criação:** 2025-11-23
**Autor:** Sistema EduAutismo IA
**Migration ID:** `zxo9rq852lkg`

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Checklist Pré-Deploy](#checklist-pré-deploy)
4. [Deploy em Staging](#deploy-em-staging)
5. [Validação em Staging](#validação-em-staging)
6. [Deploy em Produção](#deploy-em-produção)
7. [Validação em Produção](#validação-em-produção)
8. [Rollback (se necessário)](#rollback-se-necessário)
9. [Monitoramento Pós-Deploy](#monitoramento-pós-deploy)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### O que será deployado?

1. **Migration de Database**
   - Adicionar campo `needs_review` à tabela `intervention_plans`
   - Tipo: BOOLEAN NOT NULL DEFAULT false
   - Zero downtime (campo tem default)

2. **Código da Aplicação**
   - Métodos de cálculo no modelo ORM
   - Atualização automática no service
   - Testes validando funcionalidade

3. **Scripts de Manutenção**
   - Script de recálculo em batch
   - Script de relatório de saúde

### Impacto Esperado

- ✅ **Downtime:** ZERO (migration DDL com default é instantâneo)
- ✅ **Breaking Changes:** NENHUM (100% backwards compatible)
- ✅ **Performance:** Impacto mínimo (campo Boolean simples)
- ✅ **Rollback:** Possível e seguro

### Timeline Estimada

| Ambiente | Tempo Estimado | Observações |
|----------|----------------|-------------|
| Staging  | 15-30 minutos  | Inclui testes de validação |
| Produção | 30-45 minutos  | Inclui monitoramento inicial |

---

## ✅ Pré-requisitos

### Antes de Começar

- [ ] **Acesso aos ambientes** - SSH/kubectl para staging e produção
- [ ] **Credenciais de banco** - Usuário com permissões DDL (ALTER TABLE)
- [ ] **Backup verificado** - Backup recente e testado
- [ ] **Janela de manutenção** - Se aplicável (recomendado mas não obrigatório)
- [ ] **Time de plantão** - Pelo menos 2 pessoas disponíveis
- [ ] **Rollback plan** - Procedimento de rollback revisado

### Ferramentas Necessárias

```bash
# Verificar instalação
python --version    # >= 3.11
alembic --version   # >= 1.12
psql --version      # Para PostgreSQL
git --version       # Para verificar commits
```

### Variáveis de Ambiente

```bash
# Staging
export DATABASE_URL="postgresql://user:pass@staging-db:5432/eduautismo"
export ENVIRONMENT="staging"

# Produção
export DATABASE_URL="postgresql://user:pass@prod-db:5432/eduautismo"
export ENVIRONMENT="production"
```

---

## 📝 Checklist Pré-Deploy

### Verificações Obrigatórias

```bash
# 1. Verificar branch correta
git status
git log --oneline -10

# Commits necessários:
# - e6c1f3e: feat: implementar lógica de cálculo automático de needs_review
# - 1fee21b: feat: adicionar migration para campo needs_review
```

**Checklist:**

- [ ] Branch `main` atualizada localmente
- [ ] Todos os commits necessários presentes
- [ ] Tests passando em CI/CD (366/366)
- [ ] Coverage acima de 60% (atual: 80.34%)
- [ ] Code review aprovado
- [ ] Documentação atualizada

### Backup do Banco de Dados

#### PostgreSQL

```bash
# Staging
pg_dump -h staging-db-host \
        -U eduautismo_user \
        -d eduautismo_staging \
        -F c \
        -f backup_staging_$(date +%Y%m%d_%H%M%S).dump

# Produção
pg_dump -h prod-db-host \
        -U eduautismo_user \
        -d eduautismo_production \
        -F c \
        -f backup_production_$(date +%Y%m%d_%H%M%S).dump

# Verificar backup
pg_restore --list backup_*.dump | head -20
```

#### SQLite (desenvolvimento)

```bash
cp eduautismo.db eduautismo_backup_$(date +%Y%m%d_%H%M%S).db
```

**Checklist de Backup:**

- [ ] Backup criado com sucesso
- [ ] Backup verificado (arquivo não corrompido)
- [ ] Backup armazenado em local seguro
- [ ] Tamanho do backup verificado (não vazio)
- [ ] Permissões do backup verificadas

---

## 🧪 Deploy em Staging

### Passo 1: Conectar ao Ambiente

```bash
# Exemplo: SSH
ssh usuario@staging-server

# Ou: Kubectl (Kubernetes)
kubectl config use-context staging
kubectl exec -it deployment/eduautismo-api -- /bin/bash

# Ou: Docker
docker exec -it eduautismo-api-staging /bin/bash
```

### Passo 2: Atualizar Código

```bash
# Navegar para diretório
cd /app/eduautismo-ia-mvp/backend

# Pull das mudanças
git fetch origin
git checkout main
git pull origin main

# Verificar commits
git log --oneline -5
# Deve mostrar: e6c1f3e, 1fee21b, etc.

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### Passo 3: Verificar Migration

```bash
# Verificar status atual
alembic current

# Output esperado:
# 0a32abc79858 (head)

# Ver histórico de migrations
alembic history

# Output esperado deve incluir:
# zxo9rq852lkg -> 0a32abc79858 (head), add needs_review field
```

### Passo 4: Aplicar Migration

```bash
# DRY RUN (preview do SQL)
alembic upgrade head --sql > migration_sql_preview.sql
cat migration_sql_preview.sql

# SQL esperado:
# ALTER TABLE intervention_plans
# ADD COLUMN needs_review BOOLEAN NOT NULL DEFAULT false;

# Aplicar migration
echo "Aplicando migration em $(date)"
alembic upgrade head

# Output esperado:
# INFO  [alembic.runtime.migration] Running upgrade 0a32abc79858 -> zxo9rq852lkg, add needs_review field to intervention_plans
```

### Passo 5: Verificar Migration Aplicada

```bash
# Verificar versão atual
alembic current -v

# Output esperado:
# zxo9rq852lkg (head)

# Verificar estrutura da tabela (PostgreSQL)
psql $DATABASE_URL -c "\d intervention_plans" | grep needs_review

# Output esperado:
# needs_review | boolean | not null | false
```

### Passo 6: Recalcular needs_review

```bash
# Preview (sem aplicar)
python scripts/recalculate_needs_review.py --dry-run

# Aplicar recálculo
python scripts/recalculate_needs_review.py

# Verificar resultado
python scripts/intervention_plans_health_check.py
```

### Passo 7: Reiniciar Aplicação

```bash
# Kubernetes
kubectl rollout restart deployment/eduautismo-api

# Aguardar pods ficarem ready
kubectl rollout status deployment/eduautismo-api

# Docker Compose
docker-compose restart api

# Systemd
sudo systemctl restart eduautismo-api
```

---

## ✓ Validação em Staging

### Teste 1: Health Check da API

```bash
# Verificar API está respondendo
curl -f https://api-staging.eduautismo.com/health || echo "FALHOU"

# Output esperado:
# {"status":"healthy","version":"..."}
```

### Teste 2: Verificar Campo no Banco

```bash
# SQL de validação
psql $DATABASE_URL -c "
SELECT
    COUNT(*) as total_planos,
    SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as precisam_revisao,
    SUM(CASE WHEN NOT needs_review THEN 1 ELSE 0 END) as nao_precisam
FROM intervention_plans
WHERE is_active = true;
"

# Output esperado (exemplo):
#  total_planos | precisam_revisao | nao_precisam
# --------------+------------------+--------------
#            50 |               12 |           38
```

### Teste 3: Endpoint GET /intervention-plans

```bash
# Buscar plano específico
PLAN_ID="algum-uuid-valido"
curl -H "Authorization: Bearer $TOKEN" \
     https://api-staging.eduautismo.com/api/v1/intervention-plans/$PLAN_ID

# Verificar que resposta inclui needs_review
# Exemplo output:
# {
#   "id": "...",
#   "title": "...",
#   "needs_review": true,  # <-- Campo deve estar presente
#   ...
# }
```

### Teste 4: Filtro needs_review

```bash
# Listar planos que precisam revisão
curl -H "Authorization: Bearer $TOKEN" \
     "https://api-staging.eduautismo.com/api/v1/intervention-plans?needs_review=true"

# Verificar que retorna apenas planos com needs_review=true
```

### Teste 5: Executar Suite de Testes

```bash
# Rodar testes de integração
pytest tests/integration/test_intervention_plans_api.py -v

# Output esperado:
# 14 passed

# Rodar testes unitários de needs_review
pytest tests/unit/test_needs_review_logic.py -v

# Output esperado:
# 9 passed
```

### Checklist de Validação Staging

- [ ] API responde ao /health
- [ ] Campo `needs_review` existe no banco
- [ ] Planos retornam campo `needs_review` na API
- [ ] Filtro `needs_review=true` funciona
- [ ] Testes de integração passam (14/14)
- [ ] Testes unitários passam (9/9)
- [ ] Logs sem erros críticos
- [ ] Performance aceitável (latência normal)

**Se todos os checks passaram:** ✅ Prosseguir para produção
**Se algum check falhou:** ❌ Investigar e corrigir antes de produção

---

## 🚀 Deploy em Produção

### ⚠️ ATENÇÃO - Checklist Final Antes de Produção

- [ ] **Staging 100% validado** - Todos os testes passaram
- [ ] **Backup de produção verificado** - Backup recente e testado
- [ ] **Time de plantão disponível** - Pelo menos 2 pessoas
- [ ] **Horário adequado** - Preferencialmente fora do horário de pico
- [ ] **Comunicação enviada** - Stakeholders notificados
- [ ] **Rollback plan revisado** - Procedimento testado em staging

### Passo 1: Preparação

```bash
# 1. Conectar ao ambiente de produção
ssh usuario@prod-server
# ou
kubectl config use-context production

# 2. Criar marcador no monitoramento
curl -X POST https://monitoring.eduautismo.com/api/markers \
  -d '{"text":"Deploy needs_review iniciado","tags":["deploy","production"]}'

# 3. Verificar status atual
cd /app/eduautismo-ia-mvp/backend
git status
alembic current
```

### Passo 2: Backup Final

```bash
# Backup de produção
echo "Iniciando backup de produção em $(date)"
pg_dump -h prod-db-host \
        -U eduautismo_user \
        -d eduautismo_production \
        -F c \
        -f backup_prod_pre_needs_review_$(date +%Y%m%d_%H%M%S).dump

# Verificar backup
ls -lh backup_prod_*.dump
pg_restore --list backup_prod_*.dump | head -10

echo "Backup concluído em $(date)"
```

### Passo 3: Atualizar Código

```bash
# Pull das mudanças
git fetch origin
git checkout main
git pull origin main

# Verificar commits críticos
git log --oneline -10 | grep -E "(e6c1f3e|1fee21b)"

# Instalar dependências
pip install -r requirements.txt
```

### Passo 4: Aplicar Migration

```bash
# Preview do SQL (IMPORTANTE!)
alembic upgrade head --sql

# Verificar SQL gerado
# Deve ser: ALTER TABLE intervention_plans ADD COLUMN needs_review BOOLEAN NOT NULL DEFAULT false;

# Aplicar migration
echo "=== APLICANDO MIGRATION EM PRODUÇÃO ==="
echo "Início: $(date)"
time alembic upgrade head
echo "Fim: $(date)"

# Verificar sucesso
alembic current -v
# Deve mostrar: zxo9rq852lkg (head)
```

### Passo 5: Validar Estrutura

```bash
# Verificar campo criado
psql $DATABASE_URL -c "
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'intervention_plans'
AND column_name = 'needs_review';
"

# Output esperado:
# column_name  | data_type | is_nullable | column_default
# -------------+-----------+-------------+----------------
# needs_review | boolean   | NO          | false
```

### Passo 6: Recalcular needs_review

```bash
# IMPORTANTE: Primeiro fazer dry-run
python scripts/recalculate_needs_review.py --dry-run | tee recalculate_dry_run.log

# Revisar log
less recalculate_dry_run.log

# Se tudo OK, aplicar
python scripts/recalculate_needs_review.py | tee recalculate_prod.log

# Salvar log
cp recalculate_prod.log /var/log/eduautismo/
```

### Passo 7: Deploy da Aplicação

#### Kubernetes (Zero Downtime)

```bash
# Atualizar deployment
kubectl set image deployment/eduautismo-api \
  api=eduautismo-api:latest

# Aguardar rollout
kubectl rollout status deployment/eduautismo-api

# Verificar pods
kubectl get pods -l app=eduautismo-api
```

#### Docker Compose

```bash
# Rebuild e restart
docker-compose build api
docker-compose up -d api

# Verificar logs
docker-compose logs -f api
```

#### Tradicional (Systemd)

```bash
# Restart serviço
sudo systemctl restart eduautismo-api

# Verificar status
sudo systemctl status eduautismo-api

# Ver logs
sudo journalctl -u eduautismo-api -f
```

---

## ✓ Validação em Produção

### Validação Rápida (Primeiros 5 minutos)

```bash
# 1. Health check
curl -f https://api.eduautismo.com/health

# 2. Verificar logs por erros
kubectl logs -l app=eduautismo-api --tail=100 | grep -i error
# Ou: tail -100 /var/log/eduautismo/api.log | grep -i error

# 3. Teste de endpoint
curl -H "Authorization: Bearer $PROD_TOKEN" \
     https://api.eduautismo.com/api/v1/intervention-plans?limit=1
```

### Validação Completa (Primeiros 15 minutos)

```bash
# 1. Relatório de saúde
python scripts/intervention_plans_health_check.py > health_check_prod.txt
cat health_check_prod.txt

# 2. Query de validação
psql $DATABASE_URL -c "
SELECT
    status,
    COUNT(*) as total,
    SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as precisam_revisao
FROM intervention_plans
GROUP BY status
ORDER BY status;
"

# 3. Teste de filtro
curl -H "Authorization: Bearer $PROD_TOKEN" \
     "https://api.eduautismo.com/api/v1/intervention-plans?needs_review=true&limit=5"

# 4. Métricas de performance
# Verificar latência no Datadog/New Relic/etc
```

### Monitoramento Contínuo (Próximas 24h)

```bash
# Configurar alertas para:
- [ ] Latência P95 do endpoint GET /intervention-plans
- [ ] Taxa de erro 5xx
- [ ] Uso de CPU/memória dos pods
- [ ] Latência de queries ao banco (campo needs_review)
```

### Checklist Final de Validação Produção

- [ ] Health check respondendo (< 200ms)
- [ ] Campo `needs_review` existe e está populado
- [ ] API retornando campo corretamente
- [ ] Filtro `needs_review` funcionando
- [ ] Sem erros nos logs (últimos 100 linhas)
- [ ] Latência P95 normal (< 2s)
- [ ] Uso de recursos normal (CPU/RAM)
- [ ] Alertas de monitoramento OK

**Se todos os checks passaram:** ✅ **DEPLOY BEM-SUCEDIDO!**
**Se algum check crítico falhou:** ❌ **Executar ROLLBACK imediatamente**

---

## 🔙 Rollback (se necessário)

### Quando fazer Rollback?

- ❌ Taxa de erro > 5% em endpoints de intervention_plans
- ❌ Latência P95 > 5 segundos
- ❌ Erros críticos nos logs relacionados a needs_review
- ❌ Campo causando comportamento inesperado

### Procedimento de Rollback

#### 1. Rollback da Aplicação (RÁPIDO - 2 minutos)

```bash
# Kubernetes - voltar para versão anterior
kubectl rollout undo deployment/eduautismo-api

# Verificar rollout
kubectl rollout status deployment/eduautismo-api

# Docker Compose
docker-compose down
git checkout <commit-anterior>
docker-compose up -d

# Systemd
git checkout <commit-anterior>
pip install -r requirements.txt
sudo systemctl restart eduautismo-api
```

#### 2. Rollback da Migration (se necessário - 5 minutos)

```bash
# ATENÇÃO: Só fazer se necessário! Campo tem default, não quebra nada.

# Verificar versão atual
alembic current

# Downgrade (remove coluna)
alembic downgrade -1

# Verificar
alembic current
# Deve mostrar: 0a32abc79858

# Verificar que coluna foi removida
psql $DATABASE_URL -c "\d intervention_plans" | grep needs_review
# Não deve retornar nada
```

#### 3. Restaurar Backup (último recurso - 15-30 minutos)

```bash
# ATENÇÃO: Isso apaga dados criados após o backup!

# Parar aplicação
kubectl scale deployment/eduautismo-api --replicas=0

# Restaurar backup
pg_restore -h prod-db-host \
           -U eduautismo_user \
           -d eduautismo_production \
           -c \
           backup_prod_pre_needs_review_*.dump

# Verificar restauração
psql $DATABASE_URL -c "SELECT COUNT(*) FROM intervention_plans;"

# Reiniciar aplicação
kubectl scale deployment/eduautismo-api --replicas=3
```

### Pós-Rollback

```bash
# 1. Verificar health
curl https://api.eduautismo.com/health

# 2. Notificar time
echo "Rollback executado em $(date)" | slack-notify

# 3. Criar post-mortem
# Documentar:
# - O que causou o problema
# - Como foi detectado
# - Ações tomadas
# - Lições aprendidas
```

---

## 📊 Monitoramento Pós-Deploy

### Métricas para Monitorar (Primeiras 24h)

#### Performance

```sql
-- Query para medir impacto do campo
EXPLAIN ANALYZE
SELECT * FROM intervention_plans
WHERE needs_review = true
LIMIT 100;

-- Deve ser rápido (< 50ms para 100 registros)
```

#### Queries úteis

```sql
-- 1. Distribuição de needs_review
SELECT
    needs_review,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM intervention_plans
WHERE status = 'active'
GROUP BY needs_review;

-- 2. Planos ativos que precisam revisão
SELECT
    title,
    review_frequency,
    last_reviewed_at,
    DATE_PART('day', CURRENT_DATE - last_reviewed_at) as days_since_review
FROM intervention_plans
WHERE needs_review = true
AND status = 'active'
ORDER BY days_since_review DESC
LIMIT 20;

-- 3. Estatísticas por frequência de revisão
SELECT
    review_frequency,
    COUNT(*) as total,
    SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as precisam_revisao
FROM intervention_plans
WHERE status = 'active'
GROUP BY review_frequency
ORDER BY review_frequency;
```

### Dashboards Recomendados

1. **Performance Dashboard**
   - Latência P50/P95/P99 do endpoint GET /intervention-plans
   - Taxa de erro dos endpoints
   - Queries lentas envolvendo needs_review

2. **Business Dashboard**
   - Total de planos ativos
   - % de planos que precisam revisão
   - Distribuição por frequência de revisão
   - Tendência de needs_review ao longo do tempo

3. **Health Dashboard**
   - Planos nunca revisados
   - Planos atrasados (end_date passou)
   - Planos terminando em breve
   - Score de saúde geral

---

## 🔧 Troubleshooting

### Problema 1: Migration falha com "column already exists"

**Sintoma:**
```
alembic.runtime.migration.CommandError: Column "needs_review" already exists
```

**Causa:** Migration já foi aplicada anteriormente

**Solução:**
```bash
# Verificar versão atual
alembic current

# Se já mostra zxo9rq852lkg, migration já foi aplicada
# Marcar como aplicada manualmente
alembic stamp head

# Ou pular para próxima migration
alembic upgrade head
```

### Problema 2: Campo não aparece na API

**Sintoma:** API retorna planos sem campo `needs_review`

**Diagnóstico:**
```bash
# 1. Verificar campo no banco
psql $DATABASE_URL -c "SELECT needs_review FROM intervention_plans LIMIT 1;"

# 2. Verificar código deployado
git log -1 --oneline
# Deve incluir commit e6c1f3e

# 3. Verificar schema Pydantic
grep -n "needs_review" app/schemas/intervention_plan.py
```

**Solução:**
```bash
# Atualizar código se necessário
git pull origin main
pip install -r requirements.txt

# Reiniciar aplicação
sudo systemctl restart eduautismo-api
# ou
kubectl rollout restart deployment/eduautismo-api
```

### Problema 3: Performance degradada

**Sintoma:** Queries lentas após migration

**Diagnóstico:**
```sql
-- Verificar queries lentas
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
WHERE query LIKE '%needs_review%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solução:**
```sql
-- Criar índice parcial (apenas se necessário)
CREATE INDEX CONCURRENTLY idx_intervention_plans_needs_review
ON intervention_plans(needs_review)
WHERE needs_review = true;
```

### Problema 4: needs_review sempre false

**Sintoma:** Todos os planos têm `needs_review = false`

**Causa:** Recálculo não foi executado após migration

**Solução:**
```bash
# Executar recálculo
python scripts/recalculate_needs_review.py

# Verificar resultado
python scripts/intervention_plans_health_check.py
```

---

## 📞 Contatos de Emergência

### Time de Desenvolvimento

- **Tech Lead:** tech-lead@eduautismo.com
- **DevOps:** devops@eduautismo.com
- **Slack:** #eduautismo-incidents

### Procedimento de Escalação

1. **Nível 1 (0-15 min):** Dev que fez deploy investiga
2. **Nível 2 (15-30 min):** Tech Lead é notificado
3. **Nível 3 (30+ min):** Executar rollback imediato

---

## ✅ Checklist Final de Deploy

### Pré-Deploy

- [ ] Backup verificado
- [ ] Tests passando
- [ ] Code review aprovado
- [ ] Documentação atualizada
- [ ] Time de plantão disponível

### Deploy Staging

- [ ] Migration aplicada
- [ ] Código atualizado
- [ ] Testes de validação passaram
- [ ] Monitoramento OK por 24h

### Deploy Produção

- [ ] Backup final criado
- [ ] Migration aplicada
- [ ] Código deployado
- [ ] Recálculo executado
- [ ] Validações passaram
- [ ] Monitoramento configurado

### Pós-Deploy

- [ ] Health checks passando
- [ ] Performance normal
- [ ] Sem erros nos logs
- [ ] Alertas OK
- [ ] Documentação atualizada
- [ ] Post-mortem (se necessário)

---

**Última atualização:** 2025-11-23
**Próxima revisão:** Após deploy em produção
**Mantenedor:** Equipe EduAutismo IA

---

## 📚 Referências

- [Migration Notes](alembic/versions/MIGRATION_NOTES.md)
- [Sessão de Desenvolvimento](SESSAO_20251123.md)
- [Scripts README](scripts/README.md)
- [Documentação da API](../docs/API.md)

---

**BOA SORTE COM O DEPLOY! 🚀**
