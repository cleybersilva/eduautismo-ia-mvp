# ============================================================================
# terraform/backends/README.md
# ============================================================================
# Backend Configuration Guide

## 📋 Overview

O backend do Terraform armazena o `terraform.tfstate` (estado da infraestrutura).

### Configurações por Ambiente

| Ambiente | Backend | Storage | Replicação | Lock |
|----------|---------|---------|------------|------|
| **Dev** | Local | `terraform/workspaces/dev/` | ❌ | ❌ |
| **Staging** | S3 | `s3://bucket-staging/` | ❌ | DynamoDB |
| **Production** | S3 | `s3://bucket-prod/` | ✅ Cross-region | DynamoDB |

---

## 🚀 Setup Inicial

### 1. Development (Local)

```bash
# Não requer setup - funciona automaticamente
terraform init
```

### 2. Staging (S3 Backend)

```bash
# Criar recursos de backend (uma única vez)
./scripts/setup-backend-staging.sh

# Migrar state para S3
cd terraform
terraform init -reconfigure
# Responda 'yes' para migrar
```

### 3. Production (S3 Backend + Replicação)

```bash
# Criar recursos de backend (uma única vez)
./scripts/setup-backend-production.sh

# Migrar state para S3
cd terraform
terraform init -reconfigure
# Responda 'yes' para migrar
```

---

## 📝 Estrutura de Arquivos

```
terraform/
├── backends/
│   ├── README.md              # Este arquivo
│   ├── backend-dev.tf         # Config local
│   ├── backend-staging.tf     # Config S3 staging
│   └── backend-production.tf  # Config S3 production
└── workspaces/
    ├── dev/
    │   └── terraform.tfstate  # State local (dev)
    ├── staging/
    │   └── terraform.tfstate  # Pode estar aqui ou em S3
    └── production/
        └── terraform.tfstate  # Deve estar em S3
```

---

## 🔄 Migração de Backend

### Cenário: Mover de Local para S3 (Staging)

```bash
# 1. Atualize backend-staging.tf (descomente S3 config)
# 2. Execute init com reconfigure
terraform init -reconfigure

# 3. Terraform detectará diferença entre backends
# 4. Responda 'yes' para copiar state
# 5. Verifique que state foi migrado
terraform state list
```

### Cenário: Mudar bucket S3

```bash
# 1. Crie novo bucket
aws s3 mb s3://novo-bucket-terraform

# 2. Copie state antigo para novo
aws s3 cp s3://antigo-bucket/terraform.tfstate \
         s3://novo-bucket/terraform.tfstate

# 3. Atualize backend-*.tf com novo bucket
# 4. Execute terraform init -reconfigure
```

---

## 🔒 Segurança do State

### Não faça:
- ❌ Commitar `terraform.tfstate` no Git
- ❌ Compartilhar state file por email
- ❌ Usar backend local em produção
- ❌ Deixar S3 bucket público

### Faça:
- ✅ Adicionar `*.tfstate` ao `.gitignore`
- ✅ Usar S3 com versioning + encryption
- ✅ Usar DynamoDB para state locking
- ✅ Habilitar MFA delete no S3 (prod)
- ✅ Auditar access logs

---

## 🚨 Disaster Recovery

### Backup automático (Production)

```bash
# State é replicado cross-region automaticamente
# Para restaurar:

# 1. Listar versões do object
aws s3api list-object-versions \
  --bucket eduautismo-ia-terraform-production \
  --prefix production/terraform.tfstate

# 2. Restaurar versão específica
aws s3api get-object \
  --bucket eduautismo-ia-terraform-production \
  --key production/terraform.tfstate \
  --version-id <VERSION_ID> \
  terraform.tfstate.backup
```

### Recovery de região

```bash
# Se região principal falhar, restaurar do backup:

# 1. Restore do bucket replicado
aws s3 cp \
  s3://eduautismo-ia-terraform-production-backup/production/terraform.tfstate \
  s3://eduautismo-ia-terraform-production-restored/terraform.tfstate

# 2. Atualize backend para apontar nova localização
# 3. Execute terraform init -reconfigure
```

---

## 📊 Monitoramento

### Verificar lock status

```bash
# DynamoDB locks (se travado)
aws dynamodb scan \
  --table-name eduautismo-ia-terraform-lock-production

# Remover lock travado (com cuidado!)
aws dynamodb delete-item \
  --table-name eduautismo-ia-terraform-lock-production \
  --key '{"LockID":{"S":"<lock-id>"}}'
```

### Auditoria de mudanças

```bash
# Ver histórico de versions do state
aws s3api list-object-versions \
  --bucket eduautismo-ia-terraform-production

# Comparar versões
aws s3api get-object \
  --bucket eduautismo-ia-terraform-production \
  --key production/terraform.tfstate \
  --version-id <V1> state-v1.json

aws s3api get-object \
  --bucket eduautismo-ia-terraform-production \
  --key production/terraform.tfstate \
  --version-id <V2> state-v2.json

diff state-v1.json state-v2.json
```

---

## 🧹 Limpeza

### Remover state local (Dev)

```bash
# Se não precisar mais de dev local
rm -rf terraform/workspaces/dev/terraform.tfstate*
```

### Arquivar estado antigo

```bash
# Fazer backup antes de deletar
aws s3 cp \
  s3://bucket/terraform.tfstate \
  ./archives/terraform.tfstate.backup.$(date +%Y%m%d)
```

---

## 📚 Referências

- [Terraform Backends](https://www.terraform.io/docs/backends)
- [S3 Backend](https://www.terraform.io/docs/backends/types/s3)
- [State Locking](https://www.terraform.io/docs/state/locking)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/BestPractices.html)

---

**Última atualização**: 2025-01-15
