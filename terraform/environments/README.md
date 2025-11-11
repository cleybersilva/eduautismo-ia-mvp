# Terraform Environments - Guia de Uso

## 📋 Estrutura de Ambientes

Este projeto utiliza três ambientes Terraform configurados com `.tfvars`:

```
terraform/
├── environments/
│   ├── dev/
│   │   └── terraform.tfvars          # Configuração Dev (mínimo custo)
│   ├── staging/
│   │   └── terraform.tfvars          # Configuração Staging (realista)
│   └── production/
│       └── terraform.tfvars          # Configuração Prod (HA + segurança)
├── main.tf
├── variables.tf
├── outputs.tf
└── modules/
    ├── networking/
    ├── database/
    ├── compute/
    └── storage/
```

---

## 🚀 Como Usar

### 1. **Desenvolvimento (Dev)**

**Objetivo**: Ambiente local/teste com custo mínimo

```bash
# Inicializar Terraform com workspace dev
cd terraform
terraform workspace new dev || terraform workspace select dev

# Planejar com variáveis de dev
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan

# Aplicar
terraform apply tfplan
```

**Características**:
- RDS: `db.t3.micro` (menor custo)
- ECS: 1 instância
- Sem Multi-AZ
- Sem backup extendido
- Sem criptografia (mais rápido)

---

### 2. **Staging (Teste/Homologação)**

**Objetivo**: Ambiente realista para testes antes de produção

```bash
# Inicializar workspace staging
terraform workspace new staging || terraform workspace select staging

# Planejar com variáveis de staging
terraform plan -var-file="environments/staging/terraform.tfvars" -out=tfplan

# Aplicar
terraform apply tfplan
```

**Características**:
- RDS: `db.t3.small` com Multi-AZ
- ECS: 2 instâncias com auto-scaling até 4
- MongoDB DocumentDB habilitado
- Backup 14 dias
- Criptografia habilitada
- Monitoramento Datadog

---

### 3. **Production (Produção)**

**Objetivo**: Alta disponibilidade, segurança máxima, compliance LGPD

```bash
# Inicializar workspace production
terraform workspace new production || terraform workspace select production

# Planejar com variáveis de production
terraform plan -var-file="environments/production/terraform.tfvars" -out=tfplan

# Review detalhado ANTES de aplicar
terraform show tfplan

# Aplicar (com aprovação manual)
terraform apply tfplan
```

**Características**:
- RDS: `db.r5.large` com Multi-AZ + HA
- ECS: 3-10 instâncias (auto-scaling agressivo)
- MongoDB: Cluster 3 nós com PITR
- Redis: 3 nós com failover automático
- CDN CloudFront habilitado
- WAF + AWS Shield Advanced
- Backup cross-region com 90 dias
- Secrets Manager para credenciais
- Compliance LGPD

---

## 📝 Sobrescrever Variáveis Localmente

Para testes locais, use `.tfvars.local`:

```bash
# Copiar template
cp environments/dev/.tfvars.local.example environments/dev/.tfvars.local

# Editar com valores locais (sobrescreve terraform.tfvars)
terraform plan \
  -var-file="environments/dev/terraform.tfvars" \
  -var-file="environments/dev/.tfvars.local"
```

**⚠️ IMPORTANTE**: Adicionar ao `.gitignore`:
```
*.tfvars.local
*.tfvars.secret
secrets/
```

---

## 🔑 Gerenciamento de Segredos

### Para Development:
- Usar variáveis de ambiente AWS (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Ou usar AWS CLI profiles

### Para Production:
- **NUNCA** colocar secrets em `.tfvars`
- Usar AWS Secrets Manager:
  ```bash
  aws secretsmanager create-secret \
    --name eduautismo-ia/prod/database/password \
    --secret-string "seu_password_aqui"
  ```
- Referenciar no código Terraform:
  ```hcl
  data "aws_secretsmanager_secret_version" "db_password" {
    secret_id = "eduautismo-ia/prod/database/password"
  }
  ```

---

## 🏗️ Workflow de Deployment

### Dev:
```bash
terraform workspace select dev
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### Staging → Production:
```bash
# 1. Testar em staging
terraform workspace select staging
terraform plan -var-file="environments/staging/terraform.tfvars"
terraform apply -var-file="environments/staging/terraform.tfvars"

# 2. Validar saídas e comportamento

# 3. Aplicar em production
terraform workspace select production
terraform plan -var-file="environments/production/terraform.tfvars" -out=plan.prod

# 4. REVIEW CUIDADOSO
terraform show plan.prod

# 5. Aplicar
terraform apply plan.prod
```

---

## 📊 Comparação de Ambientes

| Recurso | Dev | Staging | Production |
|---------|-----|---------|------------|
| RDS Instance | t3.micro | t3.small | r5.large |
| RDS Storage | 20 GB | 100 GB | 500 GB |
| Multi-AZ | ❌ | ✅ | ✅ |
| ECS Desired | 1 | 2 | 3 |
| ECS Max | 1 | 4 | 10 |
| CPU Task | 256 MB | 512 MB | 1 GB |
| Memory Task | 512 MB | 1 GB | 2 GB |
| Redis Nodes | 1 | 2 | 3 |
| Backup (dias) | 7 | 14 | 30-90 |
| Encryption | ❌ | ✅ | ✅ |
| WAF | ❌ | ✅ | ✅ |
| CDN | ❌ | ❌ | ✅ |
| Datadog | ❌ | ✅ | ✅ |
| DDoS Protection | ❌ | ❌ | ✅ |
| **Custo/mês** | ~$50 | ~$500 | ~$3000+ |

---

## ✅ Checklist de Deployment

### Antes de Dev:
- [ ] AWS credentials configuradas
- [ ] Terraform instalado (`terraform --version`)
- [ ] Workspace criado

### Antes de Staging:
- [ ] DNS/Route53 verificado
- [ ] Certificado SSL/TLS válido
- [ ] Secrets Manager populado
- [ ] Backup policy validada

### Antes de Production:
- [ ] ✅ Staging testado completamente
- [ ] ✅ Disaster Recovery plan documentado
- [ ] ✅ LGPD compliance checklist
- [ ] ✅ Security audit realizado
- [ ] ✅ Aprovação stakeholder
- [ ] ✅ Rollback plan criado
- [ ] ✅ On-call team notificado

---

## 🐛 Troubleshooting

### Erro: "Workspace already exists"
```bash
terraform workspace select dev  # Usar existente
```

### Erro: "Invalid Terraform configuration"
```bash
terraform validate -var-file="environments/dev/terraform.tfvars"
```

### Verificar estado actual:
```bash
terraform workspace show  # Workspace atual
terraform state list     # Recursos gerenciados
terraform state show 'resource_type.name'  # Detalhe do recurso
```

### Destruir ambiente (CUIDADO!):
```bash
# Dev (seguro)
terraform destroy -var-file="environments/dev/terraform.tfvars"

# Production (PERIGO - requer aprovação)
terraform destroy -var-file="environments/production/terraform.tfvars" -auto-approve  # NÃO RECOMENDADO
```

---

## 📖 Referências

- [Terraform Workspaces](https://www.terraform.io/docs/state/workspaces.html)
- [Terraform Variables](https://www.terraform.io/docs/language/values/variables.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [LGPD Compliance](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)

---

**Última atualização**: 2025-01-15  
**Projeto**: EduAutismo IA MVP  
**Autor**: DevOps Team
