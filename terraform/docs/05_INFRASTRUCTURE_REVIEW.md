# 🔍 REVISÃO DE INFRAESTRUTURA TERRAFORM

**Data:** 05/12/2025
**Revisor:** Claude Code
**Projeto:** EduAutismo IA MVP 3.0
**Status:** ⚠️ PROBLEMAS CRÍTICOS ENCONTRADOS

---

## 📋 Sumário Executivo

A infraestrutura Terraform apresenta **7 problemas CRÍTICOS** e **15 melhorias recomendadas** que devem ser corrigidas antes do deploy em produção.

### Severidade dos Problemas:

- 🔴 **CRÍTICO (7):** Impede o funcionamento ou causa falhas no deploy
- 🟡 **ALTO (8):** Problemas de segurança ou performance
- 🟢 **MÉDIO (7):** Melhorias de best practices

**Ação Requerida:** Correção imediata dos problemas críticos antes de qualquer deploy.

---

## 🔴 PROBLEMAS CRÍTICOS

### 1. ❌ Dependência Circular entre Módulos

**Arquivo:** `terraform/main.tf`
**Linhas:** 25-53, 55-69

**Problema:**
```hcl
# Linha 25-53: módulo cache é definido ANTES de compute
module "cache" {
  # ...
  # Linha 39: Tenta usar security group do compute que ainda não existe
  allowed_security_group_ids = [module.compute.ecs_security_group_id]
}

# Linha 55-69: módulo compute definido DEPOIS
module "compute" {
  # ...
}
```

**Impacto:** ❌ `terraform plan` falhará com erro de referência cíclica.

**Correção:**
```hcl
# Opção 1: Mover cache DEPOIS de compute
module "networking" { ... }
module "database" { ... }
module "compute" { ... }  # Definir ANTES
module "cache" {           # Usar security group DEPOIS
  allowed_security_group_ids = [module.compute.ecs_security_group_id]
}

# Opção 2: Criar security group separado no networking
module "networking" {
  # Adicionar output: ecs_security_group_id
}
module "cache" {
  allowed_security_group_ids = [module.networking.ecs_security_group_id]
}
```

**Recomendação:** Opção 1 (mais simples).

---

### 2. ❌ Módulo Compute Incompleto

**Arquivo:** `terraform/modules/compute/main.tf`
**Linhas:** Múltiplas

**Recursos Faltantes:**

1. **ALB Security Group** (referenciado na linha 74, 90)
```hcl
# FALTANDO:
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

2. **IAM Roles** (referenciado na linha 102, 103)
```hcl
# FALTANDO:
resource "aws_iam_role" "ecs_execution" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-execution-"

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
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

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
}

# Policy para acessar Secrets Manager, S3, etc
resource "aws_iam_role_policy" "ecs_task_policy" {
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "*"
      }
    ]
  })
}
```

3. **CloudWatch Log Group** (referenciado na linha 160)
```hcl
# FALTANDO:
resource "aws_cloudwatch_log_group" "app" {
  name_prefix       = "/ecs/${var.project_name}-${var.environment}-"
  retention_in_days = var.environment == "production" ? 90 : 7
}
```

4. **ECR Repository** (referenciado na linha 108)
```hcl
# FALTANDO:
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

5. **ALB Target Group** (referenciado na linha 190)
```hcl
# FALTANDO:
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
  }

  deregistration_delay = 30
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

6. **Data Sources** (referenciado na linha 159)
```hcl
# FALTANDO:
data "aws_region" "current" {}
```

**Impacto:** ❌ Terraform apply falhará com erros de recursos não encontrados.

---

### 3. ❌ Variável Não Declarada no Módulo Database

**Arquivo:** `terraform/modules/database/main.tf`
**Linha:** 35

**Problema:**
```hcl
resource "aws_security_group" "rds" {
  # ...
  ingress {
    # ...
    security_groups = [var.ecs_security_group_id]  # ❌ Variável não declarada
  }
}
```

**Correção:**
```hcl
# Adicionar no topo do arquivo:
variable "ecs_security_group_id" {
  description = "ID do security group do ECS para acesso ao RDS"
  type        = string
}

