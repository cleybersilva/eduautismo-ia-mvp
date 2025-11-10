#!/bin/bash

echo "========================================="
echo "  EduAutismo IA - Verificacao"
echo "========================================="
echo ""

# 1. Verificar diretório
echo ">>> Diretorio Atual:"
pwd
echo ""

# 2. Verificar venv
echo ">>> Ambiente Virtual:"
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[ERRO] Ambiente virtual NAO esta ativo"
    echo "Execute: source venv/bin/activate"
    exit 1
else
    echo "[OK] Ambiente virtual ativo"
    echo "     $VIRTUAL_ENV"
fi
echo ""

# 3. Verificar Python
echo ">>> Python:"
python --version
which python
echo ""

# 4. Verificar pip
echo ">>> Pip:"
pip --version
echo ""

# 5. Contar pacotes
echo ">>> Contagem de Pacotes:"
if [ -f "backend/requirements.txt" ]; then
    REQ_COUNT=$(grep -v "^#" backend/requirements.txt | grep -v "^$" | wc -l)
    echo "Pacotes no requirements.txt: $REQ_COUNT"
else
    echo "[AVISO] requirements.txt nao encontrado"
fi

INSTALLED_COUNT=$(pip list | tail -n +3 | wc -l)
echo "Pacotes instalados no venv: $INSTALLED_COUNT"
echo ""

# 6. Verificar pacotes principais
echo ">>> Verificando Pacotes Principais:"
PACKAGES="fastapi uvicorn sqlalchemy boto3 pandas numpy scikit-learn pytest"

for pkg in $PACKAGES; do
    if pip show "$pkg" > /dev/null 2>&1; then
        VERSION=$(pip show "$pkg" | grep "Version:" | awk '{print $2}')
        echo "[OK] $pkg ($VERSION)"
    else
        echo "[ERRO] $pkg NAO instalado"
    fi
done
echo ""

# 7. Verificar estrutura
echo ">>> Estrutura de Diretorios:"
for dir in backend backend/app frontend docs scripts; do
    if [ -d "$dir" ]; then
        echo "[OK] $dir/"
    else
        echo "[ERRO] $dir/ NAO encontrado"
    fi
done
echo ""

# 8. Testar imports
echo ">>> Testando Imports Python:"
python << PYEND
try:
    import fastapi
    print("[OK] FastAPI importado")
except ImportError:
    print("[ERRO] Nao foi possivel importar FastAPI")

try:
    import uvicorn
    print("[OK] Uvicorn importado")
except ImportError:
    print("[ERRO] Nao foi possivel importar Uvicorn")

try:
    import sqlalchemy
    print("[OK] SQLAlchemy importado")
except ImportError:
    print("[ERRO] Nao foi possivel importar SQLAlchemy")
PYEND

echo ""
echo "========================================="
echo "  Verificacao Concluida!"
echo "========================================="
