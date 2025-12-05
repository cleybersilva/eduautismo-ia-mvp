# =================================================================
# ElastiCache Redis Module - Main Resources
# MVP 3.0 - Cache Layer for Multidisciplinary Platform
# =================================================================

# Random password for Redis AUTH token
resource "random_password" "redis_auth_token" {
  count   = var.auth_token_enabled ? 1 : 0
  length  = 32
  special = true
}

# Security Group for Redis
resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-${var.environment}-redis-"
  description = "Security group for ElastiCache Redis cluster"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis access from allowed security groups"
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-sg"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Subnet Group for Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.private_subnets

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-subnet-group"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )
}

# Parameter Group for Redis
resource "aws_elasticache_parameter_group" "redis" {
  name   = "${var.project_name}-${var.environment}-redis-params"
  family = var.parameter_group_family

  # Otimizações para cache de sessão e dados MVP 3.0
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-params"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )
}

# ElastiCache Replication Group (Redis Cluster)
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  replication_group_description = "Redis cluster for ${var.project_name} ${var.environment} - MVP 3.0 Multidisciplinary Platform"

  # Engine configuration
  engine               = "redis"
  engine_version       = var.engine_version
  port                 = var.port
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  # Node configuration
  node_type            = var.node_type
  num_cache_clusters   = var.num_cache_nodes

  # High availability
  automatic_failover_enabled = var.automatic_failover_enabled && var.num_cache_nodes > 1
  multi_az_enabled           = var.multi_az_enabled && var.num_cache_nodes > 1

  # Network configuration
  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  # Security - Encryption at rest
  at_rest_encryption_enabled = var.at_rest_encryption_enabled

  # Security - Encryption in transit
  transit_encryption_enabled = var.transit_encryption_enabled
  auth_token                 = var.auth_token_enabled && var.transit_encryption_enabled ? random_password.redis_auth_token[0].result : null

  # Backup configuration
  snapshot_retention_limit = var.snapshot_retention_limit
  snapshot_window          = var.snapshot_window
  final_snapshot_identifier = "${var.project_name}-${var.environment}-redis-final-snapshot-${formatdate("YYYYMMDD-hhmmss", timestamp())}"

  # Maintenance
  maintenance_window       = var.maintenance_window
  auto_minor_version_upgrade = true
  apply_immediately        = var.apply_immediately

  # Notifications
  notification_topic_arn = null # Can be added later for SNS notifications

  # Logs (available for Redis 6.x+)
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_engine_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "engine-log"
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
      Purpose     = "MVP 3.0 - Cache for multidisciplinary platform"
      UseCases    = "Session cache, BNCC data cache, API response cache"
    },
    var.tags
  )

  lifecycle {
    ignore_changes = [
      final_snapshot_identifier
    ]
  }
}

# CloudWatch Log Group for Redis Slow Logs
resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/${var.project_name}-${var.environment}-redis/slow-log"
  retention_in_days = 7

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-slow-log"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )
}

# CloudWatch Log Group for Redis Engine Logs
resource "aws_cloudwatch_log_group" "redis_engine_log" {
  name              = "/aws/elasticache/${var.project_name}-${var.environment}-redis/engine-log"
  retention_in_days = 7

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-engine-log"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )
}

# Store Redis auth token in Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth_token" {
  count       = var.auth_token_enabled && var.transit_encryption_enabled ? 1 : 0
  name        = "${var.project_name}-${var.environment}-redis-auth-token"
  description = "Redis AUTH token for ${var.project_name} ${var.environment}"

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-redis-auth-token"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cache"
    },
    var.tags
  )
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  count         = var.auth_token_enabled && var.transit_encryption_enabled ? 1 : 0
  secret_id     = aws_secretsmanager_secret.redis_auth_token[0].id
  secret_string = random_password.redis_auth_token[0].result
}
