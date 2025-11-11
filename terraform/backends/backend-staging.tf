# ============================================================================
# terraform/backends/backend-staging.tf
# ============================================================================
# Configuração de backend para workspace de staging
# State armazenado remotamente em S3 com DynamoDB lock
#
# Pré-requisitos:
#   - S3 bucket: eduautismo-ia-terraform-staging
#   - DynamoDB table: eduautismo-ia-terraform-lock-staging
#
# Para usar este backend:
#   1. Descomente as linhas abaixo
#   2. Execute: terraform init -reconfigure
#   3. Escolha 'yes' para migrar state

# terraform {
#   backend "s3" {
#     bucket         = "eduautismo-ia-terraform-staging"
#     key            = "staging/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "eduautismo-ia-terraform-lock-staging"
#   }
# }

# Alternativa: Local backend (não recomendado para production)
terraform {
  backend "local" {
    path = "terraform/workspaces/staging/terraform.tfstate"
  }
}