# E no main.tf raiz:
module "database" {
  # ...
  ecs_security_group_id = module.compute.ecs_security_group_id
}
```

**Mas:** Isso cria dependência circular (database → compute, compute → database). Melhor solução abaixo.

---

### 4. ❌ Módulo Networking Incompleto

**Arquivo:** `terraform/modules/networking/main.tf`

**Recursos Faltantes:**

1. **Internet Gateway** (necessário para subnets públicas)
```hcl
# FALTANDO:
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}
```

2. **Route Tables**
```hcl
# FALTANDO:
# Route table para subnets públicas (via IGW)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route table para subnets privadas (via NAT Gateway)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
```

3. **Data Source**
```hcl
# FALTANDO:
data "aws_availability_zones" "available" {
  state = "available"
}
```

**Impacto:** ❌ Subnets públicas não terão internet, NAT Gateway não funcionará.

---

### 5. 🔴 Credenciais Hardcoded (SEGURANÇA CRÍTICA)

**Arquivo:** `terraform/modules/compute/main.tf`
**Linha:** 113

**Problema:**
```hcl
environment = [
  {
    name  = "DATABASE_URL"
    value = "postgresql://user:pass@${var.rds_endpoint}/eduautismo"  # ❌ HARDCODED
  }
]
```

**Impacto:** 🔒 VIOLAÇÃO DE SEGURANÇA - credenciais expostas no código.

**Correção:**
```hcl
# Usar Secrets Manager
environment = [
  {
    name  = "DATABASE_SECRET_ARN"
    value = module.database.rds_secret_arn
  }
]

# E no código da aplicação (Python/FastAPI):
import boto3
import json

secrets_client = boto3.client('secretsmanager')
secret_arn = os.environ['DATABASE_SECRET_ARN']
secret = secrets_client.get_secret_value(SecretId=secret_arn)
db_credentials = json.loads(secret['SecretString'])
DATABASE_URL = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}/{db_credentials['dbname']}"
```

---

### 6. ❌ Backend S3 Sem Lifecycle Policy

**Arquivo:** `terraform/backend.tf`
**Linha:** 2-8

**Problema:**
```hcl
terraform {
  backend "s3" {
    bucket = "eduautismo-terraform-state"  # ❌ Bucket precisa existir primeiro
    # ... sem verificação de existência
  }
}
```

**Impacto:** ❌ Se bucket não existir, `terraform init` falhará.

**Correção:**
```bash
# Criar bucket manualmente ANTES de terraform init:
aws s3 mb s3://eduautismo-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket eduautismo-terraform-state \
  --versioning-configuration Status=Enabled

# Habilitar encryption
aws s3api put-bucket-encryption \
  --bucket eduautismo-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Criar DynamoDB table para locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Ou:** Criar módulo `bootstrap/` separado para criar esses recursos.

---

### 7. ❌ RDS PostgreSQL Versão Desatualizada

**Arquivo:** `terraform/modules/database/main.tf`
**Linha:** 53

**Problema:**
```hcl
engine_version = "14"  # ❌ Versão desatualizada, deveria ser 15.4 (MVP 3.0)
```

**Correção:**
```hcl
engine_version = var.engine_version  # Parametrizar

# E adicionar variável:
variable "engine_version" {
  description = "Versão do PostgreSQL"
  type        = string
  default     = "15.4"  # MVP 3.0
}
```

---

## 🟡 PROBLEMAS DE ALTA SEVERIDADE

### 8. 🟡 ALB Sem HTTPS

**Arquivo:** `terraform/modules/compute/main.tf`

**Problema:** ALB listener apenas na porta 80 (HTTP), sem SSL/TLS.

