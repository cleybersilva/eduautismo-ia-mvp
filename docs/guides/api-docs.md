# 📡 Documentação da API

## Visão Geral

A API do EduAutismo IA é construída usando FastAPI e fornece endpoints para gerenciamento de usuários, atividades, avaliações e integração com serviços de ML.

## Base URL

```
Desenvolvimento: http://localhost:8000
Produção: https://api.eduautismo.com
```

## Autenticação

A API usa autenticação JWT. Inclua o token no header de todas as requisições:

```http
Authorization: Bearer <seu_token_jwt>
```

## Endpoints

### Autenticação

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "usuario@exemplo.com",
    "password": "senha123"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### Usuários

#### Criar Usuário
```http
POST /api/users
Content-Type: application/json

{
    "name": "Nome do Usuário",
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "role": "teacher"
}
```

#### Listar Usuários
```http
GET /api/users
Authorization: Bearer <token>
```

### Estudantes

#### Criar Estudante
```http
POST /api/students
Content-Type: application/json

{
    "name": "Nome do Estudante",
    "birth_date": "2015-01-01",
    "diagnosis": "TEA",
    "education_level": "elementary"
}
```

#### Listar Estudantes
```http
GET /api/students
Authorization: Bearer <token>
```

### Atividades

#### Criar Atividade
```http
POST /api/activities
Content-Type: application/json

{
    "title": "Nome da Atividade",
    "description": "Descrição detalhada",
    "difficulty": "medium",
    "category": "math"
}
```

#### Listar Atividades
```http
GET /api/activities
Authorization: Bearer <token>
```

### Avaliações

#### Criar Avaliação
```http
POST /api/assessments
Content-Type: application/json

{
    "student_id": "123",
    "activity_id": "456",
    "score": 85,
    "duration": 300,
    "behaviors": ["focused", "calm"]
}
```

#### Listar Avaliações
```http
GET /api/assessments
Authorization: Bearer <token>
```

## Códigos de Status

- 200: Sucesso
- 201: Criado com sucesso
- 400: Requisição inválida
- 401: Não autorizado
- 403: Proibido
- 404: Não encontrado
- 500: Erro interno do servidor

## Rate Limiting

- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário

## Paginação

Use os parâmetros `skip` e `limit` para paginação:

```http
GET /api/activities?skip=0&limit=10
```

## Filtragem

Use query parameters para filtrar resultados:

```http
GET /api/students?age_min=6&age_max=10
GET /api/activities?difficulty=easy&category=math
```

## Ordenação

Use o parâmetro `sort` para ordenar resultados:

```http
GET /api/assessments?sort=date_desc
GET /api/activities?sort=difficulty_asc
```

## Websockets

### Notificações em Tempo Real
```http
WS /ws/notifications
Authorization: Bearer <token>
```

## Erros

Exemplo de resposta de erro:

```json
{
    "error": {
        "code": "INVALID_INPUT",
        "message": "Email inválido",
        "details": {
            "field": "email",
            "reason": "format"
        }
    }
}
```

## Links Úteis

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [Postman Collection](../postman_collection.json)
- [Guia de Desenvolvimento](./development-guide.md)