# Infraestrutura Terraform

Infraestrutura como Código (IaC) para implantação do EduAutismo IA na AWS.

## Visão Geral

Este diretório contém configurações do Terraform para provisionamento e gerenciamento da infraestrutura AWS.

## Estrutura

```
terraform/
├── main.tf           # Configuração principal da infraestrutura
├── variables.tf      # Variáveis de entrada
├── outputs.tf        # Valores de saída
├── providers.tf      # Configurações de provedores
├── backend.tf        # Configuração de estado remoto
├── modules/          # Módulos reutilizáveis
│   ├── networking/   # Rede
│   ├── database/     # Banco de dados
│   ├── compute/      # Computação
│   └── storage/      # Armazenamento
└── environments/     # Configurações específicas de ambiente
    ├── dev/         # Desenvolvimento
    ├── staging/     # Homologação
    └── production/  # Produção
```

## Pré-requisitos

- Terraform >= 1.5.0
- AWS CLI configurado
- Credenciais AWS com permissões apropriadas

## Uso

### Inicializar o Terraform

```bash
cd terraform/
terraform init
```

### Criar Workspace

```bash
terraform workspace new development
terraform workspace select development
```

### Planejar Mudanças

```bash
terraform plan -out=tfplan
```

### Aplicar Mudanças

```bash
terraform apply tfplan
```

### Destruir Infraestrutura

```bash
terraform destroy
```

## Recursos Principais

- **VPC & Rede**: Subnets, NAT Gateway, Grupos de Segurança
- **Computação**: ECS Fargate, ALB
- **Banco de Dados**: RDS PostgreSQL, DocumentDB
- **Armazenamento**: Buckets S3
- **Monitoramento**: CloudWatch, integração com Datadog
- **Segurança**: KMS, Secrets Manager

## Gerenciamento de Estado

O estado do Terraform é armazenado remotamente no S3 com DynamoDB para bloqueio:

```hcl
backend "s3" {
  bucket         = "eduautismo-terraform-state"
  key            = "terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-locks"
  encrypt        = true
}
```

## Otimização de Custos

- Usar Instâncias Reservadas para RDS
- Habilitar políticas de ciclo de vida do S3
- Dimensionar corretamente as tasks do ECS
- Usar alternativas ao NAT Gateway para ambientes de desenvolvimento

Consulte o [Guia FinOps](../docs/finops.md) para estratégias detalhadas de otimização de custos.
