# ============================================================================
# terraform/backends/backend-dev.tf
# ============================================================================
# Configuração de backend para workspace de desenvolvimento
# State armazenado localmente (pode mudar para S3 depois)

terraform {
  backend "local" {
    path = "terraform/workspaces/dev/terraform.tfstate"
  }
}
