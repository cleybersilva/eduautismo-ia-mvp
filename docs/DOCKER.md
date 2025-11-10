# Guia de Configuração Docker - EduAutismo IA

## Visão Geral

Este projeto usa Docker e Docker Compose para fornecer um ambiente de desenvolvimento e produção consistente. A configuração inclui:

- **Backend FastAPI** (Python 3.11)
- **Frontend React** (Node 20 + Vite)
- **PostgreSQL** (Banco de Dados)
- **MongoDB** (Logs & Analytics)
- **Redis** (Cache & Sessões)
- **Ferramentas Admin** (Adminer, Mongo Express, Redis Commander)

## Pré-requisitos

- Docker Desktop 20.10+ ou Docker Engine 20.10+
- Docker Compose 2.0+
- Pelo menos 4GB de RAM disponível para Docker
- Pelo menos 10GB de espaço livre em disco

### Instalação

**macOS:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
Baixe de [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Início Rápido

### 1. Configuração Inicial

```bash
# Clone o repositório (se ainda não foi feito)
cd eduautismo-ia-mvp

# Copie o arquivo de ambiente
cp .env.example .env

# Edite .env e adicione sua chave da API OpenAI (OBRIGATÓRIO)
nano .env  # ou use seu editor preferido
```

**IMPORTANTE**: Adicione sua chave da API OpenAI no `.env`:
```env
OPENAI_API_KEY=sk-sua-chave-api-aqui
```

### 2. Iniciar Todos os Serviços

```bash
# Inicie tudo (primeira vez irá baixar as imagens)
docker-compose up -d

# Visualize os logs
docker-compose logs -f

# Verifique o status
docker-compose ps
```

### 3. Acesse a Aplicação

Quando todos os serviços estiverem saudáveis (pode levar 1-2 minutos):

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Documentação da API** | http://localhost:8000/docs | - |
| **Frontend** | http://localhost:5173 | - |
| **Adminer (UI do BD)** | http://localhost:8080 | Sistema: PostgreSQL<br>Servidor: postgres<br>Usuário: eduautismo<br>Senha: (do .env) |
| **Mongo Express** | http://localhost:8081 | admin / admin |
| **Redis Commander** | http://localhost:8082 | - |

### 4. Parar Serviços

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (deleta todos os dados!)
docker-compose down -v
```

## Arquitetura

### Serviços

```
┌─────────────────────────────────────────────────────────────┐
│                      Rede Docker                            │
│                   (eduautismo-network)                      │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │PostgreSQL│   │ MongoDB  │   │  Redis   │               │
│  │  :5432   │   │  :27017  │   │  :6379   │               │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘               │
│       │              │              │                       │
│       │         ┌────┴──────────────┴────┐                 │
│       │         │                        │                 │
│       └─────────┤   Backend FastAPI      │                 │
│                 │       :8000            │                 │
│                 └───────────┬────────────┘                 │
│                             │                              │
│                    ┌────────┴─────────┐                    │
│                    │                  │                    │
│              ┌─────┴─────┐      ┌────┴────┐               │
│              │  Frontend │      │  Admin  │               │
│              │   :5173   │      │  Tools  │               │
│              └───────────┘      └─────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Builds Multi-Estágio

Ambos os Dockerfiles usam builds multi-estágio para otimização:

**Dockerfile.api** (Backend):
1. `base` - Dependências do sistema
2. `dependencies` - Pacotes Python
3. `development` - Ferramentas dev + hot-reload
4. `builder` - Artefatos de build
5. `production` - Imagem de produção otimizada

**Dockerfile.web** (Frontend):
1. `base` - Configuração Node.js
2. `dependencies` - Pacotes NPM
3. `development` - Servidor dev com hot-reload
4. `builder` - Build de assets de produção
5. `production` - Nginx servindo arquivos estáticos

## Fluxo de Trabalho de Desenvolvimento

### Executando em Modo Desenvolvimento

```bash
# Inicie com hot-reload
docker-compose up -d

# Visualize logs em tempo real
docker-compose logs -f api
docker-compose logs -f frontend

# Faça alterações no código - elas serão recarregadas automaticamente!
# Backend: Edite arquivos em backend/
# Frontend: Edite arquivos em frontend/
```

### Executando Comandos Dentro dos Containers

```bash
# Shell do backend
docker-compose exec api bash

# Execute migrations
docker-compose exec api alembic upgrade head

# Execute testes
docker-compose exec api pytest

# Shell do frontend
docker-compose exec frontend sh

# Instale novo pacote NPM
docker-compose exec frontend npm install nome-do-pacote
```

### Operações de Banco de Dados

```bash
# Conecte ao PostgreSQL
docker-compose exec postgres psql -U eduautismo -d eduautismo_dev

# Backup do banco de dados
docker-compose exec postgres pg_dump -U eduautismo eduautismo_dev > backup.sql

# Restaure o banco de dados
docker-compose exec -T postgres psql -U eduautismo eduautismo_dev < backup.sql

# Resete o banco de dados (AVISO: deleta todos os dados)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec api alembic upgrade head
```

### Depuração

```bash
# Visualize logs do serviço
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres

# Verifique saúde do serviço
docker-compose ps

# Inspecione container
docker-compose exec api env
docker inspect eduautismo-api

# Verifique uso de recursos
docker stats
```

## Deploy em Produção

### Construindo Imagens de Produção

```bash
# Construa imagem de produção da API
docker build \
  --target production \
  --build-arg PYTHON_VERSION=3.11 \
  -t eduautismo-api:1.0.0 \
  -f Dockerfile.api .

# Construa imagem de produção do Frontend
docker build \
  --target production \
  --build-arg NODE_VERSION=20 \
  --build-arg VITE_API_URL=https://api.eduautismo.com \
  -t eduautismo-web:1.0.0 \
  -f Dockerfile.web .

# Tag para registry
docker tag eduautismo-api:1.0.0 seu-registry.com/eduautismo-api:1.0.0
docker tag eduautismo-web:1.0.0 seu-registry.com/eduautismo-web:1.0.0

# Push para registry
docker push seu-registry.com/eduautismo-api:1.0.0
docker push seu-registry.com/eduautismo-web:1.0.0
```

### docker-compose de Produção

Para produção, crie `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: seu-registry.com/eduautismo-api:1.0.0
    environment:
      ENV: production
      DEBUG: false
      # ... outras variáveis de ambiente de produção
    restart: always

  frontend:
    image: seu-registry.com/eduautismo-web:1.0.0
    ports:
      - "80:80"
    restart: always
```

Execute com:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Ferramentas Admin

### Adminer (UI do Banco de Dados)

Acesse em http://localhost:8080

Recursos:
- Navegar tabelas do banco de dados
- Executar consultas SQL
- Importar/Exportar dados
- Visualizar relacionamentos de tabelas

### Mongo Express (UI do MongoDB)

Acesse em http://localhost:8081

Recursos:
- Navegar coleções
- Executar consultas
- Visualizar documentos
- Estatísticas do banco de dados

### Redis Commander

Acesse em http://localhost:8082

Recursos:
- Visualizar chaves
- Executar comandos Redis
- Monitorar performance
- Gerenciar dados

**Nota**: Ferramentas admin são habilitadas apenas com o perfil `tools`:
```bash
docker-compose --profile tools up -d
```

## Variáveis de Ambiente

### Variáveis Obrigatórias

```env
OPENAI_API_KEY=sk-...          # OBRIGATÓRIO: Chave da API OpenAI
POSTGRES_PASSWORD=...           # Senha do banco de dados
SECRET_KEY=...                  # Segredo da aplicação (mín 32 caracteres)
JWT_SECRET_KEY=...              # Chave de assinatura JWT (mín 32 caracteres)
```

### Variáveis Opcionais

```env
ENV=development                 # Ambiente: development/staging/production
DEBUG=true                      # Habilitar modo debug
LOG_LEVEL=INFO                  # Nível de logging
AWS_ACCESS_KEY_ID=...          # Credenciais AWS (opcional)
SENTRY_DSN=...                 # Monitoramento Sentry (opcional)
```

Veja `.env.example` para lista completa.

## Solução de Problemas

### Serviços Não Iniciam

```bash
# Verifique logs
docker-compose logs

# Reconstrua imagens
docker-compose build --no-cache

# Remova volumes e reinicie
docker-compose down -v
docker-compose up -d
```

### Porta Já em Uso

```bash
# Encontre processo usando a porta
lsof -i :8000  # ou :5173, :5432, etc.

# Mate o processo ou mude a porta no .env
API_PORT=8001
```

### Problemas de Conexão com Banco de Dados

```bash
# Verifique se postgres está saudável
docker-compose ps postgres

# Verifique conectividade
docker-compose exec api pg_isready -h postgres -U eduautismo

# Resete banco de dados
docker-compose down -v postgres
docker-compose up -d postgres
```

### Falta de Memória

```bash
# Aumente o limite de memória do Docker nas configurações do Docker Desktop
# Recomendado: 4GB mínimo, 8GB ideal

# Ou reduza serviços
docker-compose up -d api postgres  # Apenas serviços essenciais
```

### Builds Lentos

```bash
# Use BuildKit (mais rápido)
DOCKER_BUILDKIT=1 docker-compose build

# Build em paralelo
docker-compose build --parallel

# Use cache do registry
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### Frontend Não Recarrega Automaticamente

```bash
# Verifique montagens de volume
docker-compose exec frontend ls -la /app

# Reinicie com estado limpo
docker-compose restart frontend
```

## Otimização de Performance

### Reduzir Tamanho da Imagem

```bash
# Use builds multi-estágio (já implementado)
# Remova arquivos desnecessários no .dockerignore

# Verifique tamanhos das imagens
docker images | grep eduautismo

# Analise camadas da imagem
docker history eduautismo-api:latest
```

### Builds Mais Rápidos

```bash
# Use BuildKit
export DOCKER_BUILDKIT=1

# Cache de dependências separadamente
# (já implementado nos Dockerfiles)

# Use cache de build do docker-compose
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### Performance de Rede

```bash
# Use rede host para dev local (apenas Linux)
network_mode: "host"

# Ou otimize rede bridge
docker network inspect eduautismo-network
```

## Melhores Práticas

### Segurança

1. **Nunca commite `.env`** - Sempre use `.env.example`
2. **Mude senhas padrão** - Use senhas fortes em produção
3. **Execute como não-root** - Já implementado nos Dockerfiles
4. **Escaneie imagens** - Use `docker scan eduautismo-api:latest`
5. **Mantenha imagens atualizadas** - Reconstrua regularmente com imagens base mais recentes

### Desenvolvimento

1. **Use volumes** - Para hot-reload durante desenvolvimento
2. **Health checks** - Monitore saúde do serviço
3. **Limites de recursos** - Defina limites de memória/CPU em produção
4. **Logging** - Use logging estruturado
5. **Backups** - Backups regulares do banco de dados

### Produção

1. **Use secrets** - Docker secrets ou gerenciamento externo de secrets
2. **Habilite monitoramento** - Sentry, Datadog ou similar
3. **Load balancing** - Use múltiplas réplicas
4. **Auto-restart** - Política `restart: always`
5. **Atualizações regulares** - Mantenha dependências atualizadas

## Referência de Comandos Comuns

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Visualizar logs
docker-compose logs -f [serviço]

# Reconstruir serviços
docker-compose build

# Reiniciar serviço
docker-compose restart [serviço]

# Executar comando
docker-compose exec [serviço] [comando]

# Visualizar uso de recursos
docker stats

# Limpar
docker system prune -a

# Visualizar redes
docker network ls

# Visualizar volumes
docker volume ls
```

## Recursos Adicionais

- [Documentação Docker](https://docs.docker.com/)
- [Documentação Docker Compose](https://docs.docker.com/compose/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Docker](https://vitejs.dev/guide/static-deploy.html)

## Suporte

Para problemas relacionados ao Docker:
1. Verifique logs: `docker-compose logs`
2. Revise esta documentação
3. Verifique [seção de solução de problemas](#solução-de-problemas)
4. Abra uma issue no GitHub

---

**Última Atualização**: 2025-01-09
**Versão Docker**: 24.0+
**Versão Docker Compose**: 2.0+
