# 🧪 Referência Rápida de Testes - EduAutismo IA

## 📋 Checklist Pré-Teste

- [ ] Docker Desktop está rodando
- [ ] Serviços estão iniciados: `docker-compose ps`
- [ ] API está acessível: `curl http://localhost:8000/health`

## 🚀 Comandos Rápidos

### Iniciar Ambiente

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar saúde
docker-compose ps
```

### Executar Testes

```bash
# Teste automatizado completo
./scripts/test_routes.sh

# Teste com pytest
docker-compose exec api pytest -v

# Teste com cobertura
docker-compose exec api pytest --cov=app --cov-report=term
```

### Logs

```bash
# Ver logs da API
docker-compose logs -f api

# Ver logs do banco
docker-compose logs -f postgres
```

## 📊 Endpoints Principais

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Registro
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "role": "teacher"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePass123!"
```

### Obter Usuário (com token)
```bash
# Salvar token primeiro
export TOKEN="seu-access-token-aqui"

# Fazer request
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 Ferramentas

### Postman
1. Importar: `postman_collection.json`
2. Configurar variáveis:
   - `base_url`: `http://localhost:8000`
   - `test_email`: `test@example.com`
   - `test_password`: `SecurePass123!`

### Swagger UI
- URL: http://localhost:8000/docs
- Teste interativamente no navegador

### ReDoc
- URL: http://localhost:8000/redoc
- Documentação alternativa

## 🐛 Troubleshooting Rápido

### API não responde
```bash
docker-compose restart api
docker-compose logs api
```

### Banco de dados com problemas
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Resetar tudo
```bash
docker-compose down -v
docker-compose up -d
```

### Token expirado
```bash
# Use refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "seu-refresh-token"}'
```

## 📈 Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Autenticação necessária |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Internal Server Error - Erro no servidor |

## 🔐 Fluxo de Autenticação

```
1. Registro → POST /auth/register
2. Login    → POST /auth/login (retorna access_token + refresh_token)
3. Usar     → Header: Authorization: Bearer {access_token}
4. Renovar  → POST /auth/refresh (quando expirar)
```

## 📁 Arquivos Importantes

- `scripts/test_routes.sh` - Script de teste automatizado
- `docs/TESTING.md` - Documentação completa de testes
- `postman_collection.json` - Coleção Postman
- `.env` - Variáveis de ambiente

## 🔗 Links Úteis

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Adminer (DB)**: http://localhost:8080
- **Mongo Express**: http://localhost:8081
- **Redis Commander**: http://localhost:8082

## 📞 Precisa de Mais Ajuda?

- Documentação completa: [docs/TESTING.md](docs/TESTING.md)
- Guia Docker: [docs/DOCKER.md](docs/DOCKER.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)

---

**💡 Dica**: Salve este arquivo nos favoritos para acesso rápido durante desenvolvimento!
