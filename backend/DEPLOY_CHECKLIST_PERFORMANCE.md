# 🚀 Deploy Checklist - Performance Optimization

## 📋 Informações do Deploy

| Item | Valor |
|------|-------|
| **PR** | #XXX - perf: otimizar performance crítica |
| **Branch** | `perf/optimize-intervention-plans` |
| **Migration** | `20251124_1151_5403edb1d087_add_performance_indexes` |
| **Breaking Changes** | ❌ Nenhum |
| **Rollback Required** | ⚠️ Sim (migration down) |
| **Estimated Downtime** | 0 minutos (zero-downtime) |

---

## 🎯 Pré-Requisitos

### Antes de Começar

- [ ] PR aprovado e merged
- [ ] Branch `main` atualizada
- [ ] CI/CD passou em todas as checks
- [ ] Backup do banco de dados criado
- [ ] Acesso ao ambiente de staging/production
- [ ] Monitoramento configurado (Datadog/CloudWatch)

---

## 🧪 Fase 1: Validação em Staging

### 1.1 Deploy em Staging

- [ ] Pull da branch `main` atualizada
  ```bash
  cd /path/to/project
  git checkout main
  git pull origin main
  ```

- [ ] Ativar ambiente virtual
  ```bash
  source venv/bin/activate
  ```

- [ ] Aplicar migration
  ```bash
  export DATABASE_URL="postgresql://..."  # Staging DB
  alembic upgrade head
  ```

- [ ] Verificar migration aplicada
  ```bash
  alembic current
  # Expected: 5403edb1d087 (add_performance_indexes_intervention_plans)
  ```

### 1.2 Validar Índices

- [ ] Executar script de validação
  ```bash
  python scripts/validate_performance_indexes.py
  ```

- [ ] Verificar output esperado:
  ```
  ✅ ix_intervention_plans_status_needs_review
  ✅ ix_intervention_plans_last_reviewed_at
  ✅ ix_intervention_plans_review_frequency
  ✅ ix_intervention_plans_created_by_id
  ```

- [ ] **PostgreSQL**: Verificar índices manualmente
  ```sql
  \di intervention_plans*

  -- Verificar uso de índices
  EXPLAIN ANALYZE
  SELECT * FROM intervention_plans
  WHERE status = 'active' AND needs_review = true;
  ```

### 1.3 Restart Aplicação

- [ ] Restart do serviço (método depende do deploy)
  ```bash
  # Exemplo Docker
  docker-compose restart api

  # Exemplo Systemd
  sudo systemctl restart eduautismo-api

  # Exemplo PM2
  pm2 restart eduautismo-api
  ```

- [ ] Verificar health check
  ```bash
  curl http://staging-api.example.com/health
  # Expected: 200 OK
  ```

### 1.4 Testes Funcionais

- [ ] Testar endpoint principal
  ```bash
  curl -X GET "http://staging-api.example.com/api/v1/intervention-plans/pending-review?limit=50" \
    -H "Authorization: Bearer $TOKEN"
  ```

- [ ] Verificar resposta:
  - [ ] Status 200 OK
  - [ ] Estrutura JSON correta
  - [ ] Campos `priority`, `days_since_review` presentes
  - [ ] Contagens `high_priority`, `medium_priority`, `low_priority`

- [ ] Testar filtros
  ```bash
  # Filtro por prioridade
  curl "...pending-review?priority=high"

  # Paginação
  curl "...pending-review?skip=0&limit=10"
  curl "...pending-review?skip=10&limit=10"
  ```

### 1.5 Testes de Performance

- [ ] Medir latência do endpoint
  ```bash
  # Com curl
  time curl "...pending-review"

  # Com Apache Bench
  ab -n 100 -c 10 "...pending-review"
  ```

- [ ] Validar métricas:
  - [ ] P50 < 500ms
  - [ ] P95 < 2s
  - [ ] P99 < 3s

- [ ] Monitorar recursos:
  - [ ] CPU < 70%
  - [ ] Memory < 80%
  - [ ] DB connections < 50%

### 1.6 Verificar Logs

- [ ] Logs de aplicação mostram logging estruturado
  ```
  INFO - Fetching pending review plans - extra: {user_id: ..., priority_filter: ...}
  INFO - Pending review plans fetched successfully - extra: {total: ..., high_priority: ...}
  ```

- [ ] Nenhum erro ou warning crítico nos logs

- [ ] Query logs mostram uso de índices (se habilitado)

---

## ✅ Fase 2: Aprovação para Produção

### 2.1 Sign-off

- [ ] **QA**: Testes funcionais passaram
- [ ] **Performance**: Métricas dentro do esperado
- [ ] **DevOps**: Infraestrutura estável
- [ ] **Product Owner**: Aprovação de negócio (se necessário)

### 2.2 Preparação

- [ ] Agendar janela de deploy (se necessário)
- [ ] Notificar stakeholders
- [ ] Confirmar equipe de suporte disponível
- [ ] Backup final do banco de produção

---

## 🚀 Fase 3: Deploy em Produção

### 3.1 Pre-Deploy

- [ ] Confirmar backup criado
  ```bash
  # PostgreSQL
  pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_pre_deploy_$(date +%Y%m%d_%H%M%S).sql

  # Ou via RDS snapshot (AWS)
  aws rds create-db-snapshot \
    --db-instance-identifier eduautismo-prod \
    --db-snapshot-identifier pre-perf-optimization-$(date +%Y%m%d)
  ```

