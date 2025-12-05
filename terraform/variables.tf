variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "eduautismo-ia"
}

variable "environment" {
  description = "Ambiente (dev, staging, production)"
  type        = string
  default     = "dev"
}

# Variáveis de Rede
variable "vpc_cidr" {
  description = "CIDR block para a VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Variáveis de Banco de Dados
variable "rds_instance_class" {
  description = "Tipo de instância RDS"
  type        = string
  default     = "db.t3.small"
}

variable "rds_engine_version" {
  description = "Versão do PostgreSQL"
  type        = string
  default     = "15.4"
}

# Variáveis de Computação
variable "ecs_container_insights" {
  description = "Habilitar Container Insights no ECS"
  type        = bool
  default     = true
}

# Variáveis de Storage
variable "s3_lifecycle_enabled" {
  description = "Habilitar regras de lifecycle no S3"
  type        = bool
  default     = true
}

# =================================================================
# MVP 3.0 - ElastiCache Redis Variables
# =================================================================

variable "redis_node_type" {
  description = "Tipo de instância do Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Número de réplicas do Redis"
  type        = number
  default     = 1
}

variable "redis_engine_version" {
  description = "Versão do Redis"
  type        = string
  default     = "7.0"
}

variable "redis_at_rest_encryption_enabled" {
  description = "Habilitar criptografia at rest"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_enabled" {
  description = "Habilitar criptografia in transit"
  type        = bool
  default     = true
}

variable "redis_auth_token_enabled" {
  description = "Habilitar auth token (senha)"
  type        = bool
  default     = true
}

variable "redis_automatic_failover_enabled" {
  description = "Habilitar failover automático (requer num_cache_nodes > 1)"
  type        = bool
  default     = true
}

variable "redis_multi_az_enabled" {
  description = "Habilitar Multi-AZ"
  type        = bool
  default     = true
}

variable "redis_snapshot_retention_limit" {
  description = "Número de dias para retenção de snapshots"
  type        = number
  default     = 5
}

variable "tags" {
  description = "Tags adicionais para os recursos"
  type        = map(string)
  default     = {}
}