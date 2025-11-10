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