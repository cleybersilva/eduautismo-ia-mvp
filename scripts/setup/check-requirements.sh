#!/bin/bash

echo "========================================="
echo "   Verificação de Requisitos"
echo "========================================="
echo ""

# Python
echo ">>> Python:"
if command -v python3 &> /dev/null; then
    echo "✅ $(python3 --version)"
else
    echo "❌ Python3 não instalado"
fi
echo ""

# pip
echo ">>> pip:"
if command -v pip &> /dev/null; then
    echo "✅ $(pip --version | cut -d' ' -f1-2)"
else
    echo "❌ pip não instalado"
fi
echo ""

# Node.js
echo ">>> Node.js:"
if command -v node &> /dev/null; then
    echo "✅ $(node --version)"
else
    echo "❌ Node.js não instalado"
fi
echo ""

# npm
echo ">>> npm:"
if command -v npm &> /dev/null; then
    echo "✅ $(npm --version)"
else
    echo "❌ npm não instalado"
fi
echo ""

# Git
echo ">>> Git:"
if command -v git &> /dev/null; then
    echo "✅ $(git --version)"
else
    echo "⚠️  Git não instalado"
fi
echo ""

# PostgreSQL (opcional)
echo ">>> PostgreSQL:"
if command -v psql &> /dev/null; then
    echo "✅ $(psql --version)"
else
    echo "⚠️  PostgreSQL não instalado (opcional para dev local)"
fi
echo ""

# Redis (opcional)
echo ">>> Redis:"
if command -v redis-cli &> /dev/null; then
    echo "✅ $(redis-cli --version)"
else
    echo "⚠️  Redis não instalado (opcional para dev local)"
fi
echo ""

# Docker (opcional)
echo ">>> Docker:"
if command -v docker &> /dev/null; then
    echo "✅ $(docker --version)"
else
    echo "⚠️  Docker não instalado (opcional)"
fi
echo ""

# AWS CLI (opcional)
echo ">>> AWS CLI:"
if command -v aws &> /dev/null; then
    echo "✅ $(aws --version)"
else
    echo "⚠️  AWS CLI não instalado (necessário para deploy em produção)"
fi
echo ""

echo "========================================="
echo "Legenda:"
echo "✅ = Instalado"
echo "❌ = Necessário e não instalado"
echo "⚠️  = Opcional"
echo "========================================="
