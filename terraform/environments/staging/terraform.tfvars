# ============================================================================
# terraform.tfvars - Staging Environment
# ============================================================================
# Configuração para ambiente de staging/teste
# Prioridades: Realismo com custo moderado, Confiabilidade
# ============================================================================

# Configurações Globais
aws_region   = "us-east-1"
project_name = "eduautismo-ia"
environment  = "staging"

# ============================================================================
# Rede (VPC)
# ============================================================================
# Configuração intermediária com múltiplas zonas de disponibilidade
vpc_cidr = "10.1.0.0/16"

# ============================================================================
# Banco de Dados RDS (PostgreSQL)
# ============================================================================
# Instância média para simular ambiente de produção
rds_instance_class = "db.t3.small"

# Configurações adicionais para RDS (staging)
rds_allocated_storage           = 100  # 100 GB
rds_max_allocated_storage       = 200  # Auto-scaling até 200 GB
rds_backup_retention_period     = 14   # 14 dias de backup
rds_multi_az                    = true   # Multi-AZ para HA testing
rds_deletion_protection         = true   # Proteger dados em staging
rds_enable_cloudwatch_logs      = true   # Para monitoramento
rds_enable_enhanced_monitoring  = true   # Enhanced monitoring

# ============================================================================
# Banco de Dados MongoDB (DocumentDB - via AWS)
# ============================================================================
# Habilitado para testar ambiente real
enable_documentdb              = true
documentdb_instance_class      = "db.t3.medium"
documentdb_num_instances       = 2      # Multi-node cluster
documentdb_backup_retention    = 14

# ============================================================================
# Cache Redis (ElastiCache) - MVP 3.0
# ============================================================================
# Instância média com redundância
redis_engine_version = "7.0"
redis_node_type      = "cache.t3.small"
redis_num_cache_nodes = 2  # 2 nós para redundância

# MVP 3.0 - Security & Encryption
redis_at_rest_encryption_enabled = true   # Criptografia at rest
redis_transit_encryption_enabled = true   # Criptografia in transit (TLS)
redis_auth_token_enabled         = true   # Auth token habilitado

# MVP 3.0 - High Availability
redis_automatic_failover_enabled = true   # Failover automático
redis_multi_az_enabled           = true   # Multi-AZ para HA

# MVP 3.0 - Backups
redis_snapshot_retention_limit = 5  # 5 dias de snapshots

# ============================================================================
# Computação (ECS Fargate)
# ============================================================================
# Configuração intermediária com auto-scaling
ecs_container_insights = true

# Task Definition - API Backend
ecs_api_task_cpu    = 512   # 512 MB
ecs_api_task_memory = 1024  # 1 GB

ecs_api_desired_count = 2  # 2 instâncias para HA

# Container
ecs_api_container_port  = 8000
ecs_api_container_image = "eduautismo-ia/api:staging"

# Auto Scaling
ecs_api_max_capacity = 4
ecs_api_min_capacity = 2

# ============================================================================
# Storage S3
# ============================================================================
s3_lifecycle_enabled = true

# Lifecycle Rules para staging
s3_transition_days_to_standard_ia = 45   # Move para IA após 45 dias
s3_transition_days_to_glacier     = 120  # Move para Glacier após 120 dias
s3_expiration_days                = 365  # Deleta após 1 ano

# ============================================================================
# Load Balancer
# ============================================================================
# ALB com health checks rigorosos
enable_alb                      = true
alb_enable_access_logs          = true
alb_health_check_healthy_count  = 2
alb_health_check_unhealthy_count = 3

# ============================================================================
# Logging e Monitoring
# ============================================================================
cloudwatch_log_retention_days = 30  # Manter por 30 dias
enable_datadog_monitoring     = true  # Ativar monitoramento Datadog

# ============================================================================
# Security & Encryption
# ============================================================================
enable_rds_encryption          = true   # Criptografia em repouso
enable_s3_encryption           = true   # Server-side encryption S3
enable_efs_encryption          = true   # EFS encryption

# ============================================================================
# WAF (Web Application Firewall)
# ============================================================================
enable_waf = true

# ============================================================================
# Backup e Disaster Recovery
# ============================================================================
enable_backup_vault      = true
backup_retention_days    = 30

# ============================================================================
# Tags comuns para todos os recursos
# ============================================================================
tags = {
  Environment = "staging"
  Project     = "EduAutismo-IA"
  ManagedBy   = "Terraform"
  CostCenter  = "Staging"
  CreatedAt   = "2025-01-15"
}
