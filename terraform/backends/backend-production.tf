# ============================================================================
# terraform/backends/backend-production.tf
# ============================================================================
# Configuração de backend para workspace de produção
# State DEVE ser armazenado remotamente em S3 com DynamoDB lock
# Replicação cross-region para disaster recovery
#
# Pré-requisitos CRÍTICOS:
#   - S3 bucket: eduautismo-ia-terraform-production (versioning habilitado)
#   - S3 replication para: eduautismo-ia-terraform-production-backup
#   - DynamoDB table: eduautismo-ia-terraform-lock-production
#   - Criptografia KMS habilitada
#   - Logging habilitado
#
# Para usar este backend:
#   1. Descomente as linhas abaixo
#   2. Execute: terraform init -reconfigure
#   3. Escolha 'yes' para migrar state
#
# ⚠️  NUNCA use local backend em production!

terraform {
  backend "s3" {
    bucket         = "eduautismo-ia-terraform-production"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "eduautismo-ia-terraform-lock-production"
    
    # Configurações adicionais de segurança
    # skip_credentials_validation = false
    # skip_region_validation      = false
  }
}

# ============================================================================
# Script para criar recursos de backend (rodas uma única vez)
# ============================================================================
# 
# # Criar S3 bucket com versioning
# aws s3api create-bucket \
#   --bucket eduautismo-ia-terraform-production \
#   --region us-east-1 \
#   --acl private
#
# # Habilitar versionamento
# aws s3api put-bucket-versioning \
#   --bucket eduautismo-ia-terraform-production \
#   --versioning-configuration Status=Enabled
#
# # Habilitar encriptação
# aws s3api put-bucket-encryption \
#   --bucket eduautismo-ia-terraform-production \
#   --server-side-encryption-configuration '{
#     "Rules": [{
#       "ApplyServerSideEncryptionByDefault": {
#         "SSEAlgorithm": "AES256"
#       }
#     }]
#   }'
#
# # Habilitar logging
# aws s3api put-bucket-logging \
#   --bucket eduautismo-ia-terraform-production \
#   --bucket-logging-status '{
#     "LoggingEnabled": {
#       "TargetBucket": "eduautismo-ia-terraform-logs",
#       "TargetPrefix": "production/"
#     }
#   }'
#
# # Bloquear public access
# aws s3api put-public-access-block \
#   --bucket eduautismo-ia-terraform-production \
#   --public-access-block-configuration \
#   "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
#
# # Criar tabela DynamoDB para lock
# aws dynamodb create-table \
#   --table-name eduautismo-ia-terraform-lock-production \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
#   --region us-east-1
#
# # Habilitar Point-in-Time Recovery (PITR) na tabela
# aws dynamodb update-continuous-backups \
#   --table-name eduautismo-ia-terraform-lock-production \
#   --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
#   --region us-east-1
