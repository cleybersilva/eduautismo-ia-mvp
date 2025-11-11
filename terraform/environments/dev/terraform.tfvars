# ============================================================================
# terraform.tfvars - Development Environment
# ============================================================================
# Configuração para ambiente de desenvolvimento
# Prioridades: Custo mínimo, Rapidez de deployment
# ============================================================================

# Configurações Globais
aws_region   = "us-east-1"
project_name = "eduautismo-ia"
environment  = "dev"

# ============================================================================
# Rede (VPC)
# ============================================================================
# Configuração simples com menos subnets e zonas de disponibilidade
vpc_cidr = "10.0.0.0/16"

# ============================================================================
# Banco de Dados RDS (PostgreSQL)
# ============================================================================
# Instância pequena e otimizada para desenvolvimento
rds_instance_class = "db.t3.micro"

# Configurações adicionais para RDS (dev)
rds_allocated_storage           = 20  # 20 GB
rds_max_allocated_storage       = 50  # Auto-scaling até 50 GB
rds_backup_retention_period     = 7   # 7 dias de backup
rds_multi_az                    = false  # Sem multi-AZ em dev
rds_deletion_protection         = false  # Facilita limpeza em dev
rds_enable_cloudwatch_logs      = true   # Para debug

# ============================================================================
# Banco de Dados MongoDB (DocumentDB - via AWS)
# ============================================================================
# Desabilitado em dev - usar emulador local se necessário
enable_documentdb = false

# ============================================================================
# Cache Redis (ElastiCache)
# ============================================================================
# Instância pequena para desenvolvimento
redis_engine_version = "7.0"
redis_node_type      = "cache.t3.micro"
redis_num_cache_nodes = 1  # Nó único em dev

# ============================================================================
# Computação (ECS Fargate)
# ============================================================================
# Configuração mínima para dev
ecs_container_insights = true

# Task Definition - API Backend
ecs_api_task_cpu    = 256   # 256 MB - Mínimo para Fargate
ecs_api_task_memory = 512   # 512 MB

ecs_api_desired_count = 1  # 1 instância em dev

# Container
ecs_api_container_port = 8000
ecs_api_container_image = "eduautismo-ia/api:latest"  # Local dev image

# ============================================================================
# Storage S3
# ============================================================================
s3_lifecycle_enabled = true

# Lifecycle Rules para dev
s3_transition_days_to_standard_ia = 30  # Move para IA após 30 dias
s3_transition_days_to_glacier     = 90  # Move para Glacier após 90 dias
s3_expiration_days                = 180 # Deleta após 180 dias

# ============================================================================
# Logging e Monitoring
# ============================================================================
cloudwatch_log_retention_days = 7  # Manter por 7 dias
enable_datadog_monitoring     = false  # Não usar em dev

# ============================================================================
# Security & Encryption
# ============================================================================
enable_rds_encryption          = false  # Sem criptografia em dev (mais rápido)
enable_s3_encryption           = false  # Sem criptografia em dev
enable_efs_encryption          = false  # Sem criptografia em dev

# ============================================================================
# Tags comuns para todos os recursos
# ============================================================================
tags = {
  Environment = "development"
  Project     = "EduAutismo-IA"
  ManagedBy   = "Terraform"
  CostCenter  = "Dev"
  CreatedAt   = "2025-01-15"
}
