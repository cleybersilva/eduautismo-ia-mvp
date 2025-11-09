# Criar um script para facilitar
cat > activate.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "✅ Ambiente virtual ativado!"
echo "📍 Python: $(which python)"
echo "📦 Pip: $(pip --version)"
EOF

chmod +x activate.sh
echo "✅ Script activate.sh criado com sucesso!"
echo "📄 Para ativar o ambiente virtual, execute: ./activate.sh"
