# 🧪 Guia de Testes - Como Testar

## 📋 Visão Geral

Este guia descreve como testar mudanças em cada etapa do pipeline.

## 🔧 Testes em Feature Branch

### 1. Testes Locais (Antes do Push)

```bash
# Backend - Testes unitários
cd backend
pytest tests/unit -v

# Backend - Testes de integração
pytest tests/integration -v

# Backend - Coverage
pytest --cov=app --cov-report=html

# Backend - Linting
black --check app/ tests/
flake8 app/ tests/
mypy app/

# Frontend - Testes
cd frontend
npm test

# Frontend - Linting
npm run lint

# Frontend - Build
npm run build
```

### 2. Testes com Docker (Ambiente Completo)

```bash
# Subir ambiente completo
docker-compose up -d

# Executar testes no container
docker-compose exec api pytest tests/ -v

# Ver logs
docker-compose logs -f api

# Parar ambiente
docker-compose down
```

### 3. Push e Validação CI

```bash
# Push da feature branch
git push origin feature/minha-feature

# Acompanhar pipeline
gh run watch

# Ver resultado
gh run list --branch feature/minha-feature
```

## 🟢 Testes em Dev

### 1. Após Merge para Dev

```bash
# Verificar deploy
gh run list --workflow=00-orchestrator.yml --branch=dev

# Acessar ambiente dev
curl https://api-dev.eduautismo.com/health

# Testar endpoint específico
curl -X POST https://api-dev.eduautismo.com/api/v1/students \
  -H "Authorization: Bearer $DEV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"age": 10, "grade_level": "fundamental_1_3ano"}'
```

### 2. Smoke Tests em Dev

```bash
# Executar smoke tests
cd scripts
./smoke-tests-dev.sh

# Ou manualmente
curl https://api-dev.eduautismo.com/health
curl https://api-dev.eduautismo.com/api/v1/docs
```

### 3. Testes Funcionais

```bash
# Usar Postman Collection
newman run postman/eduautismo-dev.json \
  --environment postman/dev-environment.json

# Ou via interface
# Importar collection no Postman e executar
```

## 🟡 Testes em Staging

### 1. Após Merge para Staging

```bash
# Verificar deploy
gh run list --workflow=00-orchestrator.yml --branch=staging

# Acessar ambiente staging
curl https://api-staging.eduautismo.com/health
```

### 2. Testes de Regressão

```bash
# Executar suite completa
cd scripts
./regression-tests-staging.sh

# Testes de API
newman run postman/eduautismo-staging.json \
  --environment postman/staging-environment.json \
  --reporters cli,json

# Testes de carga (opcional)
k6 run tests/load/basic-load-test.js
```

### 3. Testes de Integração E2E

```bash
# Se houver frontend
cd frontend
npm run test:e2e -- --env=staging

# Ou com Cypress
npx cypress run --env environment=staging
```

### 4. Validação Manual

**Checklist de Validação Staging:**

- [ ] Login funciona
- [ ] Criar aluno funciona
- [ ] Gerar atividade funciona
- [ ] Aplicar avaliação funciona
- [ ] Visualizar dashboard funciona
- [ ] Gerar relatório funciona
- [ ] Performance aceitável (< 2s por request)
- [ ] Sem erros no console
- [ ] Logs sem erros críticos

```bash
# Verificar logs
aws logs tail /aws/ecs/eduautismo-staging --follow

# Verificar métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=eduautismo-staging \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## 🔴 Testes em Production

### 1. Pré-Deploy (Staging)

**ANTES de fazer merge para main:**

```bash
# Executar todos os testes de staging
./scripts/pre-production-checklist.sh

# Validar migrations
cd backend
alembic upgrade head --sql > migration-preview.sql
cat migration-preview.sql  # Revisar SQL

# Backup do banco (staging)
./scripts/backup-database.sh staging
```

### 2. Deploy para Production

```bash
# Após merge para main, deploy manual
gh workflow run 06-deploy-environment.yml \
  -f environment=production \
  -f image_tag=main-$(git rev-parse --short HEAD)

# Acompanhar deploy
gh run watch
```

### 3. Smoke Tests Pós-Deploy

```bash
# Executar imediatamente após deploy
./scripts/smoke-tests-production.sh

# Verificar health
curl https://api.eduautismo.com/health

# Testar endpoints críticos (read-only)
curl https://api.eduautismo.com/api/v1/health/db
curl https://api.eduautismo.com/api/v1/health/redis
```

### 4. Monitoramento Pós-Deploy

```bash
# Monitorar logs (primeiros 15 minutos)
aws logs tail /aws/ecs/eduautismo-production --follow

