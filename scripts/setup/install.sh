#!/bin/bash

# Script de instalação completa do EduAutismo IA

set -e  # Parar em caso de erro

echo "========================================="
echo "   EduAutismo IA - Instalação Completa"
echo "========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se está no diretório correto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Erro: Execute este script do diretório raiz do projeto${NC}"
    exit 1
fi

# Verificar Python
echo -e "${YELLOW}>>> Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 não encontrado. Instale Python 3.12+${NC}"
    exit 1
fi
python3 --version
echo ""

# Verificar Node.js
echo -e "${YELLOW}>>> Verificando Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js não encontrado. Instale Node.js 18+${NC}"
    exit 1
fi
node --version
npm --version
echo ""

# Backend
echo -e "${YELLOW}>>> Configurando Backend...${NC}"
cd backend

# Criar venv se não existir
if [ ! -d "../venv" ]; then
    cd ..
    python3 -m venv venv
    cd backend
fi

# Ativar venv
cd ..
source venv/bin/activate
cd backend

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Configurar .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Configure o arquivo backend/.env antes de continuar${NC}"
fi

cd ..
echo -e "${GREEN}✅ Backend configurado${NC}"
echo ""

# Frontend
echo -e "${YELLOW}>>> Configurando Frontend...${NC}"
cd frontend

# Instalar dependências
npm install

cd ..
echo -e "${GREEN}✅ Frontend configurado${NC}"
echo ""

echo "========================================="
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo "========================================="
echo ""
echo "Próximos passos:"
echo "1. Configure backend/.env com suas credenciais"
echo "2. Inicie o backend: cd backend && source ../venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Inicie o frontend: cd frontend && npm run dev"