**Correção:**
```hcl
# Adicionar listener HTTPS
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Redirect HTTP → HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Variável para certificado
variable "acm_certificate_arn" {
  description = "ARN do certificado ACM para HTTPS"
  type        = string
  default     = ""  # Opcional em dev
}
```

---

### 9. 🟡 Security Groups Muito Permissivos

**Arquivo:** `terraform/modules/compute/main.tf`
**Linha:** 71-82

**Problema:**
```hcl
ingress {
  from_port       = 0   # ❌ Aceita TODAS as portas
  to_port         = 0
  protocol        = "-1"  # ❌ Todos os protocolos
  security_groups = [aws_security_group.alb.id]
}
```

**Correção:**
```hcl
ingress {
  description     = "Allow traffic from ALB"
  from_port       = 8000  # ✅ Apenas porta da aplicação
  to_port         = 8000
  protocol        = "tcp"
  security_groups = [aws_security_group.alb.id]
}
```

---

### 10. 🟡 NAT Gateway Single Point of Failure

**Arquivo:** `terraform/modules/networking/main.tf`
**Linha:** 51-58

**Problema:** Apenas 1 NAT Gateway para 2 subnets privadas.

**Correção:**
```hcl
# Criar 1 NAT Gateway por AZ (HA)
resource "aws_eip" "nat" {
  count  = 2  # Um por AZ
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
  }
}

# Route table privada por AZ
resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
  }
}
```

**Custo:** +$45/mês por NAT Gateway adicional em produção.
**Benefício:** Alta disponibilidade - se 1 AZ cair, outra continua funcionando.

---

### 11. 🟡 Falta WAF no ALB (Produção)

**Problema:** ALB exposto à internet sem Web Application Firewall.

**Correção:**
```hcl
# Criar módulo security/waf.tf
resource "aws_wafv2_web_acl" "main" {
  count = var.environment == "production" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection protection
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "MainWebACL"
    sampled_requests_enabled   = true
  }
}

# Associar ao ALB
resource "aws_wafv2_web_acl_association" "main" {
  count        = var.environment == "production" ? 1 : 0
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main[0].arn
}
```

**Custo:** ~$10-50/mês dependendo do tráfego.

---

### 12. 🟡 RDS Backup Insuficiente

**Arquivo:** `terraform/modules/database/main.tf`
**Linha:** 65

**Problema:**
```hcl
backup_retention_period = var.environment == "production" ? 7 : 1  # Apenas 7 dias
```

**Correção (LGPD compliance):**
```hcl
backup_retention_period = var.environment == "production" ? 30 : 7
# 30 dias em produção para compliance
```

---

### 13. 🟡 Falta CloudWatch Alarms

**Problema:** Nenhum alarme configurado para monitoramento.

**Correção:** Criar módulo `monitoring/alarms.tf`
```hcl
# Alarme: ECS CPU alto
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization above 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }
}

# Alarme: RDS Connections alto
resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS connections above 80"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

# Alarme: Redis Memory alto
resource "aws_cloudwatch_metric_alarm" "redis_memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-redis-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Redis memory usage above 80%"

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }
}

# SNS Topic para alertas
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
```

---

### 14. 🟡 Falta Auto-Scaling do ECS

**Arquivo:** `terraform/modules/compute/main.tf`

**Problema:** Desired count fixo (não escala sob carga).

**Correção:**
```hcl
# Auto-scaling target
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.environment == "production" ? 10 : 3
  min_capacity       = var.environment == "production" ? 3 : 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Scale up policy (CPU > 70%)
resource "aws_appautoscaling_policy" "ecs_scale_up" {
  name               = "${var.project_name}-${var.environment}-scale-up"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70.0

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Scale up policy (Memory > 80%)
resource "aws_appautoscaling_policy" "ecs_scale_memory" {
  name               = "${var.project_name}-${var.environment}-scale-memory"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 80.0

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

---

### 15. 🟡 Módulo Cache Sem Provider Random

**Arquivo:** `terraform/modules/cache/main.tf`
**Linha:** 9-13

**Problema:**
```hcl
resource "random_password" "redis_auth_token" {
  # ... usa provider 'random' mas não está declarado
}
```

**Correção:** Adicionar ao `terraform/providers.tf`:
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {  # ✅ ADICIONAR
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  required_version = ">= 1.5.0"
}
```

