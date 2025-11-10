# Terraform Infrastructure

Infrastructure as Code (IaC) for EduAutismo IA deployment on AWS.

## Overview

This directory contains Terraform configurations for provisioning and managing AWS infrastructure.

## Structure

```
terraform/
├── main.tf           # Main infrastructure configuration
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── providers.tf      # Provider configurations
├── backend.tf        # Remote state configuration
├── modules/          # Reusable modules
│   ├── networking/
│   ├── database/
│   ├── compute/
│   └── storage/
└── environments/     # Environment-specific configs
    ├── dev/
    ├── staging/
    └── production/
```

## Prerequisites

- Terraform >= 1.5.0
- AWS CLI configured
- AWS credentials with appropriate permissions

## Usage

### Initialize Terraform
```bash
cd terraform/
terraform init
```

### Create Workspace
```bash
terraform workspace new development
terraform workspace select development
```

### Plan Changes
```bash
terraform plan -out=tfplan
```

### Apply Changes
```bash
terraform apply tfplan
```

### Destroy Infrastructure
```bash
terraform destroy
```

## Key Resources

- **VPC & Networking**: Subnets, NAT Gateway, Security Groups
- **Compute**: ECS Fargate, ALB
- **Database**: RDS PostgreSQL, DocumentDB
- **Storage**: S3 buckets
- **Monitoring**: CloudWatch, Datadog integration
- **Security**: KMS, Secrets Manager

## State Management

Terraform state is stored remotely in S3 with DynamoDB for locking:
```hcl
backend "s3" {
  bucket         = "eduautismo-terraform-state"
  key            = "terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-locks"
  encrypt        = true
}
```

## Cost Optimization

- Use Reserved Instances for RDS
- Enable S3 Lifecycle policies
- Right-size ECS tasks
- Use NAT Gateway alternatives for dev environments

See [FinOps Guide](../docs/finops.md) for detailed cost optimization strategies.
