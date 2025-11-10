variable "vpc_id" {
  description = "ID da VPC"
  type        = string
}

variable "private_subnets" {
  description = "IDs das subnets privadas"
  type        = list(string)
}

variable "instance_class" {
  description = "Classe da instância RDS"
  type        = string
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, production)"
  type        = string
}

# Security Group para RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }
}

# Subnet Group para RDS
resource "aws_db_subnet_group" "main" {
  name_prefix = "${var.project_name}-${var.environment}-"
  subnet_ids  = var.private_subnets

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier_prefix    = "${var.project_name}-${var.environment}-"
  engine              = "postgres"
  engine_version      = "14"
  instance_class      = var.instance_class
  allocated_storage   = 20
  storage_encrypted   = true

  db_name  = "eduautismo"
  username = "eduautismo_admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = var.environment == "production" ? 7 : 1
  multi_az               = var.environment == "production"

  skip_final_snapshot = var.environment != "production"

  tags = {
    Name = "${var.project_name}-${var.environment}-rds"
  }
}

# Senha aleatória para o RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Armazenar a senha no Secrets Manager
resource "aws_secretsmanager_secret" "rds_password" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  secret_id = aws_secretsmanager_secret.rds_password.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    host     = aws_db_instance.main.endpoint
    port     = 5432
    dbname   = aws_db_instance.main.db_name
  })
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "rds_secret_arn" {
  value = aws_secretsmanager_secret.rds_password.arn
}