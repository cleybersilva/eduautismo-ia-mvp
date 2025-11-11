# 📊 Índice de Arquivos Terraform Criados

## 🎯 Resumo

Este documento indexa todos os arquivos `terraform.tfvars` e documentação criada para o projeto EduAutismo IA MVP.

---

## 📁 Estrutura de Ambientes

### Development (Dev)
```
terraform/environments/dev/
├── terraform.tfvars              (Main config - ~100 linhas)
└── .tfvars.local.example         (Template para local overrides)
```

**Variáveis principais**:
- `aws_region = "us-east-1"`
- `rds_instance_class = "db.t3.micro"`
- `ecs_api_desired_count = 1`
- `enable_rds_encryption = false` (desabilitada para velocidade)
- **Custo estimado**: ~$50/mês

**Arquivo**: [`terraform/environments/dev/terraform.tfvars`](./dev/terraform.tfvars)

---

### Staging (Homologação)
```
terraform/environments/staging/
├── terraform.tfvars              (Main config - ~150 linhas)
└── .tfvars.local.example         (Template para local overrides)
```

**Variáveis principais**:
- `aws_region = "us-east-1"`
- `rds_instance_class = "db.t3.small"`
- `rds_multi_az = true`
- `ecs_api_desired_count = 2`
- `ecs_api_max_capacity = 4`
- `enable_rds_encryption = true`
- `enable_datadog_monitoring = true`
- **Custo estimado**: ~$500/mês

**Arquivo**: [`terraform/environments/staging/terraform.tfvars`](./staging/terraform.tfvars)

---

### Production
```
terraform/environments/production/
├── terraform.tfvars              (Main config - ~250+ linhas)
└── .tfvars.local.example         (Template para local overrides)
```

**Variáveis principais**:
- `aws_region = "us-east-1"`
- `rds_instance_class = "db.r5.large"`
- `rds_multi_az = true`
- `ecs_api_desired_count = 3`
- `ecs_api_max_capacity = 10`
- `enable_rds_encryption = true`
- `enable_cloudfront = true`
- `enable_waf = true`
- `enable_aws_shield_advanced = true`
- `enable_backup_replication = true`
- **Custo estimado**: ~$3000+/mês

**Arquivo**: [`terraform/environments/production/terraform.tfvars`](./production/terraform.tfvars)

---

## 📚 Documentação

### 1. Guia de Ambientes
**Arquivo**: [`terraform/environments/README.md`](./README.md)

**Conteúdo**:
- ✅ Como usar cada ambiente
- ✅ Workflow de deployment
- ✅ Checklist de pre-requisitos
- ✅ Troubleshooting comum
- ✅ Comparativo de recursos e custos

**Para ler**: `terraform/environments/README.md`

---

### 2. Configuração de Backend
**Arquivo**: [`terraform/backends/README.md`](../backends/README.md)

**Conteúdo**:
- ✅ Explicação de Terraform backends
- ✅ Setup S3 + DynamoDB
- ✅ State locking
- ✅ Disaster recovery
- ✅ Auditoria de mudanças

**Para ler**: `terraform/backends/README.md`

---

### 3. Setup Principal
**Arquivo**: [`terraform/TERRAFORM_SETUP.md`](../TERRAFORM_SETUP.md)

**Conteúdo**:
- ✅ Quick start guide
- ✅ Detalhes de cada ambiente
- ✅ Variáveis principais
- ✅ Segurança e secrets
- ✅ Comandos úteis
- ✅ Troubleshooting

**Para ler**: `terraform/TERRAFORM_SETUP.md`

---

### 4. Script de Setup
**Arquivo**: [`scripts/setup-terraform-env.sh`](../../scripts/setup-terraform-env.sh)

**Funcionalidade**:
- ✅ Valida pré-requisitos (Terraform, AWS CLI)
- ✅ Verifica credenciais AWS
- ✅ Cria workspace
- ✅ Valida sintaxe Terraform
- ✅ Gera preview do plan

**Como usar**:
```bash
bash scripts/setup-terraform-env.sh dev
bash scripts/setup-terraform-env.sh staging
bash scripts/setup-terraform-env.sh production
```

---

## 🚀 Quick Start

### 1. Setup Dev
```bash
# Setup automático com script
bash scripts/setup-terraform-env.sh dev

# Ou manual
cd terraform
terraform workspace select dev
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
```

### 2. Deploy Dev
```bash
cd terraform
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### 3. Setup Staging (Depois de Dev OK)
```bash
bash scripts/setup-terraform-env.sh staging
cd terraform
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### 4. Deploy Production (Depois de Staging OK)
```bash
bash scripts/setup-terraform-env.sh production
cd terraform

# PLAN COM CUIDADO
terraform plan -var-file="environments/production/terraform.tfvars" -out=plan.prod

# REVIEW
terraform show plan.prod

# APPLY (após aprovação)
terraform apply plan.prod
```

---

## 📊 Mapa de Variáveis

