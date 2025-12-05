# =================================================================
# ElastiCache Redis Module - Variables
# MVP 3.0 - Cache Layer for Multidisciplinary Platform
# =================================================================

variable "vpc_id" {
  description = "ID da VPC onde o Redis será criado"
  type        = string
}

variable "private_subnets" {
  description = "IDs das subnets privadas para o Redis"
  type        = list(string)
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, production)"
  type        = string
}

variable "node_type" {
  description = "Tipo de instância do Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "num_cache_nodes" {
  description = "Número de réplicas do Redis"
  type        = number
  default     = 1
}

variable "engine_version" {
  description = "Versão do Redis"
  type        = string
  default     = "7.0"
}

variable "parameter_group_family" {
  description = "Família do parameter group do Redis"
  type        = string
  default     = "redis7"
}

variable "port" {
  description = "Porta do Redis"
  type        = number
  default     = 6379
}

variable "snapshot_retention_limit" {
  description = "Número de dias para retenção de snapshots"
  type        = number
  default     = 5
}

variable "snapshot_window" {
  description = "Janela de tempo para snapshots (UTC)"
  type        = string
  default     = "03:00-05:00"
}

variable "maintenance_window" {
  description = "Janela de tempo para manutenção (UTC)"
  type        = string
  default     = "sun:05:00-sun:07:00"
}

variable "apply_immediately" {
  description = "Aplicar mudanças imediatamente (use com cuidado em produção)"
  type        = bool
  default     = false
}

variable "automatic_failover_enabled" {
  description = "Habilitar failover automático (requer num_cache_nodes > 1)"
  type        = bool
  default     = true
}

variable "multi_az_enabled" {
  description = "Habilitar Multi-AZ"
  type        = bool
  default     = true
}

variable "at_rest_encryption_enabled" {
  description = "Habilitar criptografia at rest"
  type        = bool
  default     = true
}

variable "transit_encryption_enabled" {
  description = "Habilitar criptografia in transit"
  type        = bool
  default     = true
}

variable "auth_token_enabled" {
  description = "Habilitar auth token (senha)"
  type        = bool
  default     = true
}

variable "allowed_security_group_ids" {
  description = "IDs dos security groups que podem acessar o Redis"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags adicionais para os recursos"
  type        = map(string)
  default     = {}
}
