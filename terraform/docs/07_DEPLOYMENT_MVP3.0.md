# 🚀 GUIA DE DEPLOYMENT - MVP 3.0

**Plataforma Multidisciplinar EduAutismo IA**
**Versão:** 3.0
**Data:** 05/12/2025
**Infraestrutura:** AWS com Terraform

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Arquitetura MVP 3.0](#arquitetura-mvp-30)
3. [Componentes Novos](#componentes-novos)
4. [Configuração por Ambiente](#configuração-por-ambiente)
5. [Deploy Passo a Passo](#deploy-passo-a-passo)
6. [Validação Pós-Deploy](#validação-pós-deploy)
7. [Rollback](#rollback)
8. [Troubleshooting](#troubleshooting)

---

## 1. Pré-requisitos

### 1.1 Ferramentas Necessárias

```bash
# Terraform
terraform --version
# Versão requerida: >= 1.5.0

# AWS CLI
aws --version
# Versão requerida: >= 2.0.0

# jq (para parsing de JSON)
jq --version

# Git
git --version
```

### 1.2 Credenciais AWS

```bash
# Configurar credenciais AWS
aws configure

# Verificar credenciais
aws sts get-caller-identity

# Output esperado:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/..."
# }
```

### 1.3 Permissões IAM Necessárias

O usuário/role deve ter permissões para:

- **VPC**: Criar VPCs, Subnets, Route Tables, Internet Gateways
- **ECS**: Criar clusters, task definitions, services
- **RDS**: Criar instâncias PostgreSQL, snapshots
- **ElastiCache**: Criar clusters Redis (NOVO MVP 3.0)
- **S3**: Criar buckets, lifecycle policies
- **CloudWatch**: Criar log groups, alarmes
- **IAM**: Criar roles e policies
- **Secrets Manager**: Criar e gerenciar secrets
- **ECR**: Push de imagens Docker

---

## 2. Arquitetura MVP 3.0

### 2.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    USUÁRIOS (Professores)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS CloudFront (CDN) [Produção]                │
│              - Cache de assets estáticos                    │
│              - TLS/SSL termination                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Load Balancer (ALB)                │
│              - Health checks                                │
│              - Target groups (blue/green)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ECS FARGATE CLUSTER                      │
│              ┌──────────────────────────────────┐           │
│              │     FastAPI Backend Tasks       │           │
│              │  Dev: 1 task (512 MB)           │           │
│              │  Staging: 2 tasks (1 GB)        │           │
│              │  Prod: 3-10 tasks (2 GB)        │           │
│              └──────────────────────────────────┘           │
│                                                              │
│              MVP 3.0 Environment Variables:                 │
│              - REDIS_URL                                    │
│              - ENABLE_MULTIDISCIPLINARY=true                │
│              - MAX_DISCIPLINES=25                           │
│              - MAX_GRADE_LEVELS=18                          │
│              - BNCC_CACHE_TTL=3600                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   RDS        │ │ ElastiCache  │ │      S3      │
│ PostgreSQL   │ │ Redis (NOVO) │ │   Buckets    │
│              │ │              │ │              │
│ v15.4        │ │ v7.0         │ │ - Uploads    │
│ Multi-AZ     │ │ Multi-AZ     │ │ - Exports    │
│ (Prod)       │ │ (Prod)       │ │ - ML Models  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 Fluxo de Requisição MVP 3.0

```
1. Professor solicita atividade de Matemática para Fundamental 1
   ↓
2. ALB encaminha para ECS Task disponível
   ↓
3. Backend verifica cache Redis (NOVO)
   ├─ Cache HIT → Retorna em < 50ms
   └─ Cache MISS → Continua
       ↓
4. Consulta PostgreSQL (disciplina + série + BNCC)
   ↓
5. Chama GPT-4o com prompt contextualizado
   ↓
6. Armazena resultado no Redis (TTL 3600s)
   ↓
7. Retorna atividade personalizada
```

---

## 3. Componentes Novos (MVP 3.0)

### 3.1 ElastiCache Redis

**Propósito:** Cache distribuído para:
- Sessões de usuário
- Resultados de queries BNCC
- Respostas de GPT-4o
- Metadados de disciplinas

**Configuração por Ambiente:**

| Ambiente   | Node Type          | Nós | Multi-AZ | Encryption | Auth Token |
|------------|-------------------|-----|----------|------------|------------|
| Dev        | cache.t3.micro    | 1   | ❌       | ❌         | ❌         |
| Staging    | cache.t3.small    | 2   | ✅       | ✅         | ✅         |
| Production | cache.r5.large    | 3   | ✅       | ✅         | ✅         |

**Custos Estimados:**
- Dev: ~$15/mês
- Staging: ~$75/mês
- Production: ~$250-350/mês

### 3.2 ECS Task Definition (Atualizado)

**Recursos Aumentados para MVP 3.0:**

| Ambiente   | CPU (vCPU) | Memory (GB) | Desired Count |
|------------|------------|-------------|---------------|
| Dev        | 0.5        | 1           | 1             |
| Staging    | 0.5        | 1           | 2             |
| Production | 1.0        | 2           | 3-10          |

**Novas Variáveis de Ambiente:**

```hcl
REDIS_URL                  = "redis://redis-endpoint:6379"
REDIS_HOST                 = "redis-endpoint.cache.amazonaws.com"
REDIS_PORT                 = "6379"
ENABLE_MULTIDISCIPLINARY   = "true"
MAX_DISCIPLINES            = "25"
MAX_GRADE_LEVELS           = "18"
BNCC_CACHE_TTL            = "3600"  # 1 hora
NLP_CACHE_TTL             = "1800"  # 30 minutos
```

---

## 4. Configuração por Ambiente

### 4.1 Development

**Arquivo:** `terraform/environments/dev/terraform.tfvars`

**Características:**
- Custo mínimo (~$150-200/mês)
- 1 instância de cada componente
- Sem Multi-AZ
- Sem criptografia (performance)
- Logs por 7 dias

**Uso:**
```bash
cd terraform
terraform workspace select dev || terraform workspace new dev
terraform plan -var-file="environments/dev/terraform.tfvars"
```

### 4.2 Staging

**Arquivo:** `terraform/environments/staging/terraform.tfvars`

**Características:**
- Custo moderado (~$400-500/mês)
- 2 instâncias de cada componente
- Multi-AZ habilitado
- Criptografia completa
- Logs por 30 dias
- Simula ambiente de produção

**Uso:**
```bash
cd terraform
terraform workspace select staging || terraform workspace new staging
terraform plan -var-file="environments/staging/terraform.tfvars"
```

### 4.3 Production

**Arquivo:** `terraform/environments/production/terraform.tfvars`

**Características:**
- Custo otimizado (~$1,500-2,500/mês)
- 3+ instâncias com auto-scaling
- Multi-AZ em múltiplas regiões
- Criptografia completa (LGPD)
- Logs por 90 dias
- Backup diário por 30 dias
- WAF habilitado
- CloudFront CDN
- LGPD compliance

**Uso:**
```bash
cd terraform
terraform workspace select production || terraform workspace new production
terraform plan -var-file="environments/production/terraform.tfvars"
```

---

## 5. Deploy Passo a Passo

### 5.1 Primeira Vez (Bootstrap)

```bash
# 1. Clonar repositório
git clone https://github.com/cleybersilva/eduautismo-ia-mvp.git
cd eduautismo-ia-mvp/terraform

# 2. Inicializar Terraform
terraform init

# 3. Criar workspace para o ambiente
terraform workspace new dev
# ou: terraform workspace new staging
# ou: terraform workspace new production

# 4. Validar configuração
terraform validate

# 5. Planejar mudanças
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan

# 6. Revisar plano
# IMPORTANTE: Revisar todos os recursos que serão criados
# Procurar por:
# - "+ create" (novos recursos)
# - "~ update" (atualizações)
# - "- destroy" (destruições - CUIDADO!)

# 7. Aplicar mudanças
terraform apply tfplan

# 8. Aguardar conclusão (15-30 minutos)
```

### 5.2 Atualização (MVP 3.0 - Incremental)

Para ambientes existentes que precisam adicionar o cache Redis:

```bash
# 1. Fazer backup do estado atual
terraform state pull > terraform.tfstate.backup

# 2. Selecionar workspace
terraform workspace select production

# 3. Planejar apenas o módulo cache
terraform plan -var-file="environments/production/terraform.tfvars" \
  -target=module.cache \
  -out=tfplan-cache

# 4. Revisar plano do cache
# Verificar:
# - Security group correto
# - Subnet group nas subnets privadas
# - Configurações de encryption
# - Auth token habilitado (prod/staging)

# 5. Aplicar criação do cache
terraform apply tfplan-cache

# 6. Aguardar criação do Redis (5-10 minutos)

# 7. Planejar atualização do ECS com variáveis Redis
terraform plan -var-file="environments/production/terraform.tfvars" \
  -target=module.compute \
  -out=tfplan-ecs

# 8. Aplicar atualização do ECS
# NOTA: Isso fará rolling update das tasks (zero downtime)
terraform apply tfplan-ecs

# 9. Aguardar atualização (5-10 minutos)
```

### 5.3 Deploy Blue/Green (Produção)

Para deploys sem downtime:

```bash
# 1. Criar nova versão da task definition
# (já feito automaticamente pelo Terraform)

# 2. ECS Service fará rolling update automático:
#    - Starta novos tasks com nova configuração
#    - Aguarda health checks passarem
#    - Remove tasks antigos

# 3. Monitorar atualização
aws ecs describe-services \
  --cluster eduautismo-ia-production \
  --services eduautismo-ia-production-app \
  --query 'services[0].events[:5]'

# 4. Verificar tasks saudáveis
aws ecs list-tasks \
  --cluster eduautismo-ia-production \
  --service-name eduautismo-ia-production-app

# 5. Verificar health checks do ALB
aws elbv2 describe-target-health \
  --target-group-arn <ARN-DO-TARGET-GROUP>
```

---

## 6. Validação Pós-Deploy

### 6.1 Checklist de Validação

```bash
# ✅ 1. Verificar recursos criados
terraform output

# Outputs esperados:
# - vpc_id
# - redis_endpoint (NOVO MVP 3.0)
# - redis_port (NOVO MVP 3.0)
# - rds_endpoint
# - ecs_cluster_name
# - alb_dns_name

# ✅ 2. Verificar Redis está acessível
aws elasticache describe-replication-groups \
  --replication-group-id eduautismo-ia-<env>-redis

# Status esperado: "available"

# ✅ 3. Verificar ECS tasks rodando
aws ecs list-tasks \
  --cluster eduautismo-ia-<env> \
  --desired-status RUNNING

# Deve mostrar tasks em estado RUNNING

# ✅ 4. Verificar logs
aws logs tail /ecs/eduautismo-ia-<env> --follow

# Procurar por:
# - "Redis connection successful" (NOVO)
# - "Application startup complete"
# - Sem stack traces de erro

# ✅ 5. Testar endpoint de health
ALB_DNS=$(terraform output -raw alb_dns_name)
curl -v http://${ALB_DNS}/health

# Resposta esperada: HTTP 200
# {
#   "status": "healthy",
#   "redis": "connected",  # NOVO MVP 3.0
#   "database": "connected",
#   "version": "3.0.0"
# }

# ✅ 6. Testar cache Redis via API
curl -v http://${ALB_DNS}/api/v1/activities/meta/subjects

# Primeira chamada: MISS (lenta)
# Segunda chamada: HIT (rápida < 50ms)

# ✅ 7. Verificar métricas no CloudWatch
# - CPUUtilization (ECS Tasks)
# - CacheHitRate (Redis) - NOVO
# - DatabaseConnections (RDS)
```

### 6.2 Testes Funcionais MVP 3.0

```bash
# Test 1: Listar disciplinas (deve vir do cache após 1ª chamada)
curl http://${ALB_DNS}/api/v1/activities/meta/subjects

# Test 2: Listar níveis escolares
curl http://${ALB_DNS}/api/v1/activities/meta/grade-levels

# Test 3: Buscar por código BNCC
curl "http://${ALB_DNS}/api/v1/activities/search/bncc/EF01MA01"

# Test 4: Filtro multidisciplinar
curl "http://${ALB_DNS}/api/v1/activities/search?subject=matematica&grade_level=fundamental_1_1ano"

# Test 5: Verificar cabeçalhos de cache
curl -I http://${ALB_DNS}/api/v1/activities/meta/subjects
# Procurar por: X-Cache: HIT (após 2ª chamada)
```

---

## 7. Rollback

### 7.1 Rollback Rápido (ECS Only)

Se houver problema com a nova versão do backend:

```bash
# 1. Reverter task definition anterior
aws ecs update-service \
  --cluster eduautismo-ia-production \
  --service eduautismo-ia-production-app \
  --task-definition eduautismo-ia-production-app:REVISION_ANTERIOR

# 2. Forçar novo deployment
aws ecs update-service \
  --cluster eduautismo-ia-production \
  --service eduautismo-ia-production-app \
  --force-new-deployment

# 3. Monitorar rollback
aws ecs describe-services \
  --cluster eduautismo-ia-production \
  --services eduautismo-ia-production-app
```

### 7.2 Rollback Terraform Completo

Se houver problema com a infraestrutura:

```bash
# 1. Restaurar estado anterior
cp terraform.tfstate.backup terraform.tfstate

# 2. Planejar reversão
terraform plan -var-file="environments/production/terraform.tfvars"

# 3. Aplicar reversão
terraform apply -auto-approve

# 4. Verificar recursos
terraform state list
```

### 7.3 Rollback do Redis (Se necessário)

```bash
# 1. Remover Redis do módulo compute
# Editar terraform/main.tf e remover linhas:
# redis_url = module.cache.redis_url
# redis_host = module.cache.redis_primary_endpoint_address
# redis_port = module.cache.redis_port

# 2. Aplicar mudança
terraform apply -var-file="environments/production/terraform.tfvars" \
  -target=module.compute

# 3. Opcionalmente destruir Redis (para economizar custos)
terraform destroy -var-file="environments/production/terraform.tfvars" \
  -target=module.cache
```

---

## 8. Troubleshooting

### 8.1 Redis Connection Failed

**Sintoma:**
```
ERROR: Failed to connect to Redis: Connection timeout
```

**Diagnóstico:**
```bash
# 1. Verificar security group do Redis
aws ec2 describe-security-groups \
  --group-ids $(terraform output -raw redis_security_group_id)

# Verificar se há regra de ingress da porta 6379 para o SG do ECS

# 2. Verificar se Redis está rodando
aws elasticache describe-replication-groups \
  --replication-group-id eduautismo-ia-production-redis

# Status deve ser "available"

# 3. Verificar endpoint
terraform output redis_endpoint

# 4. Testar conectividade de dentro de um task ECS
aws ecs execute-command \
  --cluster eduautismo-ia-production \
  --task <TASK_ID> \
  --container app \
  --interactive \
  --command "redis-cli -h <REDIS_ENDPOINT> ping"

# Resposta esperada: PONG
```

**Solução:**
```bash
# Se o SG não tiver a regra, adicionar manualmente:
aws ec2 authorize-security-group-ingress \
  --group-id <REDIS_SG_ID> \
  --protocol tcp \
  --port 6379 \
  --source-group <ECS_SG_ID>
```

### 8.2 ECS Tasks Não Iniciam

**Sintoma:**
```
Tasks stuck in PENDING state
```

**Diagnóstico:**
```bash
# 1. Verificar eventos do serviço
aws ecs describe-services \
  --cluster eduautismo-ia-production \
  --services eduautismo-ia-production-app \
  --query 'services[0].events[:10]'

# Procurar por erros como:
# - "unable to pull image" → Problema no ECR
# - "insufficient resources" → Aumentar CPU/Memory
# - "unable to assume role" → Problema IAM

# 2. Verificar logs da task
aws logs tail /ecs/eduautismo-ia-production --follow

# 3. Verificar se há tasks stopped
aws ecs list-tasks \
  --cluster eduautismo-ia-production \
  --desired-status STOPPED | head -20
```

**Solução:**
Depende do erro específico nos eventos.

### 8.3 Terraform Apply Falha

**Sintoma:**
```
Error: Error creating ElastiCache Replication Group:
InvalidParameterCombination: Automatic failover requires at least 2 nodes
```

**Solução:**
```bash
# Verificar configuração do ambiente
# Para dev com 1 nó, desabilitar automatic_failover
# terraform/environments/dev/terraform.tfvars:
redis_num_cache_nodes = 1
redis_automatic_failover_enabled = false
redis_multi_az_enabled = false
```

### 8.4 High Redis Memory Usage

**Sintoma:**
```
CloudWatch alarm: RedisMemoryUsage > 80%
```

**Diagnóstico:**
```bash
# Conectar ao Redis e verificar info
redis-cli -h <REDIS_ENDPOINT> info memory

# Verificar keys grandes
redis-cli -h <REDIS_ENDPOINT> --bigkeys
```

**Solução:**
```bash
# Opção 1: Aumentar node type (vertical scaling)
# terraform/environments/production/terraform.tfvars:
redis_node_type = "cache.r5.xlarge"  # De large para xlarge

# Opção 2: Ajustar TTLs (reduzir tempo de cache)
# ECS environment variables:
BNCC_CACHE_TTL = "1800"  # De 3600 para 1800
NLP_CACHE_TTL = "900"    # De 1800 para 900

# Opção 3: Limpar cache manualmente (emergência)
redis-cli -h <REDIS_ENDPOINT> FLUSHALL
```

---

## 9. Monitoramento Contínuo

### 9.1 Métricas Essenciais MVP 3.0

**CloudWatch Dashboards:**
```bash
# Criar dashboard customizado
aws cloudwatch put-dashboard \
  --dashboard-name eduautismo-mvp3 \
  --dashboard-body file://cloudwatch-dashboard-mvp3.json
```

**Métricas-chave:**
1. **Redis (NOVO):**
   - CacheHits / CacheMisses
   - EngineCPUUtilization
   - DatabaseMemoryUsagePercentage
   - NetworkBytesIn / NetworkBytesOut

2. **ECS:**
   - CPUUtilization (target < 70%)
   - MemoryUtilization (target < 80%)
   - TaskCount (running vs desired)

3. **RDS:**
   - DatabaseConnections
   - ReadLatency / WriteLatency
   - FreeStorageSpace

4. **ALB:**
   - TargetResponseTime (P95 < 500ms)
   - HealthyHostCount
   - RequestCount

### 9.2 Alarmes Críticos

```bash
# Alarme: Redis Down
aws cloudwatch put-metric-alarm \
  --alarm-name eduautismo-prod-redis-down \
  --alarm-description "Redis cluster unavailable" \
  --metric-name ReplicationLag \
  --namespace AWS/ElastiCache \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold

# Alarme: High Cache Miss Rate
aws cloudwatch put-metric-alarm \
  --alarm-name eduautismo-prod-cache-miss-high \
  --alarm-description "Cache hit rate below 70%" \
  --metric-name CacheMissRate \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 30 \
  --comparison-operator GreaterThanThreshold
```

---

## 10. Custos Estimados MVP 3.0

### 10.1 Breakdown por Ambiente

**Development:**
```
ElastiCache Redis (cache.t3.micro):     $15/mês
RDS PostgreSQL (db.t3.micro):           $25/mês
ECS Fargate (1 task, 0.5 vCPU, 1 GB):  $20/mês
ALB:                                    $20/mês
S3 + Logs:                              $10/mês
Data Transfer:                          $10/mês
────────────────────────────────────────────────
TOTAL DEV:                             ~$100-150/mês
```

**Staging:**
```
ElastiCache Redis (cache.t3.small, 2 nós): $75/mês
RDS PostgreSQL (db.t3.small, Multi-AZ):    $100/mês
ECS Fargate (2 tasks, 0.5 vCPU, 1 GB):    $40/mês
ALB:                                       $25/mês
S3 + Logs:                                 $30/mês
Data Transfer:                             $30/mês
────────────────────────────────────────────────
TOTAL STAGING:                            ~$300-400/mês
```

**Production:**
```
ElastiCache Redis (cache.r5.large, 3 nós): $350/mês
RDS PostgreSQL (db.r5.large, Multi-AZ):    $500/mês
ECS Fargate (3-10 tasks, 1 vCPU, 2 GB):   $200-600/mês
ALB:                                       $35/mês
CloudFront CDN:                            $50-150/mês
S3 + Logs + Backups:                       $100/mês
Data Transfer:                             $100/mês
WAF:                                       $50/mês
Secrets Manager:                           $15/mês
CloudWatch Logs:                           $50/mês
────────────────────────────────────────────────
TOTAL PRODUCTION:                         ~$1,450-2,000/mês
```

### 10.2 Otimização de Custos

**Recomendações:**
1. Use Savings Plans para ECS Fargate (até 50% desconto)
2. Use Reserved Instances para RDS produção (até 65% desconto)
3. Configure lifecycle policies S3 (move para Glacier após 90 dias)
4. Desabilite ambientes dev/staging fora do horário comercial
5. Use spot instances para tasks não críticas (até 90% desconto)

---

## 11. Próximos Passos

Após deploy bem-sucedido do MVP 3.0:

- [ ] Configurar alertas do Datadog
- [ ] Habilitar AWS X-Ray para tracing distribuído
- [ ] Implementar auto-scaling policies customizadas
- [ ] Configurar backups cross-region (DR)
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Executar testes de carga (locust/k6)
- [ ] Revisar políticas de retention de logs
- [ ] Documentar runbooks de incidentes

---

## 12. Contatos e Suporte

**Equipe DevOps:**
- Email: devops@eduautismo-ia.com
- Slack: #eduautismo-devops
- On-call: PagerDuty

**Documentação:**
- Terraform Docs: `/terraform/README.md`
- Architecture: `/docs/ARCHITECTURE.md`
- API Docs: `https://api.eduautismo-ia.com/docs`

**Incidentes:**
- Severidade 1 (Produção down): Acionar on-call imediatamente
- Severidade 2 (Performance): Abrir ticket no Jira
- Severidade 3 (Não urgente): Discussão no Slack

---

**Versão deste documento:** 1.0
**Última atualização:** 05/12/2025
**Autor:** DevOps Team / Cleyber Silva
**Revisores:** [@cleybersilva](https://github.com/cleybersilva)

✅ **MVP 3.0 Pronto para Deploy!**
