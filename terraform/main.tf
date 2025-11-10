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
}

module "storage" {
  source = "./modules/storage"

  project_name        = var.project_name
  environment         = local.environment
  lifecycle_enabled   = var.s3_lifecycle_enabled
}