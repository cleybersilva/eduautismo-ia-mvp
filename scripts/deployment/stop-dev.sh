#!/bin/bash

echo "========================================="
echo "🛑 Parando Serviços de Desenvolvimento"
echo "========================================="
echo ""

# Parar por PID salvo
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo ">>> Parando Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend já estava parado"
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo ">>> Parando Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend já estava parado"
    rm .frontend.pid
fi

# Garantir que processos foram mortos
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo ""
echo "✅ Serviços parados!"
