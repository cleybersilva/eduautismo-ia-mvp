# 🏗️ MVP 3.0 - PLANO DE INFRAESTRUTURA AWS

**Data:** 05/12/2025
**Versão:** 1.0
**Status:** 🚧 Em Implementação

---

## 📋 VISÃO GERAL

Atualização da infraestrutura AWS para suportar o MVP 3.0 da Plataforma Multidisciplinar, incluindo:

- ✅ Suporte para 25 disciplinas e 18 níveis escolares
- ✅ Cache distribuído (Redis/ElastiCache)
- ✅ Escalabilidade para 50.000-100.000 alunos ativos
- ✅ Alta disponibilidade (99.9% SLA)
- ✅ Performance otimizada (P95 < 500ms)

---

## 🎯 OBJETIVOS DA ATUALIZAÇÃO

### 1. Performance
- ✅ Cache Redis para otimizar consultas multidisciplinares
- ✅ RDS PostgreSQL otimizado para queries BNCC
- ✅ CDN (CloudFront) para assets estáticos
- ✅ Auto-scaling baseado em métricas de uso

### 2. Escalabilidade
- ✅ ECS Fargate com auto-scaling (2-20 tasks)
- ✅ RDS Read Replicas para queries read-heavy
- ✅ ElastiCache cluster mode para distribuição de cache

### 3. Segurança
- ✅ LGPD compliance (criptografia at rest e in transit)
- ✅ AWS KMS para gerenciamento de chaves
- ✅ Secrets Manager para credenciais
- ✅ WAF para proteção de API

### 4. Observabilidade
- ✅ CloudWatch Logs para todos os serviços
- ✅ CloudWatch Metrics customizadas (disciplinas, BNCC)
- ✅ X-Ray para distributed tracing
- ✅ Datadog integration (APM, logs, metrics)

---

## 🏛️ ARQUITETURA ALVO

