# ✅ PROGRESSO DAS CORREÇÕES - FASE 1

**Data:** 05/12/2025
**Status:** 🔄 EM ANDAMENTO (60% completo)

---

## ✅ PROBLEMAS CORRIGIDOS (5/7)

### 1. ✅ Dependência Circular - CORRIGIDO
- Movido `module.cache` para DEPOIS de `module.compute`
- Arquivo: `terraform/main.tf`

### 2. ✅ Módulo Networking Completo - CORRIGIDO
- ✅ Adicionado `data.aws_availability_zones.available`
- ✅ Adicionado `aws_internet_gateway`
- ✅ Adicionado `aws_route_table` (public + private)
- ✅ Adicionado `aws_route_table_association`
- Arquivo: `terraform/modules/networking/main.tf`

### 3. ✅ PostgreSQL Atualizado - CORRIGIDO
- ✅ Versão 14 → 15.4
- ✅ Parametrizado com variável `engine_version`
- ✅ Adicionado variável `rds_engine_version` no root
- Arquivos: `terraform/modules/database/main.tf`, `terraform/variables.tf`

### 4. ✅ Database Security Group - CORRIGIDO
- ✅ Removida referência circular a `var.ecs_security_group_id`
- ✅ Usa CIDR da VPC (via data source)
- Arquivo: `terraform/modules/database/main.tf`

### 5. ✅ Compute - Parcialmente Completo
- ✅ Adicionado `data.aws_region.current`
- ✅ Adicionado `data.aws_caller_identity.current`
- ✅ Adicionado `aws_security_group.alb`
- ✅ Corrigido `aws_security_group.ecs_tasks` (port 8000 only)
- ✅ Adicionado variável `rds_secret_arn`

---

## 🔄 PROBLEMAS EM PROGRESSO (2/7)

### 6. 🔄 Compute - Recursos Faltantes (40% completo)

**Faltam adicionar:**

#### A. IAM Roles (5 recursos)
```hcl
# Adicionar em terraform/modules/compute/main.tf após linha 151

# IAM Role para ECS Task Execution
resource "aws_iam_role" "ecs_execution" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-exec-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Política adicional para ECR e Secrets Manager
resource "aws_iam_role_policy" "ecs_execution_additional" {
  name = "additional-permissions"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          var.rds_secret_arn,
          "${var.rds_secret_arn}*"
        ]
      }
    ]
  })
}

# IAM Role para ECS Task (permissões da aplicação)
resource "aws_iam_role" "ecs_task" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-task-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-task-role"
  }
}

# Política para a aplicação (S3, Secrets Manager, etc)
resource "aws_iam_role_policy" "ecs_task_policy" {
  name = "application-permissions"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::${var.project_name}-${var.environment}-*/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          var.rds_secret_arn,
          "${var.rds_secret_arn}*"
        ]
      }
    ]
  })
}
```

#### B. CloudWatch Log Group
```hcl
# Adicionar antes do ECS Task Definition

resource "aws_cloudwatch_log_group" "app" {
  name_prefix       = "/ecs/${var.project_name}-${var.environment}-"
  retention_in_days = var.environment == "production" ? 90 : 7

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-logs"
  }
}
```

#### C. ECR Repository
```hcl
# Adicionar antes do ECS Task Definition

resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}
```

#### D. ALB Target Group e Listener
```hcl
# Adicionar após Application Load Balancer (linha 151)

resource "aws_lb_target_group" "app" {
  name_prefix = "app-"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
  }

  deregistration_delay = 30

  tags = {
    Name = "${var.project_name}-${var.environment}-tg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# HTTPS Listener (opcional - requer certificado ACM)
# Descomentar quando certificado estiver disponível
# resource "aws_lb_listener" "https" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = 443
#   protocol          = "HTTPS"
#   certificate_arn   = var.acm_certificate_arn
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app.arn
#   }
# }
```

---

### 7. 🔄 Credenciais Hardcoded

**Localização:** `terraform/modules/compute/main.tf` linha ~162

**Problema:**
```hcl
environment = [
  {
    name  = "DATABASE_URL"
    value = "postgresql://user:pass@${var.rds_endpoint}/eduautismo"  # ❌
  }
]
```

**Correção:**
```hcl
# Opção 1: Usar Secrets Manager via environment variable
secrets = [
  {
    name      = "DATABASE_URL"
    valueFrom = var.rds_secret_arn
  }
]

# E remover o environment DATABASE_URL hardcoded

# Opção 2: Construir URL a partir de secrets individuais (melhor)
# Não colocar DATABASE_URL no environment
# A aplicação deve construir a URL lendo do Secrets Manager
```

**Arquivo a modificar:** `terraform/modules/compute/main.tf`

**Status:** ⏳ Pendente

---

## 🔄 TAREFA ADICIONAL

### 8. 🔄 Provider Random

**Arquivo:** `terraform/providers.tf`

**Adicionar:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  required_version = ">= 1.5.0"
}
```

**Status:** ⏳ Pendente

---

## 📋 CHECKLIST FINAL - FASE 1

- [x] 1. Corrigir dependência circular
- [x] 2. Completar módulo networking
- [x] 3. Atualizar PostgreSQL 14 → 15.4
- [x] 4. Corrigir database security group
- [x] 5. Adicionar data sources e ALB SG no compute
- [ ] 6a. Adicionar IAM Roles no compute
- [ ] 6b. Adicionar CloudWatch Log Group
- [ ] 6c. Adicionar ECR Repository
- [ ] 6d. Adicionar ALB Target Group e Listener
- [ ] 7. Remover credenciais hardcoded
- [ ] 8. Adicionar provider random
- [ ] 9. Testar `terraform validate`
- [ ] 10. Testar `terraform plan` em dev

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Adicionar IAM Roles (5 recursos)
2. ✅ Adicionar CloudWatch, ECR, Target Group
3. ✅ Remover credenciais hardcoded
4. ✅ Adicionar provider random
5. ✅ Testar terraform validate

**Tempo Estimado Restante:** 1-2 horas

---

**Progresso:** 60% da Fase 1 completo
**Status:** 🟢 No caminho certo
**Bloqueadores:** Nenhum
