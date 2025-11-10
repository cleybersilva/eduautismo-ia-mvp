# Guia de Testes - EduAutismo IA

## Visão Geral

Este documento fornece instruções completas para testar a API do EduAutismo IA, incluindo testes automatizados, testes manuais e exemplos de uso.

## Índice

- [Configuração Inicial](#configuração-inicial)
- [Testes Automatizados](#testes-automatizados)
- [Testes Manuais](#testes-manuais)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação](#autenticação)
- [Códigos de Status](#códigos-de-status)
- [Exemplos com cURL](#exemplos-com-curl)
- [Solução de Problemas](#solução-de-problemas)

## Configuração Inicial

### Pré-requisitos

1. **Serviços em execução**:
```bash
# Inicie todos os serviços com Docker
docker-compose up -d

# Verifique se todos estão saudáveis
docker-compose ps
```

2. **Ferramentas necessárias**:
- `curl` - Para testes de linha de comando
- `jq` - Para formatação JSON (opcional, mas recomendado)
- Postman ou Insomnia - Para testes manuais com interface gráfica

### Instalação de Ferramentas

**macOS**:
```bash
brew install curl jq
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install curl jq
```

**Windows (WSL)**:
```bash
sudo apt-get update
sudo apt-get install curl jq
```

## Testes Automatizados

### Script de Teste Principal

Criamos um script abrangente que testa todos os endpoints da API automaticamente.

#### Executar Todos os Testes

```bash
# Tornar o script executável (primeira vez)
chmod +x scripts/test_routes.sh

# Executar testes com API padrão (localhost:8000)
./scripts/test_routes.sh

# Executar testes com URL customizada
./scripts/test_routes.sh http://seu-servidor:8000
```

#### Saída Esperada

```
╔════════════════════════════════════════╗
║   EduAutismo IA - Route Testing       ║
╚════════════════════════════════════════╝
API URL: http://localhost:8000

========================================
0. Connectivity Check
========================================

✓ PASS - API is reachable

========================================
1. Root Endpoints
========================================

Testing: Root endpoint
✓ PASS - Root endpoint (Status: 200)
  Response: {"message":"Welcome to EduAutismo IA API"}

========================================
2. Health Check Endpoints
========================================

Testing: Basic health check
✓ PASS - Basic health check (Status: 200)
  Response: {"status":"healthy","timestamp":"2025-01-09T..."}

...

========================================
Test Summary
========================================

Total Tests:  20
Passed:       20
Failed:       0
Pass Rate:    100.0%

✓ All tests passed!
```

### Estrutura do Script de Teste

O script `test_routes.sh` inclui:

1. **Teste de Conectividade**: Verifica se a API está acessível
2. **Testes de Endpoints Raiz**: Testa o endpoint principal
3. **Testes de Health Check**: 5 endpoints de verificação de saúde
4. **Testes de Autenticação**: Fluxo completo (registro, login, refresh, reset)
5. **Testes de Recursos Protegidos**: Endpoints que requerem autenticação
6. **Testes de Documentação**: Swagger UI, ReDoc, OpenAPI schema

### Testes Unitários com Pytest

Para executar testes unitários:

```bash
# Dentro do container da API
docker-compose exec api pytest

# Com cobertura de código
docker-compose exec api pytest --cov=app --cov-report=html

# Apenas testes específicos
docker-compose exec api pytest tests/test_health.py
docker-compose exec api pytest tests/test_auth.py -v
```

### Integração Contínua (CI)

Adicione ao seu `.github/workflows/test.yml`:

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Start services
      run: docker-compose up -d

    - name: Wait for API
      run: |
        timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'

    - name: Run automated tests
      run: ./scripts/test_routes.sh

    - name: Run pytest
      run: docker-compose exec -T api pytest -v
```

## Testes Manuais

### Usando cURL

#### 1. Health Check

```bash
# Health check básico
curl http://localhost:8000/api/v1/health

# Health check detalhado
curl http://localhost:8000/api/v1/health/detailed

# Formatado com jq
curl -s http://localhost:8000/api/v1/health/detailed | jq .
```

#### 2. Autenticação - Registro

```bash
# Registrar novo usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "professor@escola.com",
    "password": "SenhaSegura123!",
    "full_name": "Professor Silva",
    "role": "teacher"
  }'

# Resposta esperada (201 Created):
{
  "id": "uuid-aqui",
  "email": "professor@escola.com",
  "full_name": "Professor Silva",
  "role": "teacher",
  "is_active": true,
  "created_at": "2025-01-09T10:30:00Z"
}
```

#### 3. Autenticação - Login

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=professor@escola.com&password=SenhaSegura123!"

# Resposta esperada (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Salvar token em variável (bash)
export ACCESS_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=professor@escola.com&password=SenhaSegura123!" | jq -r '.access_token')
```

#### 4. Usar Token de Autenticação

```bash
# Obter informações do usuário atual
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Resposta esperada (200 OK):
{
  "id": "uuid-aqui",
  "email": "professor@escola.com",
  "full_name": "Professor Silva",
  "role": "teacher",
  "is_active": true
}
```

#### 5. Refresh Token

```bash
# Renovar access token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "seu-refresh-token-aqui"
  }'

# Resposta esperada (200 OK):
{
  "access_token": "novo-token-aqui",
  "token_type": "bearer"
}
```

#### 6. Reset de Senha

```bash
# Solicitar reset de senha
curl -X POST http://localhost:8000/api/v1/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "professor@escola.com"
  }'

# Resposta esperada (200 OK):
{
  "message": "If the email exists, a password reset link has been sent"
}

# Confirmar reset de senha (com token recebido por email)
curl -X POST http://localhost:8000/api/v1/auth/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset-token-do-email",
    "new_password": "NovaSenhaSegura123!"
  }'
```

### Usando Postman

1. **Importar Coleção**: Importe o arquivo `postman_collection.json` (veja seção abaixo)
2. **Configurar Ambiente**:
   - Crie um ambiente "Local"
   - Adicione variável `base_url` = `http://localhost:8000`
   - Adicione variável `api_url` = `{{base_url}}/api/v1`

3. **Executar Requests**:
   - Requests estão organizados por categoria (Health, Auth, Students, etc.)
   - Tokens são salvos automaticamente após login
   - Usa variáveis de ambiente para flexibilidade

## Endpoints da API

### Resumo de Endpoints

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| **Root** |
| GET | `/` | Mensagem de boas-vindas | Não |
| **Health Checks** |
| GET | `/api/v1/health` | Health check básico | Não |
| GET | `/api/v1/health/detailed` | Health check com detalhes de componentes | Não |
| GET | `/api/v1/health/ready` | Readiness probe (Kubernetes) | Não |
| GET | `/api/v1/health/live` | Liveness probe (Kubernetes) | Não |
| GET | `/api/v1/health/startup` | Startup probe (Kubernetes) | Não |
| **Autenticação** |
| POST | `/api/v1/auth/register` | Registrar novo usuário | Não |
| POST | `/api/v1/auth/login` | Login (retorna tokens) | Não |
| POST | `/api/v1/auth/refresh` | Renovar access token | Não |
| POST | `/api/v1/auth/logout` | Logout (invalidar token) | Sim |
| GET | `/api/v1/auth/me` | Obter dados do usuário atual | Sim |
| POST | `/api/v1/auth/password-reset` | Solicitar reset de senha | Não |
| POST | `/api/v1/auth/password-reset/confirm` | Confirmar reset de senha | Não |
| **Documentação** |
| GET | `/docs` | Swagger UI interativo | Não |
| GET | `/redoc` | ReDoc documentação | Não |
| GET | `/openapi.json` | OpenAPI schema JSON | Não |

### Detalhes dos Endpoints

#### Health Check - Básico

```http
GET /api/v1/health
```

**Resposta (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T10:30:00.000Z"
}
```

#### Health Check - Detalhado

```http
GET /api/v1/health/detailed
```

**Resposta (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T10:30:00.000Z",
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "database": {
      "status": "up",
      "latency_ms": 12.34
    },
    "cache": {
      "status": "up",
      "latency_ms": 2.56
    },
    "openai": {
      "status": "up"
    }
  }
}
```

#### Registro de Usuário

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "string",
  "password": "string",
  "full_name": "string",
  "role": "teacher" | "admin"
}
```

**Resposta (201 Created)**:
```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true,
  "created_at": "2025-01-09T10:30:00Z",
  "updated_at": "2025-01-09T10:30:00Z"
}
```

**Erros Possíveis**:
- `400 Bad Request` - Email já cadastrado
- `422 Unprocessable Entity` - Dados inválidos

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=email@exemplo.com&password=senha
```

**Resposta (200 OK)**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Erros Possíveis**:
- `401 Unauthorized` - Credenciais incorretas
- `422 Unprocessable Entity` - Dados inválidos

#### Obter Usuário Atual

```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**Resposta (200 OK)**:
```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true,
  "created_at": "2025-01-09T10:30:00Z"
}
```

**Erros Possíveis**:
- `401 Unauthorized` - Token inválido ou expirado

## Autenticação

### Fluxo de Autenticação

```
1. Registro → POST /auth/register
   ↓
2. Login → POST /auth/login
   ↓ (recebe access_token e refresh_token)
3. Usar Token → Headers: Authorization: Bearer {access_token}
   ↓ (quando access_token expira)
4. Renovar → POST /auth/refresh
   ↓ (recebe novo access_token)
5. Continuar usando novo token
```

### Tipos de Token

- **Access Token**:
  - Validade: 30 minutos
  - Uso: Autenticação em todas as requisições protegidas
  - Header: `Authorization: Bearer {access_token}`

- **Refresh Token**:
  - Validade: 7 dias
  - Uso: Renovar access token sem fazer login novamente
  - Endpoint: `POST /auth/refresh`

### Segurança

- Senhas são hash com bcrypt
- Tokens JWT assinados com chave secreta
- HTTPS recomendado em produção
- Tokens armazenados com segurança (não em localStorage)

## Códigos de Status

### Success (2xx)

| Código | Nome | Uso |
|--------|------|-----|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 204 | No Content | Requisição bem-sucedida, sem conteúdo |

### Client Errors (4xx)

| Código | Nome | Uso |
|--------|------|-----|
| 400 | Bad Request | Dados inválidos ou requisição malformada |
| 401 | Unauthorized | Autenticação necessária ou inválida |
| 403 | Forbidden | Sem permissão para acessar recurso |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Validação de dados falhou |
| 429 | Too Many Requests | Rate limit excedido |

### Server Errors (5xx)

| Código | Nome | Uso |
|--------|------|-----|
| 500 | Internal Server Error | Erro no servidor |
| 503 | Service Unavailable | Serviço temporariamente indisponível |

## Exemplos com cURL

### Script Completo de Teste

```bash
#!/bin/bash
# Script de teste completo da API

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

# 1. Verificar se API está online
echo "1. Verificando conectividade..."
curl -s $API_URL/health | jq .

# 2. Registrar novo usuário
echo -e "\n2. Registrando novo usuário..."
TIMESTAMP=$(date +%s)
EMAIL="test_${TIMESTAMP}@example.com"
PASSWORD="SecurePass123!"

REGISTER_RESPONSE=$(curl -s -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"full_name\": \"Test User\",
    \"role\": \"teacher\"
  }")

echo $REGISTER_RESPONSE | jq .

# 3. Fazer login
echo -e "\n3. Fazendo login..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token')

echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."

# 4. Obter dados do usuário
echo -e "\n4. Obtendo dados do usuário..."
curl -s $API_URL/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .

# 5. Renovar token
echo -e "\n5. Renovando token..."
curl -s -X POST $API_URL/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | jq .

echo -e "\n✅ Todos os testes completados!"
```

Salve como `scripts/quick_test.sh` e execute:

```bash
chmod +x scripts/quick_test.sh
./scripts/quick_test.sh
```

## Solução de Problemas

### Erro: "Connection refused"

```bash
# Verifique se serviços estão rodando
docker-compose ps

# Inicie os serviços
docker-compose up -d

# Aguarde alguns segundos e teste novamente
sleep 10
curl http://localhost:8000/api/v1/health
```

### Erro: "401 Unauthorized"

```bash
# Verifique se o token é válido
echo $ACCESS_TOKEN

# Se vazio, faça login novamente
# Se expirado, use refresh token

# Renovar token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

### Erro: "422 Unprocessable Entity"

Verifique se os dados enviados correspondem ao schema esperado:

```bash
# Ver documentação interativa
open http://localhost:8000/docs

# Verificar schema do endpoint específico
curl http://localhost:8000/openapi.json | jq '.paths."/api/v1/auth/register"'
```

### Erro: "Database connection failed"

```bash
# Verifique status do PostgreSQL
docker-compose ps postgres

# Reinicie o banco de dados
docker-compose restart postgres

# Verifique logs
docker-compose logs postgres
```

### Health Check Retorna "degraded" ou "unhealthy"

```bash
# Health check detalhado para identificar componente com problema
curl http://localhost:8000/api/v1/health/detailed | jq .

# Verifique logs da API
docker-compose logs api

# Reinicie serviços problemáticos
docker-compose restart postgres redis mongodb
```

## Ferramentas Recomendadas

### 1. HTTPie

Alternativa mais amigável ao cURL:

```bash
# Instalação
pip install httpie

# Exemplos
http GET localhost:8000/api/v1/health
http POST localhost:8000/api/v1/auth/login username=email@example.com password=senha
http GET localhost:8000/api/v1/auth/me "Authorization: Bearer $TOKEN"
```

### 2. Postman

- Interface gráfica intuitiva
- Coleções de requisições
- Ambientes para dev/staging/prod
- Testes automatizados
- Import: `postman_collection.json`

### 3. Insomnia

- Alternativa ao Postman
- Interface mais simples
- Suporte para GraphQL também
- Gratuito e open-source

### 4. Swagger UI

- Já incluído na API
- Acesse: http://localhost:8000/docs
- Teste endpoints diretamente no navegador
- Documentação interativa

## Cobertura de Testes

### Verificar Cobertura Atual

```bash
# Executar testes com cobertura
docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term

# Abrir relatório HTML
open backend/htmlcov/index.html
```

### Meta de Cobertura

- **Mínimo**: 80% para código crítico (autenticação, pagamentos)
- **Recomendado**: 70% cobertura geral
- **Excelente**: 90%+ cobertura geral

## Integração com IDE

### VS Code

Instale extensões:
- REST Client
- Thunder Client
- Postman

Exemplo de arquivo `.http`:

```http
### Health Check
GET http://localhost:8000/api/v1/health

### Register
POST http://localhost:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "full_name": "Test User",
  "role": "teacher"
}

### Login
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=SecurePass123!

### Get User (use token from login)
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer {{access_token}}
```

## Recursos Adicionais

- [Documentação FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JWT.io](https://jwt.io/) - Decodificar tokens JWT
- [ReqBin](https://reqbin.com/) - Testar APIs online

## Suporte

Para problemas com testes:
1. Verifique se serviços estão rodando: `docker-compose ps`
2. Verifique logs: `docker-compose logs api`
3. Consulte documentação interativa: http://localhost:8000/docs
4. Revise esta documentação
5. Abra uma issue no GitHub

---

**Última Atualização**: 2025-01-09
**Versão da API**: 1.0.0
