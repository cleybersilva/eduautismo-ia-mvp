#!/bin/bash

echo "========================================="
echo "🚀 Deploy para Desenvolvimento"
echo "========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado"
    echo "Execute primeiro: ./scripts/setup/install.sh"
    exit 1
fi

# Limpar processos anteriores
echo ">>> Limpando processos anteriores..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Backend
echo ">>> Iniciando Backend..."
cd backend
source ../venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

# Aguardar backend iniciar
sleep 3

# Frontend
echo ">>> Iniciando Frontend..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

# Salvar PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "========================================="
echo "✅ Serviços iniciados!"
echo "========================================="
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:5173"
echo "📍 API Docs: http://localhost:8000/api/v1/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 Para parar: ./scripts/deployment/stop-dev.sh"
echo "========================================="
