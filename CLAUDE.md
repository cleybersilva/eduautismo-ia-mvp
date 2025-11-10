# 🧩 EduAutismo IA - Guia para Claude/IA

## 📋 Visão Geral do Projeto

**EduAutismo IA** é uma plataforma web que utiliza IA e ML para auxiliar professores na criação de atividades pedagógicas personalizadas para alunos com TEA (Transtorno do Espectro Autista).

## 🏗️ Arquitetura

### Stack Tecnológico
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite, React Router
- **IA/ML**: OpenAI GPT-4, scikit-learn
- **Infraestrutura**: AWS (ECS, RDS, DocumentDB, S3)

### Estrutura de Diretórios
```
eduautismo-ia-mvp/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints
│   │   ├── core/        # Config, database, security
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
├── ml_models/           # Modelos ML treinados
├── scripts/             # Scripts de automação
├── terraform/           # IaC
└── tests/              # Testes
```

## 🚀 Comandos Rápidos

### Desenvolvimento Local

```bash
# Backend
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev

# Ambos (com script)
./scripts/deployment/deploy-dev.sh
```

### Instalação Inicial

```bash
# Setup completo
./scripts/setup/install.sh

# Ou manual:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

## 🔑 Variáveis de Ambiente

```env
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/eduautismo_dev
MONGO_URL=mongodb://user:pass@localhost:27017
OPENAI_API_KEY=sk-your-key
SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
```

## 📦 Funcionalidades Principais

### 1. Gestão de Alunos
- Cadastro com perfil cognitivo e sensorial
- Avaliações comportamentais (CARS, AQ, SPM)
- Acompanhamento de evolução

### 2. Geração de Atividades (IA)
- Personalização baseada em perfil do aluno
- Uso de GPT-4 para conteúdo contextualizado
- Adaptação de dificuldade

### 3. Sistema de Recomendação (ML)
- Classificação de perfil comportamental
- Sugestões baseadas em similaridade
- Análise preditiva

### 4. Compliance LGPD
- Anonimização de dados
- Criptografia (AES-256, TLS 1.2+)
- Auditoria completa

## 🎯 Contexto de Desenvolvimento

### Quando Modificar Código

**Backend (FastAPI)**:
- Novos endpoints: `backend/app/api/routes/`
- Lógica de negócio: `backend/app/services/`
- Modelos de dados: `backend/app/models/`
- Validação: `backend/app/schemas/`

**Frontend (React)**:
- Páginas: `frontend/src/pages/`
- Componentes: `frontend/src/components/`
- Chamadas API: `frontend/src/services/`

**ML/IA**:
- Modelos: `ml_models/`
- Treinamento: `scripts/train_models.py`

### Padrões de Código

- **Python**: Black, Flake8, MyPy, isort
- **JavaScript**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Testes**: Coverage >80%

## 🧪 Testes

```bash
# Backend
pytest
pytest --cov=app --cov-report=html

# Frontend
npm test
npm run test:coverage
```

## 📚 Documentação API

- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Segurança

- JWT para autenticação
- Criptografia de dados sensíveis
- Rate limiting
- Validação de entrada (Pydantic)
- CORS configurado

## 🐛 Troubleshooting Comum

### Backend não inicia
```bash
# Verificar venv ativo
source venv/bin/activate

# Verificar dependências
pip install -r requirements.txt

# Verificar banco
docker-compose up -d postgres
```

### Frontend não compila
```bash
# Limpar cache
rm -rf node_modules package-lock.json
npm install

# Verificar Node.js
node --version  # Deve ser 18+
```

### Erro de importação
```bash
# Verificar estrutura de arquivos
# Todos os componentes devem ter export default
```

## 📝 Notas para IA

### Ao Criar Código
- Seguir estrutura existente
- Adicionar docstrings/comentários
- Incluir validação de entrada
- Considerar LGPD/segurança
- Adicionar testes quando relevante

### Ao Modificar Código
- Ler código existente primeiro
- Manter padrões do projeto
- Não remover código sem confirmar
- Atualizar documentação se necessário

### Ao Debugar
- Verificar logs: `logs/backend.log`, `logs/frontend.log`
- Testar endpoints: http://localhost:8000/docs
- Verificar console do navegador

## 🎓 Contexto Acadêmico

Este é um TCC de MBA em IA e Big Data pela USP, focado em:
- Aplicação prática de IA/ML em educação inclusiva
- Compliance com LGPD
- Arquitetura cloud-native (AWS)
- Boas práticas de engenharia de software

## 📞 Recursos

- **README Principal**: `README.md`
- **Docs Detalhados**: `docs/`
- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8000/docs

---

**Última atualização**: 2025-01-09
**Versão**: 1.0.0-MVP