# 🚀 Guia de Início Rápido - EduAutismo IA

Coloque a aplicação em funcionamento em menos de 5 minutos!

## Pré-requisitos

✅ Docker Desktop instalado ([Download](https://www.docker.com/products/docker-desktop))
✅ Chave da API OpenAI ([Obtenha aqui](https://platform.openai.com/api-keys))
✅ 4GB+ de RAM disponível
✅ 10GB+ de espaço livre em disco

## Passo 1: Configurar Ambiente (1 minuto)

```bash
# Copie o template de ambiente
cp .env.example .env

# Edite .env e adicione sua chave da API OpenAI
# Obrigatório: Altere OPENAI_API_KEY=sk-sua-chave-aqui
nano .env  # ou use seu editor preferido
```

**IMPORTANTE**: Você DEVE adicionar sua chave da API OpenAI no `.env` para a aplicação funcionar!

## Passo 2: Iniciar Serviços (2-3 minutos)

```bash
# Usando Make (recomendado)
make dev

# OU usando docker-compose diretamente
docker-compose up -d
```

A primeira vez levará 2-3 minutos para baixar imagens e construir containers.

## Passo 3: Verificar Serviços (30 segundos)

```bash
# Verifique se todos os serviços estão saudáveis
make health

# OU verifique manualmente
docker-compose ps
```

Todos os serviços devem mostrar status "healthy".

## Passo 4: Acessar a Aplicação

### 🎯 Serviços Principais

| O Que | URL | Descrição |
|-------|-----|-----------|
| **Documentação da API** | http://localhost:8000/docs | Interface Swagger interativa |
| **Frontend** | http://localhost:5173 | Aplicação React |
| **Health Check** | http://localhost:8000/health | Status da API |

### 🛠️ Ferramentas Admin (Opcional)

Acesse interfaces de gerenciamento de banco de dados:

| Ferramenta | URL | Credenciais |
|------------|-----|-------------|
| **Adminer** (PostgreSQL) | http://localhost:8080 | Sistema: PostgreSQL<br>Servidor: postgres<br>Usuário: eduautismo<br>Senha: (do .env) |
| **Mongo Express** | http://localhost:8081 | admin / admin |
| **Redis Commander** | http://localhost:8082 | Sem credenciais necessárias |

Para habilitar ferramentas admin:
```bash
docker-compose --profile tools up -d
```

## Passo 5: Verificar se Tudo Funciona

### Testar API

```bash
# Usando curl
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy"}
```

### Testar Banco de Dados

```bash
# Execute migrations
make db-migrate

# OU
docker-compose exec api alembic upgrade head
```

### Executar Testes

```bash
# Execute todos os testes
make test

# OU
docker-compose exec api pytest -v
```

## Comandos Comuns

```bash
# Visualizar logs
make logs              # Todos os serviços
make logs-api          # Apenas API
make logs-frontend     # Apenas Frontend

# Parar serviços
make stop

# Reiniciar serviços
make restart

# Abrir shell da API
make shell-api

# Executar migrations do banco de dados
make db-migrate

# Mostrar todos os comandos disponíveis
make help
```

## Solução de Problemas

### Serviços não iniciam?

```bash
# Verifique logs para erros
docker-compose logs

# Reconstrua tudo
docker-compose down -v
docker-compose up -d --build
```

### Porta já em uso?

Edite `.env` e mude a porta:
```env
API_PORT=8001  # Em vez de 8000
FRONTEND_PORT=5174  # Em vez de 5173
```

### Não consegue conectar ao banco de dados?

```bash
# Verifique se postgres está rodando
docker-compose ps postgres

# Reinicie postgres
docker-compose restart postgres

# Aguarde alguns segundos para ficar saudável
docker-compose ps
```

### Falta de memória?

Aumente a memória do Docker no Docker Desktop:
- Configurações → Recursos → Memória
- Defina para pelo menos 4GB

## Próximos Passos

### 1. Configurar a Aplicação

Edite `backend/.env.example` para configurações específicas do backend:
```bash
cd backend
cp .env.example .env
nano .env
```

### 2. Configurar Banco de Dados

```bash
# Execute migrations
make db-migrate

# Popule com dados de exemplo (opcional)
docker-compose exec api python scripts/seed_database.py
```

### 3. Explorar a API

Visite http://localhost:8000/docs para explorar todos os endpoints:
- Gerenciamento de alunos
- Geração de atividades
- Avaliações
- Autenticação

### 4. Começar Desenvolvimento

```bash
# Código do backend está em backend/app/
# Código do frontend está em frontend/src/

# Alterações serão recarregadas automaticamente graças ao hot-reload!
```

## Fluxo de Trabalho de Desenvolvimento

### Fazendo Alterações

1. **Backend**: Edite arquivos em `backend/app/`
   - Alterações recarregam automaticamente (hot-reload habilitado)
   - Verifique logs: `make logs-api`

2. **Frontend**: Edite arquivos em `frontend/src/`
   - Alterações recarregam automaticamente (Vite HMR habilitado)
   - Verifique logs: `make logs-frontend`

### Adicionando Dependências

```bash
# Backend (Python)
docker-compose exec api pip install nome-do-pacote
# Então atualize requirements.txt
docker-compose exec api pip freeze > backend/requirements.txt

# Frontend (NPM)
docker-compose exec frontend npm install nome-do-pacote
```

### Executando Comandos

```bash
# Shell da API
make shell-api
# Dentro do container:
# - pytest
# - alembic upgrade head
# - python scripts/seu_script.py

# Shell do banco de dados
make db-shell
# Dentro do postgres:
# - \dt (listar tabelas)
# - SELECT * FROM students;
```

## Deploy em Produção

Para guia de deploy em produção, veja:
- [Guia Docker](docs/DOCKER.md)
- [Guia de Deploy](docs/deployment.md) (se disponível)

Ou use:
```bash
# Construa imagens de produção
make build-prod

# Inicie stack de produção
make prod
```

## Precisa de Ajuda?

- 📖 [Guia Completo Docker](docs/DOCKER.md)
- 📊 [Validação de Estrutura](docs/structure-validation.md)
- 📝 [README Principal](README.md)
- 🤖 [Guia Claude](CLAUDE.md)

## Links Úteis

- **Docs da API**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**Tempo para começar**: ~5 minutos
**Pré-requisitos**: Docker + Chave da API OpenAI
**Status**: ✅ Pronto para desenvolvimento

Bom código! 🎉
