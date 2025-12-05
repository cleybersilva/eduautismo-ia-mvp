locals {
  environment = terraform.workspace
  name_prefix = "${var.project_name}-${local.environment}"
}

module "networking" {
  source = "./modules/networking"

  vpc_cidr     = var.vpc_cidr
  project_name = var.project_name
  environment  = local.environment
}

module "database" {
  source = "./modules/database"

  vpc_id            = module.networking.vpc_id
  private_subnets   = module.networking.private_subnet_ids
  instance_class    = var.rds_instance_class
  engine_version    = var.rds_engine_version
  project_name      = var.project_name
  environment       = local.environment
}

module "compute" {
  source = "./modules/compute"

  vpc_id          = module.networking.vpc_id
  public_subnets  = module.networking.public_subnet_ids
  private_subnets = module.networking.private_subnet_ids
  project_name    = var.project_name
  environment     = local.environment

  container_insights = var.ecs_container_insights
  rds_endpoint      = module.database.rds_endpoint
  rds_secret_arn    = module.database.rds_secret_arn
}

# MVP 3.0 - ElastiCache Redis for multidisciplinary platform
# Movido para DEPOIS de compute para evitar dependência circular
module "cache" {
  source = "./modules/cache"

  vpc_id             = module.networking.vpc_id
  private_subnets    = module.networking.private_subnet_ids
  project_name       = var.project_name
  environment        = local.environment

  # Node configuration
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_cache_nodes
  engine_version     = var.redis_engine_version

  # Security - Agora compute já está definido
  allowed_security_group_ids = [module.compute.ecs_security_group_id]
  at_rest_encryption_enabled = var.redis_at_rest_encryption_enabled
  transit_encryption_enabled = var.redis_transit_encryption_enabled
  auth_token_enabled         = var.redis_auth_token_enabled

  # High availability
  automatic_failover_enabled = var.redis_automatic_failover_enabled
  multi_az_enabled           = var.redis_multi_az_enabled

  # Backups
  snapshot_retention_limit = var.redis_snapshot_retention_limit

  # Tags
  tags = var.tags
}

module "storage" {
  source = "./modules/storage"

  project_name        = var.project_name
  environment         = local.environment
  lifecycle_enabled   = var.s3_lifecycle_enabled
}