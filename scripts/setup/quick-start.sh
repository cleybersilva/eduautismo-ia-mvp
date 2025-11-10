#!/bin/bash

# Quick start - Inicia tudo rapidamente

echo "========================================="
echo "⚡ EduAutismo IA - Quick Start"
echo "========================================="
echo ""

cd /mnt/d/ENGINEER/VS_Code/eduautismo-ia-mvp

# Verificar instalação
if [ ! -d "venv" ]; then
    echo ">>> Primeira execução - Instalando..."
    ./scripts/setup/install.sh
fi

# Criar diretório de logs
mkdir -p logs

# Ativar venv
source venv/bin/activate

# Verificar backend
echo ">>> Verificando Backend..."
cd backend
python -c "from app.main import app; print('✅ Backend OK')" 2>/dev/null || {
    echo "❌ Erro no backend"
    cd ..
    exit 1
}
cd ..

# Iniciar serviços
./scripts/deployment/deploy-dev.sh

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 5

# Testar serviços
echo ""
echo ">>> Testando Backend..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend respondendo" || echo "⚠️  Backend não respondeu"

echo ""
echo "========================================="
echo "✅ Sistema pronto!"
echo "========================================="