# Verificar métricas
# - Taxa de erro < 1%
# - Latência p95 < 500ms
# - CPU < 70%
# - Memória < 80%

# Verificar alertas
# Acessar Datadog/CloudWatch e verificar se há alertas
```

### 5. Validação de Produção

**Checklist Pós-Deploy Production:**

- [ ] Health check retorna 200
- [ ] Logs sem erros críticos (primeiros 15min)
- [ ] Métricas dentro do normal
- [ ] Sem alertas disparados
- [ ] Teste de login funciona
- [ ] Endpoints críticos respondem
- [ ] Performance aceitável
- [ ] Usuários conseguem acessar

## 🚨 Testes de Rollback

### Simular Rollback em Staging

```bash
# 1. Fazer deploy de versão anterior
gh workflow run 06-deploy-environment.yml \
  -f environment=staging \
  -f image_tag=staging-previous

# 2. Validar que rollback funcionou
./scripts/smoke-tests-staging.sh

# 3. Verificar logs
aws logs tail /aws/ecs/eduautismo-staging --since 5m
```

### Rollback em Production (Emergência)

```bash
# 1. Identificar última versão estável
git log --oneline main

# 2. Deploy da versão anterior
gh workflow run 06-deploy-environment.yml \
  -f environment=production \
  -f image_tag=main-<commit-hash-anterior>

# 3. Validar rollback
./scripts/smoke-tests-production.sh

# 4. Notificar stakeholders
# Enviar comunicado sobre rollback
```

## 📊 Scripts de Teste

### Criar Script de Smoke Tests

```bash
# scripts/smoke-tests-dev.sh
#!/bin/bash
set -e

API_URL="https://api-dev.eduautismo.com"

echo "🧪 Running smoke tests for DEV..."

# Health check
echo "Testing /health..."
curl -f $API_URL/health || exit 1

# API docs
echo "Testing /api/v1/docs..."
curl -f $API_URL/api/v1/docs || exit 1

echo "✅ All smoke tests passed!"
```

### Criar Script de Testes de Regressão

```bash
# scripts/regression-tests-staging.sh
#!/bin/bash
set -e

echo "🧪 Running regression tests for STAGING..."

# Executar Postman collection
newman run postman/eduautismo-staging.json \
  --environment postman/staging-environment.json \
  --reporters cli,json \
  --reporter-json-export results/regression-results.json

# Verificar resultados
if [ $? -eq 0 ]; then
  echo "✅ All regression tests passed!"
else
  echo "❌ Regression tests failed!"
  exit 1
fi
```

### Criar Checklist Pré-Production

```bash
# scripts/pre-production-checklist.sh
#!/bin/bash

echo "📋 Pre-Production Checklist"
echo "============================"
echo ""

# 1. Verificar staging
echo "1. Checking staging health..."
curl -f https://api-staging.eduautismo.com/health || exit 1

# 2. Executar testes
echo "2. Running regression tests..."
./scripts/regression-tests-staging.sh || exit 1

# 3. Verificar migrations
echo "3. Checking migrations..."
cd backend
alembic upgrade head --sql > /tmp/migration-preview.sql
echo "Review migration SQL in /tmp/migration-preview.sql"

# 4. Backup
echo "4. Creating backup..."
./scripts/backup-database.sh staging

echo ""
echo "✅ Pre-production checklist complete!"
echo "Ready to merge to main"
```

## 🔍 Troubleshooting

### Testes Falhando Localmente

```bash
# Limpar ambiente
docker-compose down -v
docker system prune -f

# Reinstalar dependências
cd backend
pip install -r requirements.txt -r requirements-dev.txt

cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Pipeline Falhando no CI

```bash
# Ver logs detalhados
gh run view <run-id> --log

# Reexecutar job específico
gh run rerun <run-id> --job <job-id>

# Reexecutar apenas jobs falhados
gh run rerun <run-id> --failed
```

### Testes Passam Local mas Falham no CI

- Verificar versões de dependências
- Verificar variáveis de ambiente
- Verificar diferenças de timezone
- Verificar permissões de arquivo

## 📚 Recursos Adicionais

- [Postman Collection](../postman/README.md)
- [Load Testing Guide](./LOAD_TESTING.md)
- [Monitoring Guide](./MONITORING.md)
- [Rollback Procedures](./ROLLBACK.md)

---

**Última atualização**: 2025-01-15