```
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIOS                            │
│                    (Professores/Alunos)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS CLOUDFRONT (CDN)                     │
│              - Cache de assets estáticos                    │
│              - TLS/SSL termination                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS WAF (Firewall)                       │
│              - Rate limiting                                │
│              - DDoS protection                              │
│              - Bot detection                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION LOAD BALANCER (ALB)                │
│              - Health checks                                │
│              - SSL offloading                               │
│              - Target groups (blue/green)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ECS FARGATE CLUSTER                      │
│              ┌──────────────────────────────────┐           │
│              │     FastAPI Backend Tasks       │           │
│              │  (Auto-scaling: 2-20 tasks)     │           │
│              └──────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   RDS        │ │ ElastiCache  │ │     S3       │
│ PostgreSQL   │ │    Redis     │ │  Artifacts   │
│              │ │              │ │              │
│ - Main DB    │ │ - Sessions   │ │ - Uploads    │
│ - Read       │ │ - Cache      │ │ - Exports    │
│   Replicas   │ │ - Rate limit │ │ - ML Models  │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  MONITORING & LOGGING                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CloudWatch  │  │   X-Ray      │  │   Datadog    │      │
│  │  Logs/Metrics│  │  Tracing     │  │  APM/Alerts  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 COMPONENTES A SEREM ADICIONADOS/ATUALIZADOS

### 1. ✅ ElastiCache (Redis) - NOVO
**Arquivo:** `terraform/modules/cache/main.tf`

**Recursos:**
- `aws_elasticache_subnet_group` - Subnet group para Redis
- `aws_elasticache_replication_group` - Redis cluster
- `aws_security_group` - Security group para Redis

**Configuração:**
```hcl
- Engine: Redis 7.0
- Node Type: cache.t3.micro (dev), cache.r6g.large (prod)
- Replicas: 1 (dev), 2 (prod)
- Cluster Mode: Enabled (prod)
- Encryption: At rest + in transit
```

### 2. ✅ RDS PostgreSQL - ATUALIZADO
**Arquivo:** `terraform/modules/database/main.tf`

**Melhorias:**
- ✅ Engine version: 14 → 15.4
- ✅ Parameter group customizado (BNCC queries otimizadas)
- ✅ Read replicas para produção
- ✅ Performance Insights habilitado
- ✅ Enhanced Monitoring

**Parâmetros Customizados:**
```hcl
- shared_preload_libraries = 'pg_stat_statements'
- max_connections = 200 (dev), 500 (prod)
- work_mem = 16MB
- effective_cache_size = 4GB (prod)
```

### 3. ✅ ECS Fargate - ATUALIZADO
**Arquivo:** `terraform/modules/compute/main.tf`

**Melhorias:**
- ✅ Task CPU: 512 → 1024 (prod)
- ✅ Task Memory: 1GB → 2GB (prod)
- ✅ Auto-scaling metrics customizadas
- ✅ Health check otimizado
- ✅ Container Insights habilitado

**Variáveis de Ambiente MVP 3.0:**
```hcl
- REDIS_URL = elasticache_endpoint
- ENABLE_MULTIDISCIPLINARY = true
- MAX_DISCIPLINES = 25
- MAX_GRADE_LEVELS = 18
- BNCC_CACHE_TTL = 3600
- NLP_CACHE_TTL = 1800
```

### 4. ✅ CloudWatch - ATUALIZADO
**Arquivo:** `terraform/modules/monitoring/main.tf` (NOVO)

**Recursos:**
- ✅ CloudWatch Dashboard multidisciplinar
- ✅ Alarmes customizados (por disciplina, BNCC)
- ✅ Log Groups com retention policy
- ✅ Metric filters

**Métricas Customizadas:**
```
- eduautismo/disciplines/requests_per_subject
- eduautismo/bncc/searches_per_code
- eduautismo/cache/hit_rate
- eduautismo/api/p95_latency
```

### 5. ✅ WAF - NOVO
**Arquivo:** `terraform/modules/security/waf.tf` (NOVO)

**Recursos:**
- `aws_wafv2_web_acl` - Web ACL principal
- `aws_wafv2_rule_group` - Rule groups customizados

**Regras:**
- ✅ Rate limiting (100 req/min por IP)
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ Bot detection
- ✅ Geo-blocking (apenas Brasil)

### 6. ✅ S3 Buckets - ATUALIZADO
**Arquivo:** `terraform/modules/storage/main.tf`

**Novos Buckets:**
- ✅ `eduautismo-{env}-exports` - Relatórios PDF/Excel
- ✅ `eduautismo-{env}-ml-models` - Modelos ML treinados
- ✅ `eduautismo-{env}-bncc-data` - Dados BNCC estáticos

**Lifecycle Policies:**
```hcl
- Exports: 30 dias → Glacier, 90 dias → Delete
- Uploads: 7 dias → IA, 30 dias → Glacier
- ML Models: Versioning habilitado
```

---

## 📊 DIMENSIONAMENTO POR AMBIENTE

### Development
```yaml
RDS:
  Instance: db.t3.micro
  Storage: 20 GB
  Multi-AZ: false
  Backups: 1 dia

ElastiCache:
  Node Type: cache.t3.micro
  Replicas: 0
  Cluster Mode: false

ECS:
  Tasks: 1-2
  CPU: 512
  Memory: 1GB

Custos Estimados: $150-200/mês
```

### Staging
```yaml
RDS:
  Instance: db.t3.small
  Storage: 50 GB
  Multi-AZ: false
  Backups: 3 dias

ElastiCache:
  Node Type: cache.t3.small
  Replicas: 1
  Cluster Mode: false

ECS:
  Tasks: 2-5
  CPU: 1024
  Memory: 2GB

Custos Estimados: $400-500/mês
```

### Production
```yaml
RDS:
  Instance: db.r6g.xlarge
  Storage: 200 GB
  Multi-AZ: true
  Backups: 7 dias
  Read Replicas: 2

ElastiCache:
  Node Type: cache.r6g.large
  Replicas: 2
  Cluster Mode: true (3 shards)

ECS:
  Tasks: 5-20 (auto-scaling)
  CPU: 2048
  Memory: 4GB

WAF: Habilitado
CloudFront: Habilitado

