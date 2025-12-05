# =================================================================
# ElastiCache Redis Module - Outputs
# MVP 3.0 - Cache Layer for Multidisciplinary Platform
# =================================================================

output "redis_replication_group_id" {
  description = "ID do ElastiCache Replication Group"
  value       = aws_elasticache_replication_group.redis.id
}

output "redis_primary_endpoint_address" {
  description = "Endereço do endpoint primário do Redis"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_reader_endpoint_address" {
  description = "Endereço do endpoint de leitura do Redis (se Multi-AZ habilitado)"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "redis_port" {
  description = "Porta do Redis"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_configuration_endpoint" {
  description = "Configuration endpoint (para cluster mode)"
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
}

output "redis_url" {
  description = "URL completa de conexão Redis (redis://host:port)"
  value       = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
}

output "redis_url_with_auth" {
  description = "URL completa de conexão Redis com auth token (se habilitado) - SENSITIVE"
  value = var.auth_token_enabled && var.transit_encryption_enabled ? "rediss://:${random_password.redis_auth_token[0].result}@${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}" : "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
  sensitive   = true
}

output "redis_auth_token" {
  description = "Redis AUTH token - SENSITIVE"
  value       = var.auth_token_enabled && var.transit_encryption_enabled ? random_password.redis_auth_token[0].result : null
  sensitive   = true
}

output "redis_auth_token_secret_arn" {
  description = "ARN do secret no Secrets Manager contendo o auth token"
  value       = var.auth_token_enabled && var.transit_encryption_enabled ? aws_secretsmanager_secret.redis_auth_token[0].arn : null
}

output "redis_security_group_id" {
  description = "ID do Security Group do Redis"
  value       = aws_security_group.redis.id
}

output "redis_subnet_group_name" {
  description = "Nome do Subnet Group do Redis"
  value       = aws_elasticache_subnet_group.redis.name
}

output "redis_parameter_group_name" {
  description = "Nome do Parameter Group do Redis"
  value       = aws_elasticache_parameter_group.redis.name
}

output "redis_engine_version" {
  description = "Versão do Redis"
  value       = aws_elasticache_replication_group.redis.engine_version_actual
}

output "redis_node_type" {
  description = "Tipo de instância do Redis"
  value       = var.node_type
}

output "redis_num_cache_nodes" {
  description = "Número de nós no cluster Redis"
  value       = var.num_cache_nodes
}

output "redis_multi_az_enabled" {
  description = "Se Multi-AZ está habilitado"
  value       = var.multi_az_enabled
}

output "redis_encryption_at_rest_enabled" {
  description = "Se criptografia at rest está habilitada"
  value       = var.at_rest_encryption_enabled
}

output "redis_encryption_in_transit_enabled" {
  description = "Se criptografia in transit está habilitada"
  value       = var.transit_encryption_enabled
}

# CloudWatch Logs
output "redis_slow_log_group_name" {
  description = "Nome do CloudWatch Log Group para slow logs"
  value       = aws_cloudwatch_log_group.redis_slow_log.name
}

output "redis_engine_log_group_name" {
  description = "Nome do CloudWatch Log Group para engine logs"
  value       = aws_cloudwatch_log_group.redis_engine_log.name
}

# For ECS task definition environment variables
output "redis_env_vars" {
  description = "Variáveis de ambiente para o ECS task definition"
  value = {
    REDIS_HOST = aws_elasticache_replication_group.redis.primary_endpoint_address
    REDIS_PORT = tostring(aws_elasticache_replication_group.redis.port)
    REDIS_URL  = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
  }
}

# For monitoring and alarms
output "redis_metrics" {
  description = "Informações para criação de métricas e alarmes do CloudWatch"
  value = {
    replication_group_id = aws_elasticache_replication_group.redis.id
    cluster_name         = "${var.project_name}-${var.environment}-redis"
    namespace            = "AWS/ElastiCache"
  }
}
