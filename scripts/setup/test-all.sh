#!/bin/bash

echo "========================================="
echo "🧪 Executando Todos os Testes"
echo "========================================="
echo ""

# Backend Tests
echo ">>> Backend Tests..."
cd backend
source ../venv/bin/activate
pytest tests/ -v --cov=app
BACKEND_EXIT=$?
cd ..
echo ""

# Frontend Tests
echo ">>> Frontend Tests..."
cd frontend
npm run test
FRONTEND_EXIT=$?
cd ..
echo ""

# Resultado
echo "========================================="
if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
    exit 0
else
    echo "❌ Alguns testes falharam"
    exit 1
fi
