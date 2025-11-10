variable "vpc_id" {
  description = "ID da VPC"
  type        = string
}

variable "public_subnets" {
  description = "IDs das subnets públicas"
  type        = list(string)
}

variable "private_subnets" {
  description = "IDs das subnets privadas"
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

variable "container_insights" {
  description = "Habilitar Container Insights"
  type        = bool
}

variable "rds_endpoint" {
  description = "Endpoint do RDS"
  type        = string
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = var.container_insights ? "enabled" : "disabled"
  }
}

# Security Group para ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-tasks-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name_prefix        = "main-"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.public_subnets
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-${var.environment}-app"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = 256
  memory                  = 512
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  task_role_arn          = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "app"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://user:pass@${var.rds_endpoint}/eduautismo"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-stream-prefix" = "app"
        }
      }

      portMappings = [
        {
          containerPort = 8000
          hostPort     = 8000
          protocol     = "tcp"
        }
      ]
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-${var.environment}-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.environment == "production" ? 2 : 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnets
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8000
  }
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "ecs_security_group_id" {
  value = aws_security_group.ecs_tasks.id
}