variable "project_name" {
  description = "Nome do projeto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, production)"
  type        = string
}

variable "lifecycle_enabled" {
  description = "Habilitar regras de lifecycle"
  type        = bool
}

# S3 Bucket principal
resource "aws_s3_bucket" "main" {
  bucket_prefix = "${var.project_name}-${var.environment}-"

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
  }
}

# Criptografia do bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Versionamento do bucket
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = var.environment == "production" ? "Enabled" : "Disabled"
  }
}

# Regras de lifecycle
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  count  = var.lifecycle_enabled ? 1 : 0
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "cleanup"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }

    expiration {
      days = 90
    }
  }
}

# Política de bucket
resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceHTTPS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.main.arn,
          "${aws_s3_bucket.main.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

output "s3_bucket_name" {
  value = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.main.arn
}