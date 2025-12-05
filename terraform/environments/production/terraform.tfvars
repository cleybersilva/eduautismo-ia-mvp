# ============================================================================
# terraform.tfvars - Production Environment
# ============================================================================
# Configuração para ambiente de produção
# Prioridades: Alta disponibilidade, Segurança, Performance, Compliance (LGPD)
# ============================================================================

# Configurações Globais
aws_region   = "us-east-1"
project_name = "eduautismo-ia"
environment  = "production"

# ============================================================================
# Rede (VPC)
# ============================================================================
# Configuração robusta com múltiplas zonas de disponibilidade
vpc_cidr = "10.2.0.0/16"

# Subnets em 3 AZs para alta disponibilidade
public_subnet_cidrs  = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
private_subnet_cidrs = ["10.2.11.0/24", "10.2.12.0/24", "10.2.13.0/24"]

# ============================================================================
# Banco de Dados RDS (PostgreSQL)
# ============================================================================
# Instância grande com máxima confiabilidade
rds_instance_class = "db.r5.large"

# Configurações adicionais para RDS (production)
rds_allocated_storage           = 500   # 500 GB
rds_max_allocated_storage       = 1000  # Auto-scaling até 1 TB
rds_backup_retention_period     = 30    # 30 dias de backup
rds_multi_az                    = true  # Multi-AZ em múltiplas regiões
rds_deletion_protection         = true  # Proteger dados críticos
rds_enable_cloudwatch_logs      = true  # Logs detalhados
rds_enable_enhanced_monitoring  = true  # Enhanced monitoring
rds_enable_iam_database_auth    = true  # IAM authentication
rds_storage_encrypted           = true  # Criptografia em repouso

# Performance Insights
rds_enable_performance_insights = true
rds_performance_insights_retention = 7

# ============================================================================
# Banco de Dados MongoDB (DocumentDB - via AWS)
# ============================================================================
# Cluster robusto com replicação e sharding
enable_documentdb              = true
documentdb_instance_class      = "db.r5.xlarge"
documentdb_num_instances       = 3      # 3 instâncias para replicação
documentdb_backup_retention    = 30     # 30 dias
documentdb_backup_window       = "03:00-04:00"  # Backup diário

# Point-in-Time Recovery (PITR)
documentdb_enable_pitr         = true
documentdb_pitr_window         = 7

# ============================================================================
# Cache Redis (ElastiCache) - MVP 3.0
# ============================================================================
# Cluster com múltiplos nós e failover automático
redis_engine_version = "7.0"
redis_node_type      = "cache.r5.large"
redis_num_cache_nodes = 3  # 3 nós com failover automático

# MVP 3.0 - Security & Encryption (LGPD Compliance)
redis_at_rest_encryption_enabled = true   # Criptografia at rest (LGPD)
redis_transit_encryption_enabled = true   # Criptografia in transit (TLS 1.2+)
redis_auth_token_enabled         = true   # Auth token para segurança

# MVP 3.0 - High Availability
redis_automatic_failover_enabled = true   # Failover automático
redis_multi_az_enabled           = true   # Multi-AZ para HA

# MVP 3.0 - Backups
redis_snapshot_retention_limit = 7  # 7 dias de snapshots (compliance)

# ============================================================================
# Computação (ECS Fargate)
# ============================================================================
# Configuração robusta com auto-scaling agressivo
ecs_container_insights = true

# Task Definition - API Backend
ecs_api_task_cpu    = 1024  # 1 vCPU
ecs_api_task_memory = 2048  # 2 GB

ecs_api_desired_count = 3  # 3 instâncias base

# Container
ecs_api_container_port  = 8000
ecs_api_container_image = "eduautismo-ia/api:latest"

# Auto Scaling - Mais agressivo
ecs_api_max_capacity        = 10
ecs_api_min_capacity        = 3
ecs_api_target_cpu_utilization = 70
ecs_api_target_memory_utilization = 80

# ============================================================================
# Storage S3
# ============================================================================
s3_lifecycle_enabled = true
s3_versioning_enabled = true  # Versionamento para compliance