---

## 🟢 MELHORIAS RECOMENDADAS

### 16. 🟢 Separar Variáveis e Outputs por Módulo

**Problema:** Módulos compute, database, networking têm tudo em `main.tf`.

**Best Practice:** Criar arquivos separados:
```
modules/compute/
├── main.tf       # Recursos
├── variables.tf  # Variáveis de entrada
├── outputs.tf    # Outputs
└── versions.tf   # Provider requirements (opcional)
```

---

### 17. 🟢 Adicionar Tags Consistentes

**Problema:** Tags inconsistentes entre recursos.

**Best Practice:**
```hcl
# Em cada módulo, usar locals para tags
locals {
  common_tags = merge(
    var.tags,
    {
      Module      = "compute"  # Nome do módulo
      ManagedBy   = "Terraform"
      Environment = var.environment
      Project     = var.project_name
      CostCenter  = var.environment == "production" ? "Prod" : "Dev"
    }
  )
}

# Aplicar em todos os recursos
resource "aws_ecs_cluster" "main" {
  # ...
  tags = local.common_tags
}
```

---

### 18. 🟢 Usar count/for_each Consistentemente

**Problema:** Alguns recursos usam `count`, outros não.

**Best Practice:**
```hcl
# Usar for_each para múltiplos recursos similares
resource "aws_subnet" "public" {
  for_each = toset(var.public_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[index(var.public_subnet_cidrs, each.value)]

  tags = {
    Name = "${var.project_name}-${var.environment}-public-${each.key}"
  }
}
```

---

### 19. 🟢 Adicionar Lifecycle Rules

**Best Practice:**
```hcl
resource "aws_db_instance" "main" {
  # ...

  lifecycle {
    prevent_destroy = true  # Em produção
    ignore_changes  = [password]  # Ignorar mudanças de senha
  }
}

resource "aws_security_group" "ecs_tasks" {
  # ...

  lifecycle {
    create_before_destroy = true  # Para security groups
  }
}
```

---

### 20. 🟢 Parametrizar Mais Valores

**Problema:** Valores hardcoded que deveriam ser variáveis.

**Exemplos:**
```hcl
# Hardcoded:
retention_in_days = 7

# Melhor:
retention_in_days = var.log_retention_days

# Com variável:
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch value."
  }
}
```

---

### 21. 🟢 Adicionar Validações de Variáveis

```hcl
variable "environment" {
  description = "Environment name"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}
```

---

### 22. 🟢 Usar terraform-docs para Documentação

```bash
# Instalar terraform-docs
brew install terraform-docs  # macOS
# ou: https://github.com/terraform-docs/terraform-docs

# Gerar documentação
cd terraform/modules/cache
terraform-docs markdown table . > README.md
```

---

## 📊 Priorização de Correções

### 🔴 FASE 1 - CRÍTICO (Deve ser feito ANTES de qualquer deploy):

1. ✅ Corrigir dependência circular (mover cache após compute)
2. ✅ Completar módulo compute (ALB SG, IAM, CloudWatch, ECR, Target Group, Data Sources)
3. ✅ Completar módulo networking (IGW, Route Tables, Data Source)
4. ✅ Remover credenciais hardcoded (usar Secrets Manager)
5. ✅ Corrigir variável faltante no database
6. ✅ Criar bucket S3 e DynamoDB table para backend
7. ✅ Atualizar PostgreSQL 14 → 15.4

**Tempo Estimado:** 4-6 horas

---

### 🟡 FASE 2 - ALTA PRIORIDADE (Antes de produção):

