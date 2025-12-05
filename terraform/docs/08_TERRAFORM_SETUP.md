# ✅ Terraform Configuration - EduAutismo IA MVP

## 📦 Arquivos Criados

Este documento resume os arquivos `terraform.tfvars` criados para cada ambiente.

### ✨ Estrutura Criada

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── terraform.tfvars           ✅ Novo
│   │   └── .tfvars.local.example      ✅ Novo
│   ├── staging/
│   │   ├── terraform.tfvars           ✅ Novo
│   │   └── .tfvars.local.example      ✅ Novo
│   ├── production/
│   │   ├── terraform.tfvars           ✅ Novo
│   │   └── .tfvars.local.example      ✅ Novo
│   └── README.md                      ✅ Novo - Guia de Uso
├── backends/
│   ├── backend-dev.tf                 ✅ Novo
│   ├── backend-staging.tf             ✅ Novo
│   ├── backend-production.tf          ✅ Novo
│   └── README.md                      ✅ Novo - Backend Guide
└── scripts/
    └── setup-terraform-env.sh         ✅ Novo - Setup Script
```

---

## 🎯 Configurações por Ambiente

### 1️⃣ Development (Dev)

**Arquivo**: `terraform/environments/dev/terraform.tfvars`

**Características**:
- 🔧 Custo mínimo (~$50/mês)
- ⚡ Setup rápido
- 🎮 Ideal para desenvolvimento local
- 📊 Sem redundância (1 instância)
- 🔐 Sem criptografia (para velocidade)

**Recursos principais**:
```hcl
environment            = "dev"
rds_instance_class     = "db.t3.micro"      # Mais barato
ecs_api_desired_count  = 1                 # 1 instância
redis_num_cache_nodes  = 1                 # 1 nó
s3_lifecycle_enabled   = true
```

**Uso**:
```bash
terraform workspace select dev
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"
```

---

### 2️⃣ Staging (Homologação)

**Arquivo**: `terraform/environments/staging/terraform.tfvars`

**Características**:
- 🔧 Custo moderado (~$500/mês)
- 📊 Realista (Multi-AZ, redundância)
- ✅ Testes antes de production
- 🔐 Criptografia habilitada
- 📈 Auto-scaling (2-4 instâncias)

**Recursos principais**:
```hcl
environment            = "staging"
rds_instance_class     = "db.t3.small"     # Intermediário
rds_multi_az           = true              # HA
ecs_api_desired_count  = 2                 # 2 instâncias
ecs_api_max_capacity   = 4
redis_num_cache_nodes  = 2                 # Redundância
enable_datadog_monitoring = true           # Monitoramento
```

**Uso**:
```bash
terraform workspace select staging
terraform plan -var-file="environments/staging/terraform.tfvars"
terraform apply -var-file="environments/staging/terraform.tfvars"
```

---

### 3️⃣ Production

**Arquivo**: `terraform/environments/production/terraform.tfvars`

**Características**:
- 🚀 Alta disponibilidade (Multi-AZ, Multi-region)
- 🔐 Segurança máxima (Compliance LGPD)
- 💰 Custo premium (~$3000+/mês)
- 📈 Auto-scaling agressivo (3-10 instâncias)
- 🛡️ WAF + DDoS Protection
- 🔄 Backup cross-region
- 📊 Monitoramento completo

**Recursos principais**:
```hcl
environment            = "production"
rds_instance_class     = "db.r5.large"    # Performance otimizada
rds_multi_az           = true
ecs_api_desired_count  = 3                # 3 instâncias mínimas
ecs_api_max_capacity   = 10               # Auto-scaling agressivo
redis_num_cache_nodes  = 3                # Alta redundância
enable_cloudfront      = true             # CDN global
enable_waf             = true             # Web Application Firewall
enable_aws_shield_advanced = true         # DDoS Protection
```

**Uso**:
```bash
terraform workspace select production
terraform plan -var-file="environments/production/terraform.tfvars" -out=plan.prod

# ⚠️ REVIEW CRÍTICO antes de aplicar
terraform show plan.prod

# Aplicar com cuidado
terraform apply plan.prod
```

---

## 🚀 Quick Start

### 1. Setup Inicial

```bash
# Clonar/navegar para repo
cd eduautismo-ia-mvp

# Instalar Terraform (se necessário)
# https://www.terraform.io/downloads

# Configurar AWS credentials
aws configure
```

### 2. Deploy em Dev

```bash
cd terraform

# Initialize
terraform init

# Criar/selecionar workspace
terraform workspace new dev || terraform workspace select dev

# Plan
terraform plan -var-file="environments/dev/terraform.tfvars"

# Apply
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### 3. Deploy em Staging

```bash
terraform workspace new staging || terraform workspace select staging
terraform plan -var-file="environments/staging/terraform.tfvars"
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### 4. Deploy em Production

```bash
# ⚠️ CUIDADO - NUNCA fazer apply sem review
terraform workspace new production || terraform workspace select production

# Plan com output para arquivo
terraform plan -var-file="environments/production/terraform.tfvars" \
  -out=plan.production

# Review detalhado
terraform show plan.production