# Lifecycle Rules para production
s3_transition_days_to_standard_ia = 60   # Move para IA após 60 dias
s3_transition_days_to_glacier     = 180  # Move para Glacier após 180 dias
s3_expiration_days                = 2555 # Deleta após 7 anos (compliance)

# Replicação cross-region para DR
s3_enable_replication = true
s3_replication_destination_region = "us-west-2"

# ============================================================================
# Load Balancer
# ============================================================================
# ALB com health checks rigorosos e WAF
enable_alb                      = true
alb_enable_access_logs          = true
alb_access_logs_bucket          = "eduautismo-ia-prod-alb-logs"
alb_health_check_healthy_count  = 2
alb_health_check_unhealthy_count = 3
alb_health_check_interval       = 30
alb_health_check_timeout        = 5

# HTTPS/TLS
enable_https            = true
certificate_arn         = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID"  # TODO: Replace
enable_http_to_https_redirect = true

# ============================================================================
# CDN (CloudFront)
# ============================================================================
enable_cloudfront           = true
cloudfront_default_ttl      = 3600
cloudfront_max_ttl          = 86400
cloudfront_min_ttl          = 0
enable_cloudfront_logging   = true

# ============================================================================
# Logging e Monitoring
# ============================================================================
cloudwatch_log_retention_days = 90  # Manter por 90 dias
enable_datadog_monitoring     = true
datadog_api_key_param         = "/eduautismo-ia/prod/datadog/api-key"  # SSM Parameter

# ============================================================================
# Security & Encryption
# ============================================================================
enable_rds_encryption          = true   # Criptografia RDS
enable_s3_encryption           = true   # Server-side encryption S3
enable_efs_encryption          = true   # EFS encryption
enable_secrets_manager         = true   # Secrets Manager para credenciais

# KMS Keys para cada recurso
kms_key_rds_deletion_window = 10
kms_key_s3_deletion_window  = 10
kms_key_secrets_deletion_window = 10

# ============================================================================
# WAF (Web Application Firewall)
# ============================================================================
enable_waf = true

waf_rules = {
  rate_limit      = 2000  # Requests per 5 minutos
  geo_blocking    = false # Ou true se necessário
  blocked_countries = []  # Lista de países bloqueados
}

# ============================================================================
# DDoS Protection
# ============================================================================
enable_aws_shield_advanced = true

# ============================================================================
# Backup e Disaster Recovery
# ============================================================================
enable_backup_vault      = true
backup_retention_days    = 90

# Cross-region backup
enable_backup_replication = true
backup_replication_region = "us-west-2"

# ============================================================================
# Route 53 e DNS
# ============================================================================
enable_route53            = true
hosted_zone_id            = "Z1234567890ABC"  # TODO: Replace com ID real
domain_name               = "api.eduautismo-ia.com"
enable_health_checks      = true
health_check_interval     = 30

# ============================================================================
# VPN e Network Security
# ============================================================================
enable_vpn               = true
vpn_client_subnets       = ["10.2.21.0/24"]

# ============================================================================
# Secrets Management
# ============================================================================
# Credenciais críticas armazenadas em AWS Secrets Manager
secrets_to_create = [
  "database/postgres/password",
  "database/mongodb/connection-string",
  "openai/api-key",
  "jwt/secret-key",
  "redis/auth-token"
]

# ============================================================================
# Observabilidade
# ============================================================================
enable_xray_tracing       = true
enable_container_logging  = true
enable_vpc_flow_logs      = true

# ============================================================================
# LGPD Compliance
# ============================================================================
# Conformidade com Lei Geral de Proteção de Dados
enable_data_residency_validation = true
allowed_regions = ["us-east-1"]  # Dados residem nos EUA

# Encryption at rest and in transit
require_tls_1_2_or_higher = true
encryption_at_rest_enabled = true

# Data retention and deletion policies
student_data_retention_days = 1825  # 5 anos pós-escola

# ============================================================================
# Tagging Strategy
# ============================================================================
tags = {
  Environment  = "production"
  Project      = "EduAutismo-IA"
  ManagedBy    = "Terraform"
  CostCenter   = "Production"
  DataClass    = "Confidential"  # Para LGPD
  Compliance   = "LGPD"
  CreatedAt    = "2025-01-15"
  BackupPolicy = "Daily-90-days"
}
