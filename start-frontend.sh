#!/bin/bash

cd /mnt/d/ENGINEER/VS_Code/eduautismo-ia-mvp/frontend

echo "========================================="
echo "🚀 Iniciando Frontend - EduAutismo IA"
echo "========================================="
echo ""

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo ">>> node_modules não encontrado. Instalando dependências..."
    npm install --legacy-peer-deps
    echo ""
fi

# Verificar se vite existe
if [ ! -f "node_modules/.bin/vite" ]; then
    echo "❌ Vite não encontrado. Reinstalando..."
    rm -rf node_modules package-lock.json
    npm install --legacy-peer-deps
    echo ""
fi

# Iniciar vite
echo ">>> Iniciando Vite..."
echo ""
npx vite --host 0.0.0.0 --port 5173