- [ ] Confirmar rollback plan pronto

### 3.2 Deploy

- [ ] Pull da main em produção
  ```bash
  cd /path/to/production
  git fetch origin
  git checkout main
  git pull origin main
  ```

- [ ] Aplicar migration
  ```bash
  export DATABASE_URL="postgresql://..." # Production DB
  alembic upgrade head
  ```

- [ ] **CRÍTICO**: Verificar migration aplicada sem erros
  ```bash
  alembic current
  # Expected: 5403edb1d087
  ```

- [ ] Validar índices criados
  ```bash
  python scripts/validate_performance_indexes.py
  ```

### 3.3 Restart Aplicação

- [ ] Método depende da infraestrutura:

  **Docker/ECS**:
  ```bash
  # Force new deployment
  aws ecs update-service \
    --cluster eduautismo-prod \
    --service eduautismo-api \
    --force-new-deployment
  ```

  **Kubernetes**:
  ```bash
  kubectl rollout restart deployment/eduautismo-api -n production
  kubectl rollout status deployment/eduautismo-api -n production
  ```

  **Traditional**:
  ```bash
  sudo systemctl restart eduautismo-api
  sudo systemctl status eduautismo-api
  ```

### 3.4 Smoke Tests

- [ ] Health check
  ```bash
  curl https://api.eduautismo.com/health
  # Expected: 200 OK
  ```

- [ ] Test endpoint principal
  ```bash
  curl "https://api.eduautismo.com/api/v1/intervention-plans/pending-review" \
    -H "Authorization: Bearer $PROD_TOKEN"
  ```

- [ ] Verificar resposta correta (status 200, JSON válido)

---

## 📊 Fase 4: Monitoramento Pós-Deploy

### 4.1 Primeiros 5 Minutos

- [ ] Monitorar dashboard em tempo real
- [ ] CPU usage normal (< 70%)
- [ ] Memory usage normal (< 80%)
- [ ] Error rate < 1%
- [ ] Response time P95 < 2s

### 4.2 Primeira Hora

- [ ] Monitorar métricas:
  - [ ] Taxa de erro
  - [ ] Latência (P50, P95, P99)
  - [ ] Throughput
  - [ ] DB connections
  - [ ] Query performance

- [ ] Verificar logs:
  - [ ] Nenhum erro crítico
  - [ ] Logging estruturado funcionando
  - [ ] Queries usando índices

- [ ] Alertas:
  - [ ] Nenhum alerta crítico disparado
  - [ ] Monitoramento ativo

### 4.3 Primeira 24 Horas

- [ ] Comparar métricas antes/depois:
  ```
  Métrica              | Antes  | Depois | Melhoria
  ---------------------|--------|--------|----------
  Latência P95         | 3.2s   | 0.8s   | 75%
  Queries por request  | 103    | 3      | 97%
  CPU usage (avg)      | 65%    | 35%    | 46%
  Memory usage (avg)   | 78%    | 42%    | 46%
  ```

- [ ] Feedback de usuários (se aplicável)
- [ ] Nenhuma regressão funcional reportada

---

## 🔄 Rollback Plan

### Se Algo Der Errado

#### Opção 1: Rollback da Migration

```bash
# Downgrade migration
alembic downgrade -1

# Restart app
sudo systemctl restart eduautismo-api

# Verificar
alembic current
```

#### Opção 2: Rollback Completo

```bash
# Revert código
git revert HEAD

# Rebuild e deploy
docker build -t eduautismo-api:rollback .
docker-compose up -d --force-recreate

# Ou fazer deploy da versão anterior
```

#### Opção 3: Restaurar Backup

```bash
# PostgreSQL
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup_pre_deploy.sql

# Ou restaurar RDS snapshot (AWS)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier eduautismo-prod-restored \
  --db-snapshot-identifier pre-perf-optimization-20251124
```

### Quando Fazer Rollback

Fazer rollback imediatamente se:
- [ ] Error rate > 5%
- [ ] P95 latency > 5s (pior que antes)
- [ ] CPU ou Memory > 90%
- [ ] Erros críticos nos logs
- [ ] Funcionalidade quebrada

---

## 📝 Pós-Deploy

### Documentação

- [ ] Atualizar CHANGELOG
- [ ] Atualizar documentação técnica
- [ ] Documentar lições aprendidas
- [ ] Fechar issue/ticket relacionado

### Comunicação

- [ ] Notificar stakeholders do sucesso
- [ ] Postar em canal de deploy (#deploys)
- [ ] Atualizar status page (se aplicável)

### Configuração de Alertas

- [ ] Configurar alerta: Latência P95 > 2s
- [ ] Configurar alerta: Error rate > 2%
- [ ] Configurar alerta: DB slow queries (> 1s)
- [ ] Configurar alerta: Memory usage > 85%

---

## ✅ Sign-Off Final

**Deploy concluído por**: _______________
**Data/Hora**: _______________
**Status**: ✅ Sucesso / ⚠️ Com avisos / ❌ Rollback

**Notas**:
```
[Espaço para notas adicionais]
```

---

## 📚 Referências

- **PR**: https://github.com/cleybersilva/eduautismo-ia-mvp/pull/XXX
- **Migration**: `alembic/versions/20251124_1151_5403edb1d087_*`
- **Documentação**: `PENDING_REVIEW_ENDPOINT.md`
- **Changelog**: `CHANGELOG_PENDING_REVIEW.md`
- **Monitoramento**: [Link para dashboard]

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