| Variável | Dev | Staging | Prod |
|----------|-----|---------|------|
| `aws_region` | us-east-1 | us-east-1 | us-east-1 |
| `environment` | dev | staging | production |
| `rds_instance_class` | t3.micro | t3.small | r5.large |
| `rds_allocated_storage` | 20 GB | 100 GB | 500 GB |
| `rds_multi_az` | false | true | true |
| `ecs_api_desired_count` | 1 | 2 | 3 |
| `ecs_api_max_capacity` | 1 | 4 | 10 |
| `redis_num_cache_nodes` | 1 | 2 | 3 |
| `enable_rds_encryption` | false | true | true |
| `enable_waf` | false | true | true |
| `enable_cloudfront` | false | false | true |
| `cloudwatch_log_retention_days` | 7 | 30 | 90 |

---

## 🔐 Variáveis de Segurança

Todas as configurações de segurança estão em `terraform/variables.tf`:

```hcl
# Definições padrão
variable "enable_rds_encryption" {
  default = false  # Override por ambiente
}

variable "enable_s3_encryption" {
  default = false
}

variable "enable_waf" {
  default = false
}
```

**Sobrescrita por ambiente** em `terraform.tfvars`:
```
enable_rds_encryption = true   # Habilita em staging/prod
enable_waf = true
```

---

## 📝 Arquivos de Suporte

### Backend Configuration
```
terraform/backends/
├── backend-dev.tf              (Local backend)
├── backend-staging.tf          (S3 backend com comentários)
├── backend-production.tf       (S3 + Replicação)
└── README.md                   (Backend guide)
```

---

## ✅ Checklist de Uso

### Primeiro Deploy (Dev)
- [ ] Terraform instalado (`terraform --version`)
- [ ] AWS CLI configurado (`aws configure`)
- [ ] Git clone do projeto
- [ ] Executado `terraform init`
- [ ] Lido `terraform/environments/README.md`
- [ ] Executado `bash scripts/setup-terraform-env.sh dev`
- [ ] Revisado output de `terraform plan`
- [ ] Aplicado com `terraform apply`

### Deploy em Staging
- [ ] Dev rodando com sucesso há 24h+
- [ ] Testes passando
- [ ] Lido `terraform/TERRAFORM_SETUP.md`
- [ ] Executado `bash scripts/setup-terraform-env.sh staging`
- [ ] Revisado arquivo `staging/terraform.tfvars`
- [ ] Dados de teste preparados
- [ ] DNS/SSL configurado
- [ ] Monitoramento testado

### Deploy em Production
- [ ] ✅ Staging validado completamente
- [ ] ✅ Backup/DR plan documentado
- [ ] ✅ Security audit concluído
- [ ] ✅ LGPD compliance checklist
- [ ] ✅ Aprovação stakeholder
- [ ] ✅ On-call team notificado
- [ ] ✅ Rollback plan preparado
- [ ] ✅ Review final de `production/terraform.tfvars`
- [ ] ✅ Plan saved to `plan.production`
- [ ] ✅ Múltiplas revisões do plano
- [ ] ✅ Apply executado

---

## 🎓 Recursos Educacionais

### Sobre Terraform
- [Terraform Official Docs](https://www.terraform.io/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest)

### Sobre AWS
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/best_practices.html)

### Sobre LGPD
- [LGPD Official (português)](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [AWS e LGPD](https://aws.amazon.com/pt/compliance/lgpd/)

---

## 🔗 Links Rápidos

| Arquivo | Descrição | Link |
|---------|-----------|------|
| Dev tfvars | Configuração desenvolvimento | `environments/dev/terraform.tfvars` |
| Staging tfvars | Configuração teste | `environments/staging/terraform.tfvars` |
| Prod tfvars | Configuração produção | `environments/production/terraform.tfvars` |
| Env README | Guia de ambientes | `environments/README.md` |
| Terraform Setup | Setup principal | `../TERRAFORM_SETUP.md` |
| Backend Guide | Backend configuration | `../backends/README.md` |
| Setup Script | Script automático | `../../scripts/setup-terraform-env.sh` |

---

## 📞 Suporte e Troubleshooting

### Erro Comum: "Invalid variable value"
**Solução**: Verificar arquivo `terraform.tfvars` - valores devem estar entre aspas

### Erro: "AWS credentials not found"
**Solução**: Executar `aws configure` e reconfigurar credenciais

### Erro: "Terraform state lock"
**Solução**: Ver `backends/README.md` - seção "Remover lock travado"

### Erro: "Plan tem 100+ mudanças"
**Solução**: STOP! Revisar detalhes em `terraform show plan.prod | less`

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Arquivos tfvars | 3 (dev, staging, prod) |
| Arquivos de documentação | 4 |
| Scripts | 1 |
| Linhas de código Terraform | ~600+ |
| Variáveis configuráveis | 40+ |
| Ambientes suportados | 3 |

---

**Criado em**: 15 de janeiro de 2025  
**Versão**: 1.0.0  
**Status**: ✅ Completo e Pronto para Uso