Custos Estimados: $1,500-2,500/mês
```

---

## 🚀 PLANO DE IMPLEMENTAÇÃO

### Fase 1: Cache Layer (Sprint 1) ✅ EM ANDAMENTO
- [ ] Criar módulo `terraform/modules/cache/`
- [ ] Adicionar ElastiCache Redis ao `main.tf`
- [ ] Configurar security groups
- [ ] Adicionar outputs (redis_endpoint)
- [ ] Atualizar variáveis de ambiente ECS

**Estimativa:** 2-3 horas
**Risk Level:** LOW

### Fase 2: Database Optimization (Sprint 2)
- [ ] Atualizar PostgreSQL 14 → 15.4
- [ ] Criar parameter group customizado
- [ ] Adicionar Read Replicas (prod)
- [ ] Habilitar Performance Insights
- [ ] Configurar Enhanced Monitoring

**Estimativa:** 3-4 horas
**Risk Level:** MEDIUM (requer teste de migração)

### Fase 3: Compute Enhancement (Sprint 3)
- [ ] Atualizar task definitions (CPU/Memory)
- [ ] Adicionar variáveis MVP 3.0
- [ ] Configurar auto-scaling avançado
- [ ] Otimizar health checks
- [ ] Adicionar X-Ray integration

**Estimativa:** 2-3 horas
**Risk Level:** LOW

### Fase 4: Monitoring & Observability (Sprint 4)
- [ ] Criar módulo `monitoring/`
- [ ] Configurar CloudWatch Dashboard
- [ ] Adicionar alarmes customizados
- [ ] Integrar Datadog
- [ ] Configurar log aggregation

**Estimativa:** 3-4 horas
**Risk Level:** LOW

### Fase 5: Security & WAF (Sprint 5)
- [ ] Criar módulo `security/`
- [ ] Configurar WAF rules
- [ ] Adicionar rate limiting
- [ ] Configurar geo-blocking
- [ ] Testar DDoS protection

**Estimativa:** 4-5 horas
**Risk Level:** MEDIUM

### Fase 6: Storage Optimization (Sprint 6)
- [ ] Adicionar novos S3 buckets
- [ ] Configurar lifecycle policies
- [ ] Habilitar versioning (ML models)
- [ ] Configurar CORS
- [ ] Adicionar bucket policies

**Estimativa:** 1-2 horas
**Risk Level:** LOW

### Fase 7: Testing & Validation (Sprint 7)
- [ ] Terraform validate
- [ ] Terraform plan (dev)
- [ ] Deploy em dev
- [ ] Smoke tests
- [ ] Load testing

**Estimativa:** 3-4 horas
**Risk Level:** MEDIUM

### Fase 8: Documentation & Rollout (Sprint 8)
- [ ] Atualizar README
- [ ] Criar runbooks
- [ ] Deploy staging
- [ ] Deploy production (blue/green)
- [ ] Monitoramento pós-deploy

**Estimativa:** 2-3 horas
**Risk Level:** LOW

---

## 🔒 SEGURANÇA & COMPLIANCE

### LGPD Compliance
- ✅ Criptografia at rest (RDS, S3, EBS)
- ✅ Criptografia in transit (TLS 1.3)
- ✅ Anonimização de dados (aplicação)
- ✅ Data retention policies
- ✅ Audit logs (CloudTrail)

### Security Best Practices
- ✅ Principle of Least Privilege (IAM)
- ✅ Network segmentation (VPC, Subnets)
- ✅ Security Groups restrictive
- ✅ Secrets Manager (não .env)
- ✅ WAF + Shield Standard

---

## 📈 MÉTRICAS DE SUCESSO

### Performance
- ✅ P95 latency < 500ms
- ✅ Cache hit rate > 80%
- ✅ API availability > 99.9%

### Escalabilidade
- ✅ Suportar 50.000 alunos ativos
- ✅ 1.000+ requests/min
- ✅ Auto-scaling < 2min

### Custos
- ✅ Prod: $1,500-2,500/mês
- ✅ Cost per student: $0.03-0.05/mês

---

## 🔄 ROLLBACK PLAN

Se houver problemas após deploy:

1. **Imediato (< 5min):**
   - Rollback ECS task definition (versão anterior)
   - Desabilitar auto-scaling

2. **Curto Prazo (< 30min):**
   - Terraform state rollback
   - Revert RDS parameter group
   - Desabilitar Redis cache

3. **Longo Prazo (< 2h):**
   - Restore RDS snapshot
   - Rollback completo da infra

---

## 📚 REFERÊNCIAS

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [RDS PostgreSQL Performance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [ElastiCache Redis Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html)

---

**Próximo Passo:** Implementar Fase 1 (Cache Layer)

**Responsável:** DevOps Team
**Reviewer:** @cleybersilva
**Status:** 🚧 Ready for Implementation