# Apenas depois de tudo validado:
terraform apply plan.production
```

---

## 📋 Variáveis Principais

Todas as variáveis estão documentadas em `terraform/variables.tf`:

### Globais
```hcl
aws_region = "us-east-1"           # Região AWS
project_name = "eduautismo-ia"     # Nome do projeto
environment = "dev|staging|prod"   # Ambiente
```

### RDS (PostgreSQL)
```hcl
rds_instance_class = "db.t3.micro"  # Tipo de instância
rds_allocated_storage = 20          # Storage em GB
rds_multi_az = false                # Multi-AZ para HA
rds_backup_retention_period = 7     # Dias de backup
```

### ECS (Compute)
```hcl
ecs_api_desired_count = 1           # Instâncias desejadas
ecs_api_task_cpu = 256              # CPU em MB
ecs_api_task_memory = 512           # Memória em MB
ecs_api_max_capacity = 4            # Max para auto-scaling
```

### Redis (Cache)
```hcl
redis_num_cache_nodes = 1           # Número de nós
redis_node_type = "cache.t3.micro"  # Tipo de nó
```

### Security
```hcl
enable_rds_encryption = true        # Criptografia RDS
enable_s3_encryption = true         # Criptografia S3
enable_waf = true                   # Web Application Firewall
```

---

## 🔐 Segurança

### Senhas e Credenciais
- ❌ NUNCA colocar em `.tfvars` arquivos versionados
- ✅ Usar AWS Secrets Manager
- ✅ Usar AWS Systems Manager Parameter Store
- ✅ Usar arquivos `.tfvars.local` com `.gitignore`

### Exemplo - Secrets Manager
```bash
# Criar secret
aws secretsmanager create-secret \
  --name eduautismo-ia/prod/database/password \
  --secret-string "senha_super_secreta"

# Referenciar no Terraform
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "eduautismo-ia/prod/database/password"
}
```

### .gitignore
Adicione ao `.gitignore`:
```
*.tfvars.local
*.tfvars.secret
**/*.tfstate
**/*.tfstate.*
.terraform.lock.hcl
```

---

## 📊 Comparativo de Ambientes

| Aspecto | Dev | Staging | Production |
|---------|-----|---------|------------|
| **RDS Instance** | t3.micro | t3.small | r5.large |
| **RDS Storage** | 20 GB | 100 GB | 500 GB |
| **Multi-AZ** | ❌ | ✅ | ✅ |
| **ECS Instâncias** | 1 | 2 | 3-10 |
| **Redis Nodes** | 1 | 2 | 3 |
| **Auto-scaling** | ❌ | ✅ | ✅ |
| **Criptografia** | ❌ | ✅ | ✅ |
| **WAF** | ❌ | ✅ | ✅ |
| **CDN** | ❌ | ❌ | ✅ |
| **DDoS Shield** | ❌ | ❌ | ✅ |
| **Monitoramento** | ❌ | ✅ | ✅ |
| **Custo/mês** | ~$50 | ~$500 | ~$3000+ |

---

## 🛠️ Comandos Úteis

### Planning e Applying
```bash
# Plan sem aplicar
terraform plan -var-file="environments/dev/terraform.tfvars"

# Plan e salvar
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan

# Apply específico
terraform apply -var-file="environments/dev/terraform.tfvars"

# Destroy (CUIDADO!)
terraform destroy -var-file="environments/dev/terraform.tfvars"
```

### State Management
```bash
# Listar workspaces
terraform workspace list

# Selecionar workspace
terraform workspace select dev

# Listar recursos
terraform state list

# Ver detalhe de recurso
terraform state show aws_db_instance.main

# Remover recurso do state (não deleta recurso na AWS)
terraform state rm aws_instance.example
```

### Debugging
```bash
# Validar sintaxe
terraform validate -var-file="environments/dev/terraform.tfvars"

# Ver formato JSON
terraform show -json > state.json

# Taint recurso (força recriação)
terraform taint aws_db_instance.main

# Inspect log
terraform console
```

---

## 📈 Scaling

### Dev → Staging
```bash
# Quando pronto para testar:
terraform workspace select staging
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### Staging → Production
```bash
# Depois de validar em staging:
terraform workspace select production

# Plan com cuidado
terraform plan -var-file="environments/production/terraform.tfvars" -out=plan.prod

# Review
terraform show plan.prod | less

# Apply
terraform apply plan.prod
```

---

## 🐛 Troubleshooting

### Erro: "InvalidParameterCombination"
```bash
# Verificar valores de variáveis
terraform console -var-file="environments/dev/terraform.tfvars"
# > var.rds_instance_class
# > var.rds_allocated_storage
```

### Erro: "AWS credentials not found"
```bash
# Configurar credenciais
aws configure

# Ou usar profile
export AWS_PROFILE=seu_profile
terraform plan
```

### Erro: "State already exists"
```bash
# Selecionar workspace existente
terraform workspace select dev
```

---

## 📚 Referências

- [Terraform Variables](https://www.terraform.io/docs/language/values/variables.html)
- [Terraform Workspaces](https://www.terraform.io/docs/state/workspaces.html)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [EduAutismo IA - CLAUDE.md](../CLAUDE.md)

---

## ✅ Checklist de Deployment

### Antes de Dev
- [ ] Terraform instalado
- [ ] AWS credentials configuradas
- [ ] Arquivo `dev/terraform.tfvars` criado

### Antes de Staging
- [ ] Dev testado completamente
- [ ] Staging tfvars validado
- [ ] DNS registrado
- [ ] SSL certificate válido

### Antes de Production
- [ ] Staging em execução há 24h+
- [ ] Production tfvars revisado
- [ ] Security audit realizado
- [ ] LGPD compliance checklist
- [ ] Backup/DR plan documentado
- [ ] Team notificado
- [ ] Rollback plan criado

---

**Última atualização**: 15 de janeiro de 2025  
**Versão**: 1.0.0  
**Status**: ✅ Pronto para Deploy