8. ✅ Adicionar HTTPS no ALB
9. ✅ Corrigir Security Groups (least privilege)
10. ✅ Adicionar segundo NAT Gateway (HA)
11. ✅ Adicionar WAF (produção)
12. ✅ Aumentar RDS backup retention (30 dias)
13. ✅ Adicionar CloudWatch Alarms
14. ✅ Adicionar ECS Auto-Scaling
15. ✅ Adicionar provider random

**Tempo Estimado:** 3-4 horas

---

### 🟢 FASE 3 - MELHORIAS (Pode ser feito gradualmente):

16-22. Melhorias de organização e best practices

**Tempo Estimado:** 2-3 horas

---

## 🚀 Plano de Ação Recomendado

### Opção A: Correção Incremental (Recomendado para produção existente)

1. Criar branch `fix/terraform-issues`
2. Corrigir problemas críticos (Fase 1)
3. Testar em dev: `terraform plan -var-file=environments/dev/terraform.tfvars`
4. Deploy em dev: `terraform apply`
5. Validar: smoke tests
6. Corrigir problemas alta prioridade (Fase 2)
7. Testar em staging
8. Deploy em produção (janela de manutenção)

**Timeline:** 2-3 dias

---

### Opção B: Refatoração Completa (Recomendado para novo projeto)

1. Criar branch `refactor/terraform-complete`
2. Corrigir TODOS os problemas (Fases 1, 2, 3)
3. Adicionar testes automatizados (terraform validate, tflint, checkov)
4. Testar deploy from scratch em dev
5. Deploy em staging
6. Deploy em produção

**Timeline:** 1 semana

---

## 📝 Checklist de Validação

Antes de considerar a infraestrutura pronta:

- [ ] `terraform init` executa sem erros
- [ ] `terraform validate` passa sem warnings
- [ ] `terraform plan` não mostra erros
- [ ] `terraform apply` cria todos os recursos
- [ ] Smoke tests passam (ALB responde, ECS healthy, RDS conectável, Redis conectável)
- [ ] Security scan passa (checkov, tfsec, ou similar)
- [ ] Documentação atualizada (README de cada módulo)
- [ ] Variáveis documentadas com descriptions
- [ ] Outputs documentados com descriptions
- [ ] Tags aplicadas consistentemente
- [ ] Secrets Manager configurado (sem credenciais hardcoded)
- [ ] CloudWatch Alarms configurados
- [ ] Auto-Scaling configurado
- [ ] Backups configurados (30 dias prod)
- [ ] HTTPS configurado (produção)
- [ ] WAF configurado (produção)

---

## 📚 Referências de Best Practices

1. **Terraform AWS Best Practices:**
   - https://aws.amazon.com/blogs/apn/terraform-best-practices-for-aws-users/
   - https://www.terraform-best-practices.com/

2. **AWS Well-Architected Framework:**
   - https://aws.amazon.com/architecture/well-architected/

3. **Security:**
   - https://docs.aws.amazon.com/security/
   - https://cheatsheetseries.owasp.org/cheatsheets/Infrastructure_as_Code_Security_Cheat_Sheet.html

4. **Terraform Module Structure:**
   - https://developer.hashicorp.com/terraform/language/modules/develop/structure

---

## 🎯 Conclusão

A infraestrutura Terraform atual **NÃO ESTÁ PRONTA** para deploy em produção devido aos 7 problemas críticos identificados.

**Ação Requerida:**
1. ❌ NÃO fazer deploy até corrigir problemas críticos
2. ✅ Priorizar Fase 1 (problemas críticos)
3. ✅ Seguir plano de ação (Opção A ou B)
4. ✅ Validar com checklist antes de produção

**Tempo Estimado Total:** 9-13 horas (todas as fases)

---

**Documento Revisado por:** Claude Code
**Data:** 05/12/2025
**Versão:** 1.0
**Próxima Revisão:** Após correções da Fase 1

**Status:** ⚠️ BLOQUEADO PARA PRODUÇÃO - Correções necessárias
