# 🚀 Checklist de Deploy - Otimizações de Performance

**Branch**: `perf/optimize-intervention-plans`
**Commit**: `55bc01d`
**Data de Criação**: 2025-11-24
**Responsável**: Time de Backend

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Fase 1: Validação em Staging](#fase-1-validação-em-staging)
3. [Fase 2: Aprovação para Produção](#fase-2-aprovação-para-produção)
4. [Fase 3: Deploy em Produção](#fase-3-deploy-em-produção)
5. [Fase 4: Monitoramento Pós-Deploy](#fase-4-monitoramento-pós-deploy)
6. [Rollback Plan](#rollback-plan)

---

## Pré-requisitos

### Ambiente de Desenvolvimento

- [ ] Branch `perf/optimize-intervention-plans` merged para `main`
- [ ] Todos os testes passando (98.4% ou superior)
- [ ] Code review aprovado
- [ ] PR aprovado e merged

### Ambiente de Staging

- [ ] Staging atualizado com código da `main`
- [ ] Banco de dados staging com dados de teste (mínimo 1000 planos)
- [ ] Credenciais de acesso configuradas

### Ferramentas

- [ ] Acesso ao AWS Console
- [ ] Acesso ao Datadog/CloudWatch
- [ ] Scripts de validação baixados:
  - `scripts/validate_performance_indexes.py`
  - `scripts/load_test_pending_review.py`
- [ ] Cliente PostgreSQL (psql ou DBeaver)

---

## Fase 1: Validação em Staging

### 1.1 Deploy em Staging

```bash
# 1. Fazer backup do banco staging
pg_dump -h staging-db.example.com -U user -d eduautismo_staging > backup_staging_$(date +%Y%m%d_%H%M%S).sql

# 2. Deploy da aplicação em staging
./deploy.sh staging main

# 3. Aguardar health check
curl https://api-staging.eduautismo.example.com/health
```

**Checklist**:
- [ ] Backup do banco de dados criado
- [ ] Deploy concluído sem erros
- [ ] Health check retorna 200 OK
- [ ] Logs não mostram erros críticos

### 1.2 Executar Migration

```bash
# SSH no servidor staging
ssh staging-server

# Navegar para diretório da aplicação
cd /app/backend

# Executar migration
alembic upgrade head

# Verificar migration aplicada
alembic current
# Deve mostrar: 20251124_1151_5403edb1d087 (head)
```

**Checklist**:
- [ ] Migration executada sem erros
- [ ] Versão do banco atualizada para `5403edb1d087`
- [ ] Logs de migration não mostram warnings

### 1.3 Validar Índices

```bash
# Executar script de validação
python scripts/validate_performance_indexes.py
```

**Output esperado**:
```
✓ Conectado ao banco: eduautismo_staging
✓ Total de índices na tabela 'intervention_plans': 8

Validando: ix_intervention_plans_status_needs_review
  ✓ Índice encontrado
  ✓ Colunas corretas: ['status', 'needs_review']

Validando: ix_intervention_plans_last_reviewed_at
  ✓ Índice encontrado
  ✓ Colunas corretas: ['last_reviewed_at']

Validando: ix_intervention_plans_review_frequency
  ✓ Índice encontrado
  ✓ Colunas corretas: ['review_frequency']

Validando: ix_intervention_plans_created_by_id
  ✓ Índice encontrado
  ✓ Colunas corretas: ['created_by_id']

✓ SUCESSO: Todos os índices foram criados corretamente!
```

**Checklist**:
- [ ] Todos os 4 índices criados corretamente
- [ ] Query plan mostra uso de índices
- [ ] Sem erros de validação

### 1.4 Testes Funcionais

```bash
# 1. Testar endpoint pending-review básico
curl -H "Authorization: Bearer $TOKEN" \
  https://api-staging.eduautismo.example.com/api/v1/intervention-plans/pending-review

# 2. Testar filtro por prioridade
curl -H "Authorization: Bearer $TOKEN" \
  "https://api-staging.eduautismo.example.com/api/v1/intervention-plans/pending-review?priority=high"

# 3. Testar paginação
curl -H "Authorization: Bearer $TOKEN" \
  "https://api-staging.eduautismo.example.com/api/v1/intervention-plans/pending-review?skip=10&limit=20"

# 4. Testar filtro por profissional
curl -H "Authorization: Bearer $TOKEN" \
  "https://api-staging.eduautismo.example.com/api/v1/intervention-plans/pending-review?professional_id=UUID"
```

**Checklist**:
- [ ] Endpoint retorna 200 OK
- [ ] Estrutura de resposta correta (items, total, counts por prioridade)
- [ ] Filtro por prioridade funciona
- [ ] Paginação funciona corretamente
- [ ] Filtro por profissional funciona
- [ ] Response time < 2s (P95)

### 1.5 Teste de Carga

```bash
# Teste básico: 100 requisições, 10 concorrentes
python scripts/load_test_pending_review.py \
  --url https://api-staging.eduautismo.example.com \
  --requests 100 \
  --concurrent 10 \
  --username test@example.com \
  --password testpass

# Teste intermediário: 500 requisições, 25 concorrentes
python scripts/load_test_pending_review.py \
  --url https://api-staging.eduautismo.example.com \
  --requests 500 \
  --concurrent 25 \
  --username test@example.com \
  --password testpass

# Teste de stress: 1000 requisições, 50 concorrentes
python scripts/load_test_pending_review.py \
  --url https://api-staging.eduautismo.example.com \
  --requests 1000 \
  --concurrent 50 \
  --username test@example.com \
  --password testpass
```

**Critérios de Sucesso**:
- [ ] Taxa de sucesso > 95%
- [ ] P95 latency < 2000ms
- [ ] P99 latency < 5000ms
- [ ] Sem timeouts
- [ ] Sem erros de memória

**Se falhar**:
- Investigar logs de erro
- Verificar uso de CPU/memória
- Revisar query performance no banco
- Considerar ajuste de recursos (scaling)

### 1.6 Validação Manual

**Testar via Swagger UI**: `https://api-staging.eduautismo.example.com/docs`

1. Autenticar (endpoint `/api/v1/auth/login`)
2. Testar `/api/v1/intervention-plans/pending-review`:
   - Sem filtros
   - Com filtro de prioridade: high, medium, low
   - Com paginação: diferentes valores de skip/limit
   - Com filtro de profissional

**Checklist**:
- [ ] Interface Swagger carrega corretamente
- [ ] Endpoint aparece na documentação
- [ ] Parâmetros de query documentados
- [ ] Response schema correto
- [ ] Exemplos funcionam

### 1.7 Monitoramento Staging (24h)

**Deixar staging rodando por 24 horas antes de produção**

**Métricas a observar**:
- [ ] Latência P95 estável < 2s
- [ ] Taxa de erro < 1%
- [ ] Uso de CPU estável < 70%
- [ ] Uso de memória estável < 80%
- [ ] Sem memory leaks
- [ ] Query performance consistente

**Ferramentas**:
- Datadog: Dashboard de APM
- CloudWatch: Logs e métricas
- PostgreSQL: pg_stat_statements para queries lentas

---

## Fase 2: Aprovação para Produção

### 2.1 Sign-off do Time

**Aprovações necessárias**:
- [ ] Tech Lead - Performance validada
- [ ] Backend Team - Code review OK
- [ ] DevOps - Infraestrutura pronta
- [ ] QA - Testes funcionais passando
- [ ] Product Owner - Funcionalidade aprovada

### 2.2 Preparação de Produção

**Comunicação**:
- [ ] Notificar time de DevOps sobre janela de deploy
- [ ] Notificar stakeholders sobre nova funcionalidade
- [ ] Agendar janela de manutenção (se necessário)
- [ ] Preparar mensagem de comunicação para usuários

**Infraestrutura**:
- [ ] Revisar limites de recursos (CPU, memória, conexões DB)
- [ ] Verificar capacidade de scaling automático
- [ ] Confirmar backups automáticos ativos
- [ ] Verificar alertas de monitoramento configurados

---

## Fase 3: Deploy em Produção

### 3.1 Backup de Produção

```bash
# Backup completo do banco de produção
pg_dump -h prod-db.example.com -U user -d eduautismo_prod > \
  backup_prod_pre_deploy_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup criado
ls -lh backup_prod_pre_deploy_*.sql
```

**Checklist**:
- [ ] Backup criado com sucesso
- [ ] Tamanho do backup coerente (> 0 bytes)
- [ ] Backup armazenado em local seguro (S3)
- [ ] Retenção de backup configurada (30 dias)

### 3.2 Modo de Manutenção (Opcional)

**Se janela de manutenção for necessária**:

```bash
# Ativar modo de manutenção
./maintenance_mode.sh enable

# Aguardar requisições ativas terminarem (30-60s)
sleep 60
```

**Checklist**:
- [ ] Modo de manutenção ativado
- [ ] Mensagem exibida para usuários
- [ ] Requisições ativas finalizadas

### 3.3 Deploy da Aplicação

```bash
# 1. Deploy do código
./deploy.sh production main

# 2. Aguardar health check
./wait_for_health.sh https://api.eduautismo.example.com/health 300

# 3. Verificar logs iniciais
./tail_logs.sh production
```

**Checklist**:
- [ ] Deploy concluído sem erros
- [ ] Health check retorna 200 OK
- [ ] Aplicação iniciou corretamente
- [ ] Logs não mostram erros críticos

### 3.4 Executar Migration em Produção

```bash
# SSH no servidor de produção
ssh production-server

# Navegar para diretório da aplicação
cd /app/backend

# IMPORTANTE: Verificar versão atual antes
alembic current

# Executar migration
alembic upgrade head

# Confirmar nova versão
alembic current
# Deve mostrar: 20251124_1151_5403edb1d087 (head)
```

**Checklist**:
- [ ] Migration executada sem erros
- [ ] Versão do banco atualizada
- [ ] Logs de migration sem warnings
- [ ] Tempo de execução < 30s

### 3.5 Validar Índices em Produção

```bash
# Executar script de validação
python scripts/validate_performance_indexes.py
```

**Checklist**:
- [ ] Todos os 4 índices criados
- [ ] Query plan mostra uso de índices
- [ ] Sem erros de validação

### 3.6 Smoke Tests em Produção

```bash
# 1. Teste básico do endpoint
curl -H "Authorization: Bearer $PROD_TOKEN" \
  https://api.eduautismo.example.com/api/v1/intervention-plans/pending-review

# 2. Verificar estrutura de resposta
# Deve retornar: { items: [], total: N, high_priority: N, medium_priority: N, low_priority: N }
```

**Checklist**:
- [ ] Endpoint retorna 200 OK
- [ ] Estrutura de resposta correta
- [ ] Dados sendo retornados (se houver planos)
- [ ] Response time < 2s

### 3.7 Desativar Modo de Manutenção

```bash
# Desativar modo de manutenção
./maintenance_mode.sh disable
```

**Checklist**:
- [ ] Modo de manutenção desativado
- [ ] Usuários podem acessar a aplicação
- [ ] Mensagem de manutenção removida

### 3.8 Restart de Serviços (Se Necessário)

**Se houver problemas de performance iniciais**:

```bash
# Restart graceful dos workers
./restart_workers.sh graceful

# Ou restart completo do serviço
./restart_service.sh
```

**Checklist**:
- [ ] Serviços reiniciados com sucesso
- [ ] Health check OK após restart
- [ ] Logs mostram inicialização correta

---

## Fase 4: Monitoramento Pós-Deploy

### 4.1 Monitoramento Imediato (Primeiros 5 minutos)

**Verificar em tempo real**:

```bash
# Logs em tempo real
./tail_logs.sh production

# Métricas de API
watch -n 5 'curl -s https://api.eduautismo.example.com/health | jq .'

# Métricas de banco de dados
./monitor_db.sh production
```

**Checklist** (verificar a cada minuto):
- [ ] Min 1: Sem erros nos logs
- [ ] Min 2: Response time estável
- [ ] Min 3: Banco de dados respondendo normalmente
- [ ] Min 4: CPU e memória estáveis
- [ ] Min 5: Taxa de erro < 0.1%

**Se houver problemas**: Executar [Rollback Plan](#rollback-plan) imediatamente

### 4.2 Monitoramento de 1 Hora

**Datadog/CloudWatch Dashboard**:

Métricas a observar:
- [ ] Latência P50 < 500ms
- [ ] Latência P95 < 2000ms
- [ ] Latência P99 < 5000ms
- [ ] Taxa de erro < 1%
- [ ] Taxa de sucesso > 99%
- [ ] Throughput estável (req/s)
- [ ] CPU < 70%
- [ ] Memória < 80%
- [ ] Conexões de banco < 50% do pool

**Queries de Banco de Dados**:

```sql
-- Verificar queries lentas (> 1s)
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Verificar uso de índices
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'intervention_plans'
ORDER BY idx_scan DESC;
```

**Checklist**:
- [ ] Nenhuma query lenta detectada
- [ ] Índices sendo utilizados corretamente
- [ ] Nenhum bloqueio de transação (deadlock)

### 4.3 Monitoramento de 24 Horas

**Revisão Diária**:

Gerar relatório de métricas:
```bash
# Gerar relatório do último dia
./generate_metrics_report.sh --last-24h > metrics_report_$(date +%Y%m%d).txt
```

**Métricas a revisar**:
- [ ] Latência média mantida < 1s
- [ ] P95 mantida < 2s
- [ ] Sem picos anormais de latência
- [ ] Taxa de erro < 0.5%
- [ ] Sem memory leaks (uso de memória estável)
- [ ] Sem degradação de performance ao longo do tempo
- [ ] Logs sem erros críticos recorrentes

**Alertas Configurados**:
- [ ] Alerta de latência P95 > 3s
- [ ] Alerta de taxa de erro > 2%
- [ ] Alerta de CPU > 85%
- [ ] Alerta de memória > 90%
- [ ] Alerta de conexões DB > 80% do pool

### 4.4 Teste de Carga em Produção (Opcional)

**Apenas se aprovado e em horário de baixo tráfego**:

```bash
# Teste leve: 50 requisições, 5 concorrentes
python scripts/load_test_pending_review.py \
  --url https://api.eduautismo.example.com \
  --requests 50 \
  --concurrent 5 \
  --username prod_test@example.com \
  --password $PROD_TEST_PASS
```

**Checklist**:
- [ ] Teste aprovado por Tech Lead
- [ ] Executado em horário de baixo tráfego
- [ ] Métricas dentro do esperado
- [ ] Sem impacto em usuários reais

---

## Rollback Plan

### Opção 1: Rollback de Migration Apenas

**Quando usar**: Migration causou problemas, mas código está OK

```bash
# 1. SSH no servidor
ssh production-server

# 2. Reverter migration
cd /app/backend
alembic downgrade -1

# 3. Verificar versão
alembic current

# 4. Restart da aplicação (para limpar cache)
./restart_service.sh

# 5. Verificar health check
curl https://api.eduautismo.example.com/health
```

**Tempo estimado**: 2-5 minutos

### Opção 2: Rollback de Código

**Quando usar**: Código novo causou problemas, migration OK

```bash
# 1. Deploy da versão anterior
./deploy.sh production v1.2.3  # versão anterior estável

# 2. Aguardar health check
./wait_for_health.sh https://api.eduautismo.example.com/health 300

# 3. Verificar logs
./tail_logs.sh production
```

**Tempo estimado**: 5-10 minutos

### Opção 3: Rollback Completo (Código + Migration)

**Quando usar**: Ambos código e migration causaram problemas

```bash
# 1. Rollback de migration
ssh production-server
cd /app/backend
alembic downgrade -1

# 2. Deploy da versão anterior
./deploy.sh production v1.2.3

# 3. Aguardar health check
./wait_for_health.sh https://api.eduautismo.example.com/health 300

# 4. Verificar funcionamento
curl -H "Authorization: Bearer $TOKEN" \
  https://api.eduautismo.example.com/api/v1/intervention-plans
```

**Tempo estimado**: 10-15 minutos

### Critérios para Rollback

**Execute rollback imediatamente se**:
- Taxa de erro > 10% por mais de 2 minutos
- Latência P95 > 10s
- Banco de dados travado (deadlocks frequentes)
- Aplicação crashando repetidamente
- Perda de dados detectada

**Considere rollback se**:
- Taxa de erro > 5% por mais de 10 minutos
- Latência P95 > 5s por mais de 10 minutos
- CPU > 95% de forma sustentada
- Memória > 95% de forma sustentada
- Logs mostram erros críticos recorrentes

---

## 📞 Contatos de Emergência

**Durante o Deploy**:
- Tech Lead: [nome] - [telefone] - [email]
- DevOps On-Call: [nome] - [telefone] - [PagerDuty]
- DBA On-Call: [nome] - [telefone] - [PagerDuty]

**Escalation**:
- CTO: [nome] - [telefone] - [email]
- VP Engineering: [nome] - [telefone] - [email]

**Canais Slack**:
- `#deploys` - Anúncios de deploy
- `#incidents` - Incidentes de produção
- `#backend-team` - Discussão técnica

---

## 📚 Documentação Relacionada

- [PR #XXX](link) - Pull Request com mudanças
- [RELATORIO_FINAL_PERFORMANCE.md](./RELATORIO_FINAL_PERFORMANCE.md) - Relatório técnico completo
- [PENDING_REVIEW_ENDPOINT.md](./PENDING_REVIEW_ENDPOINT.md) - Documentação da API
- [CHANGELOG_PENDING_REVIEW.md](./CHANGELOG_PENDING_REVIEW.md) - Changelog das mudanças

---

## ✅ Assinatura de Conclusão

**Deploy realizado por**:
Nome: ___________________________
Data: ___________________________
Hora: ___________________________

**Validado por**:
Tech Lead: ___________________________
DevOps: ___________________________
QA: ___________________________

**Notas**:
```
[Adicionar observações importantes sobre o deploy]
```

---

**Versão do Checklist**: 1.0
**Última Atualização**: 2025-11-24
**Próxima Revisão**: Após deploy em produção
