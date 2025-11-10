output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.networking.vpc_id
}

output "public_subnets" {
  description = "IDs das subnets públicas"
  value       = module.networking.public_subnet_ids
}

output "private_subnets" {
  description = "IDs das subnets privadas"
  value       = module.networking.private_subnet_ids
}

output "rds_endpoint" {
  description = "Endpoint do banco de dados RDS"
  value       = module.database.rds_endpoint
  sensitive   = true
}

output "ecs_cluster_name" {
  description = "Nome do cluster ECS"
  value       = module.compute.ecs_cluster_name
}

output "alb_dns_name" {
  description = "DNS name do Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "s3_bucket_name" {
  description = "Nome do bucket S3 principal"
  value       = module.storage.s3_bucket_name
}