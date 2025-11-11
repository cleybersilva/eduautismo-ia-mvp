#!/bin/bash
# ============================================================================
# scripts/setup-terraform-env.sh
# ============================================================================
# Script para validar e setupar ambiente Terraform
#
# Uso:
#   ./scripts/setup-terraform-env.sh dev
#   ./scripts/setup-terraform-env.sh staging
#   ./scripts/setup-terraform-env.sh production

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
ENVIRONMENT="${1:-dev}"
TERRAFORM_DIR="terraform"
ENVIRONMENTS_DIR="$TERRAFORM_DIR/environments"

echo -e "${YELLOW}🚀 Setup Terraform para ambiente: $ENVIRONMENT${NC}"
echo ""

# ============================================================================
# 1. Validações Iniciais
# ============================================================================

echo -e "${YELLOW}📋 Validando pré-requisitos...${NC}"

# Verificar se Terraform está instalado
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform não encontrado. Instale em: https://www.terraform.io/downloads${NC}"
    exit 1
fi

TERRAFORM_VERSION=$(terraform version | head -n 1)
echo -e "${GREEN}✅ $TERRAFORM_VERSION${NC}"

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI não encontrado. Instale em: https://aws.amazon.com/cli/${NC}"
    exit 1
fi

AWS_VERSION=$(aws --version)
echo -e "${GREEN}✅ $AWS_VERSION${NC}"

# Verificar se jq está instalado (para parsing JSON)
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq não encontrado (recomendado). Instale: https://stedolan.github.io/jq/${NC}"
fi

echo ""

# ============================================================================
# 2. Validar arquivo terraform.tfvars
# ============================================================================

echo -e "${YELLOW}📁 Validando arquivo terraform.tfvars...${NC}"

TFVARS_FILE="$ENVIRONMENTS_DIR/$ENVIRONMENT/terraform.tfvars"

if [ ! -f "$TFVARS_FILE" ]; then
    echo -e "${RED}❌ Arquivo não encontrado: $TFVARS_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arquivo encontrado: $TFVARS_FILE${NC}"
echo ""

# ============================================================================
# 3. Validar Syntax Terraform
# ============================================================================

echo -e "${YELLOW}🔍 Validando sintaxe Terraform...${NC}"

cd "$TERRAFORM_DIR"

if terraform validate -var-file="$TFVARS_FILE" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Sintaxe válida${NC}"
else
    echo -e "${RED}❌ Erro na sintaxe Terraform:${NC}"
    terraform validate -var-file="$TFVARS_FILE"
    cd ..
    exit 1
fi

echo ""

# ============================================================================
# 4. Validar AWS Credentials
# ============================================================================

echo -e "${YELLOW}🔐 Validando credenciais AWS...${NC}"

if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ Credenciais AWS não configuradas ou inválidas${NC}"
    echo "Configure com: aws configure"
    cd ..
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
AWS_USER=$(aws sts get-caller-identity --query 'Arn' --output text)

echo -e "${GREEN}✅ Conectado à AWS${NC}"
echo "   Account: $AWS_ACCOUNT"
echo "   User/Role: $AWS_USER"
echo ""

# ============================================================================
# 5. Criar Workspace
# ============================================================================

echo -e "${YELLOW}🏗️  Configurando Terraform workspace...${NC}"

CURRENT_WORKSPACE=$(terraform workspace show)
echo "   Workspace atual: $CURRENT_WORKSPACE"

if [ "$CURRENT_WORKSPACE" != "$ENVIRONMENT" ]; then
    echo -e "${YELLOW}   Criando/Selecionando workspace: $ENVIRONMENT${NC}"
    terraform workspace new "$ENVIRONMENT" 2>/dev/null || terraform workspace select "$ENVIRONMENT"
fi

SELECTED_WORKSPACE=$(terraform workspace show)
echo -e "${GREEN}✅ Workspace selecionado: $SELECTED_WORKSPACE${NC}"
echo ""

# ============================================================================
# 6. Terraform Init
# ============================================================================

echo -e "${YELLOW}⚙️  Inicializando Terraform...${NC}"

terraform init

echo -e "${GREEN}✅ Terraform inicializado${NC}"
echo ""

# ============================================================================
# 7. Plan Preview
# ============================================================================

echo -e "${YELLOW}👀 Gerando plan preview...${NC}"
echo "    (Este pode ser um resumo - use 'terraform plan' completo antes de apply)"
echo ""

PLAN_OUTPUT=$(terraform plan -var-file="../$TFVARS_FILE" -no-color 2>&1 | tail -n 3)
echo "$PLAN_OUTPUT"
echo ""

# ============================================================================
# 8. Resumo
# ============================================================================

cd ..

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup completado para ambiente: $ENVIRONMENT${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo "📌 Próximos passos:"
echo ""
echo "1. Revisar o plano Terraform:"
echo "   cd terraform"
echo "   terraform plan -var-file=\"$TFVARS_FILE\""
echo ""
echo "2. Aplicar as mudanças:"
echo "   terraform apply -var-file=\"$TFVARS_FILE\""
echo ""
echo "3. Verificar outputs:"
echo "   terraform output"
echo ""

echo "📚 Referência rápida:"
echo "   terraform destroy -var-file=\"$TFVARS_FILE\"  # Destruir ambiente"
echo "   terraform state list                          # Listar recursos"
echo "   terraform show                                # Ver estado"
echo ""
