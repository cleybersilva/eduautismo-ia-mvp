#!/bin/bash
# =============================================================================
# EduAutismo IA - Setup Enhanced Features
# =============================================================================
#
# Script para configurar funcionalidades avançadas:
# - Cache Redis
# - Sistema de Notificações
# - Exportação CSV/Excel
#
# Uso: ./scripts/setup_enhanced_features.sh
#
# Autor: Claude Code
# Data: 2025-11-24
# =============================================================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo "=================================================="
echo "  EduAutismo IA - Enhanced Features Setup"
echo "=================================================="
echo ""

# 1. Verificar dependências
log_info "Verificando dependências do sistema..."

command -v python3 >/dev/null 2>&1 || { log_error "Python3 não encontrado. Instale Python 3.11+"; exit 1; }
command -v docker >/dev/null 2>&1 || { log_error "Docker não encontrado. Instale Docker"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { log_error "Docker Compose não encontrado. Instale Docker Compose"; exit 1; }

log_success "Dependências verificadas"

# 2. Verificar .env
log_info "Verificando arquivo .env..."

if [ ! -f ".env" ]; then
    log_warning ".env não encontrado. Criando a partir do .env.example..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_success ".env criado"
    else
        log_error ".env.example não encontrado"
        exit 1
    fi
fi

# 3. Verificar/Adicionar variáveis Redis
log_info "Verificando configurações do Redis..."

if ! grep -q "REDIS_URL" .env; then
    log_warning "REDIS_URL não encontrado. Adicionando..."
    echo "" >> .env
    echo "# Redis Cache" >> .env
    echo "REDIS_URL=redis://:eduautismo_dev_pass@localhost:6379/0" >> .env
    echo "REDIS_ENABLED=true" >> .env
    echo "REDIS_TTL=3600" >> .env
    log_success "Variáveis Redis adicionadas"
fi

# 4. Instalar dependências Python
log_info "Instalando dependências Python..."

if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate

log_info "Instalando requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

log_info "Instalando dependências avançadas..."
pip install -q redis openpyxl

log_success "Dependências instaladas"

# 5. Iniciar serviços Docker
log_info "Iniciando serviços Docker..."

docker-compose up -d postgres mongodb redis

log_info "Aguardando serviços ficarem prontos..."
sleep 10

# Verificar saúde dos serviços
if docker-compose ps | grep -q "unhealthy"; then
    log_error "Alguns serviços não estão saudáveis"
    docker-compose ps
    exit 1
fi

log_success "Serviços Docker iniciados"

# 6. Aplicar migrations
log_info "Aplicando migrations do banco de dados..."

export DATABASE_URL="postgresql://eduautismo:eduautismo_dev_pass@localhost:5432/eduautismo_dev"

alembic upgrade head

log_success "Migrations aplicadas"

# 7. Verificar conexão Redis
log_info "Testando conexão Redis..."

python3 << EOF
import redis
try:
    r = redis.from_url('redis://:eduautismo_dev_pass@localhost:6379/0')
    r.ping()
    print("✅ Redis conectado com sucesso")
except Exception as e:
    print(f"❌ Erro ao conectar Redis: {e}")
    exit(1)
EOF

log_success "Redis operacional"

# 8. Testar imports Python
log_info "Validando imports Python..."

python3 << EOF
try:
    from app.core.cache import cache_manager
    from app.models.notification import Notification
    from app.services.notification_service import NotificationService
    from app.services.export_service import ExportService
    print("✅ Todos os imports funcionando")
except ImportError as e:
    print(f"❌ Erro de import: {e}")
    exit(1)
EOF

log_success "Imports validados"

# 9. Seed de dados de teste (opcional)
read -p "Deseja criar dados de teste para notificações? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    log_info "Criando dados de teste..."

    if [ -f "scripts/seed_notifications.py" ]; then
        python3 scripts/seed_notifications.py
        log_success "Dados de teste criados"
    else
        log_warning "Script seed_notifications.py não encontrado"
    fi
fi

# 10. Exibir URLs úteis
echo ""
echo "=================================================="
log_success "Setup concluído com sucesso!"
echo "=================================================="
echo ""
echo "🌐 URLs disponíveis:"
echo "   - API:               http://localhost:8000"
echo "   - API Docs:          http://localhost:8000/docs"
echo "   - Health Check:      http://localhost:8000/api/v1/health"
echo "   - Redis Commander:   http://localhost:8082"
echo "   - Adminer:           http://localhost:8080"
echo ""
echo "📋 Endpoints novos:"
echo "   - Notificações:      http://localhost:8000/api/v1/notifications"
echo "   - Export CSV:        http://localhost:8000/api/v1/export/pending-review/csv"
echo "   - Export Excel:      http://localhost:8000/api/v1/export/pending-review/excel"
echo ""
echo "🚀 Para iniciar a API:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📖 Documentação completa: ENHANCED_FEATURES_README.md"
echo "=================================================="
