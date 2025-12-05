# Terraform - Referência Rápida

## 🚀 Deploy em 5 Minutos

### Dev
```bash
cd terraform
terraform workspace select dev || terraform workspace new dev
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### Staging
```bash
cd terraform
terraform workspace select staging || terraform workspace new staging
terraform init
terraform plan -var-file="environments/staging/terraform.tfvars"
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### Production
```bash
cd terraform
terraform workspace select production || terraform workspace new production
terraform init
terraform plan -var-file="environments/production/terraform.tfvars" -out=plan.prod
terraform show plan.prod    # REVIEW CRÍTICO
terraform apply plan.prod
```

---

## 📋 Arquivos

| Caminho | Tamanho | Ambiente | Descrição |
|---------|--------|----------|-----------|
| `environments/dev/terraform.tfvars` | ~100 linhas | Dev | Mínimo custo, 1 instância |
| `environments/staging/terraform.tfvars` | ~150 linhas | Staging | HA, 2-4 instâncias |
| `environments/production/terraform.tfvars` | ~250 linhas | Prod | HA, 3-10 instâncias, LGPD |

---

## 🔑 Variáveis Principais

```
# Globais (todos ambientes)
aws_region = "us-east-1"
project_name = "eduautismo-ia"
environment = "dev|staging|production"

# RDS - Diferente por ambiente
rds_instance_class = "db.t3.micro" (dev) / "db.t3.small" (staging) / "db.r5.large" (prod)
rds_multi_az = false (dev) / true (staging/prod)

# ECS - Diferente por ambiente
ecs_api_desired_count = 1 (dev) / 2 (staging) / 3 (prod)
ecs_api_max_capacity = 1 (dev) / 4 (staging) / 10 (prod)

# Security - Diferente por ambiente
enable_rds_encryption = false (dev) / true (staging/prod)
enable_waf = false (dev) / true (staging/prod)
```

---

## 📊 Comparação Rápida

| Recurso | Dev | Staging | Prod |
|---------|-----|---------|------|
| RDS | t3.micro | t3.small | r5.large |
| Multi-AZ | ❌ | ✅ | ✅ |
| ECS Instâncias | 1 | 2 | 3-10 |
| Redis Nós | 1 | 2 | 3 |
| Backup (dias) | 7 | 14 | 30-90 |
| Custo/mês | ~$50 | ~$500 | ~$3000+ |

---

## 🛠️ Comandos Essenciais

```bash
# Plan
terraform plan -var-file="environments/dev/terraform.tfvars"

# Apply
terraform apply -var-file="environments/dev/terraform.tfvars"

# Destroy
terraform destroy -var-file="environments/dev/terraform.tfvars"

# State
terraform state list
terraform state show 'resource_type.name'

# Workspaces
terraform workspace list
terraform workspace select dev
```

---

## 🔐 Segurança

- ❌ Nunca commitar `.tfvars.local` ou segredos
- ✅ Usar AWS Secrets Manager para credenciais
- ✅ Usar S3 backend em staging/prod
- ✅ Habilitar state locking com DynamoDB

---

## 📚 Documentação Completa

- `terraform/environments/README.md` - Guia de Ambientes
- `terraform/TERRAFORM_SETUP.md` - Setup Completo
- `terraform/backends/README.md` - Backend Configuration
- `terraform/environments/INDEX.md` - Índice de Arquivos
