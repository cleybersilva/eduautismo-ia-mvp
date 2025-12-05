# API Documentation - Enhanced Features

> **Versão**: 1.0.0
> **Data**: 2025-11-24
> **Autor**: Claude Code

Documentação completa dos novos endpoints implementados para Cache Redis, Sistema de Notificações e Exportação de Dados.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [API de Notificações](#api-de-notificações)
4. [API de Exportação](#api-de-exportação)
5. [Modelos de Dados](#modelos-de-dados)
6. [Códigos de Status](#códigos-de-status)
7. [Exemplos de Uso](#exemplos-de-uso)
8. [Rate Limiting e Cache](#rate-limiting-e-cache)

---

## Visão Geral

### Base URL

```
http://localhost:8000/api/v1
```

### Formato de Resposta

Todas as respostas são em JSON com codificação UTF-8.

### Headers Padrão

```http
Content-Type: application/json
Authorization: Bearer {access_token}
```

---

## Autenticação

Todos os endpoints (exceto `/health`) requerem autenticação via JWT Bearer Token.

### Obter Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token

```http
GET /api/v1/notifications
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API de Notificações

### 1. Listar Notificações

Obtém lista paginada de notificações do usuário autenticado.

```http
GET /api/v1/notifications
```

#### Query Parameters

| Parâmetro      | Tipo    | Padrão | Descrição                                    |
| -------------- | ------- | ------ | -------------------------------------------- |
| `skip`         | integer | 0      | Número de registros a pular                  |
| `limit`        | integer | 50     | Número máximo de registros (máx: 100)        |
| `unread_only`  | boolean | false  | Filtrar apenas não lidas                     |
| `type`         | string  | -      | Filtrar por tipo de notificação              |
| `priority`     | string  | -      | Filtrar por prioridade                       |

#### Tipos de Notificação

- `review_overdue` - Revisão atrasada
- `review_due_soon` - Revisão próxima
- `plan_created` - Plano criado
- `plan_updated` - Plano atualizado
- `plan_reviewed` - Plano revisado
- `high_priority` - Alta prioridade
- `system` - Sistema

#### Prioridades

- `urgent` - Urgente
- `high` - Alta
- `medium` - Média
- `low` - Baixa

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/notifications?skip=0&limit=20&unread_only=true&priority=high' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (200 OK)

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "review_overdue",
      "priority": "urgent",
      "title": "⚠️ Revisão Crítica Atrasada",
      "message": "O plano de intervenção está 15 dias atrasado",
      "intervention_plan_id": "789e0123-e89b-12d3-a456-426614174000",
      "is_read": false,
      "read_at": null,
      "action_url": "/intervention-plans/123",
      "created_at": "2025-11-24T10:30:00Z",
      "expires_at": "2025-12-24T10:30:00Z"
    }
  ],
  "total": 42,
  "unread_count": 15,
  "has_more": true
}
```

---

### 2. Obter Contagem de Não Lidas

Retorna apenas a contagem de notificações não lidas.

```http
GET /api/v1/notifications/unread-count
```

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/notifications/unread-count' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (200 OK)

```json
{
  "unread_count": 15
}
```

---

### 3. Obter Estatísticas

Retorna estatísticas agregadas das notificações.

```http
GET /api/v1/notifications/stats
```

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/notifications/stats' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (200 OK)

```json
{
  "total": 42,
  "unread": 15,
  "by_type": {
    "review_overdue": 5,
    "review_due_soon": 8,
    "plan_created": 10,
    "plan_updated": 12,
    "plan_reviewed": 5,
    "high_priority": 1,
    "system": 1
  },
  "by_priority": {
    "urgent": 6,
    "high": 10,
    "medium": 20,
    "low": 6
  },
  "urgent_count": 6
}
```

---

### 4. Marcar Como Lida

Marca uma notificação específica como lida.

```http
PATCH /api/v1/notifications/{notification_id}
```

#### Path Parameters

| Parâmetro         | Tipo | Descrição                |
| ----------------- | ---- | ------------------------ |
| `notification_id` | UUID | ID da notificação        |

#### Body

```json
{
  "is_read": true
}
```

#### Exemplo de Requisição

```bash
curl -X PATCH \
  'http://localhost:8000/api/v1/notifications/550e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"is_read": true}'
```

#### Resposta Sucesso (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "review_overdue",
  "priority": "urgent",
  "title": "⚠️ Revisão Crítica Atrasada",
  "message": "O plano de intervenção está 15 dias atrasado",
  "is_read": true,
  "read_at": "2025-11-24T11:00:00Z",
  "created_at": "2025-11-24T10:30:00Z"
}
```

#### Respostas de Erro

**404 Not Found** - Notificação não encontrada
```json
{
  "detail": "Notification not found"
}
```

---

### 5. Marcar Todas Como Lidas

Marca todas as notificações do usuário como lidas.

```http
POST /api/v1/notifications/mark-all-read
```

#### Exemplo de Requisição

```bash
curl -X POST \
  'http://localhost:8000/api/v1/notifications/mark-all-read' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (200 OK)

```json
{
  "updated_count": 15,
  "message": "15 notifications marked as read"
}
```

---

### 6. Deletar Notificação

Remove uma notificação específica.

```http
DELETE /api/v1/notifications/{notification_id}
```

#### Path Parameters

| Parâmetro         | Tipo | Descrição                |
| ----------------- | ---- | ------------------------ |
| `notification_id` | UUID | ID da notificação        |

#### Exemplo de Requisição

```bash
curl -X DELETE \
  'http://localhost:8000/api/v1/notifications/550e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (204 No Content)

Sem corpo de resposta.

#### Respostas de Erro

**404 Not Found** - Notificação não encontrada

---

## API de Exportação

### 1. Obter Resumo de Exportação

Retorna preview dos dados que serão exportados.

```http
GET /api/v1/export/pending-review/summary
```

#### Query Parameters

| Parâmetro         | Tipo   | Descrição                              |
| ----------------- | ------ | -------------------------------------- |
| `priority`        | string | Filtrar por prioridade                 |
| `professional_id` | UUID   | Filtrar por profissional               |

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/export/pending-review/summary?priority=high' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

#### Resposta Sucesso (200 OK)

```json
{
  "total": 45,
  "high_priority": 12,
  "medium_priority": 23,
  "low_priority": 10,
  "excel_available": true
}
```

---

### 2. Exportar CSV

Exporta planos pendentes de revisão em formato CSV.

```http
GET /api/v1/export/pending-review/csv
```

#### Query Parameters

| Parâmetro          | Tipo    | Padrão | Descrição                              |
| ------------------ | ------- | ------ | -------------------------------------- |
| `skip`             | integer | 0      | Registros a pular                      |
| `limit`            | integer | 1000   | Máximo de registros (máx: 1000)        |
| `priority`         | string  | -      | Filtrar por prioridade                 |
| `professional_id`  | UUID    | -      | Filtrar por profissional               |
| `include_student`  | boolean | false  | Incluir dados do aluno                 |

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/export/pending-review/csv?limit=100&priority=high&include_student=true' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  --output planos_pendentes.csv
```

#### Resposta Sucesso (200 OK)

**Headers:**
```http
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename=planos_pendentes_20251124_103000.csv
```

**Body (CSV):**
```csv
Prioridade,ID,Título,Descrição,Status,Frequência de Revisão,Precisa Revisão,Última Revisão,Criado Em
HIGH,123e4567-e89b-12d3-a456-426614174000,Plano de Matemática,Desenvolvimento de habilidades numéricas,active,weekly,Sim,15/11/2025,01/11/2025 14:30
MEDIUM,234e5678-e89b-12d3-a456-426614174001,Plano de Leitura,Compreensão textual,active,biweekly,Sim,10/11/2025,05/11/2025 09:15
```

#### Respostas de Erro

**404 Not Found** - Nenhum plano pendente encontrado
```json
{
  "detail": "No pending review plans found"
}
```

**422 Unprocessable Entity** - Parâmetros inválidos
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

### 3. Exportar Excel

Exporta planos pendentes de revisão em formato Excel com formatação.

```http
GET /api/v1/export/pending-review/excel
```

#### Query Parameters

Mesmos parâmetros do CSV.

#### Exemplo de Requisição

```bash
curl -X GET \
  'http://localhost:8000/api/v1/export/pending-review/excel?limit=500' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  --output planos_pendentes.xlsx
```

#### Resposta Sucesso (200 OK)

**Headers:**
```http
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=planos_pendentes_20251124_103000.xlsx
```

**Body:** Arquivo Excel binário com:
- Aba "Planos Pendentes" com dados formatados
- Aba "Resumo" com estatísticas
- Células coloridas por prioridade
- Filtros automáticos
- Larguras de coluna ajustadas

#### Respostas de Erro

**501 Not Implemented** - openpyxl não instalado
```json
{
  "detail": "Excel export not available. Install openpyxl: pip install openpyxl"
}
```

---

## Modelos de Dados

### Notification

```typescript
{
  id: string (UUID),
  user_id: string (UUID),
  type: "review_overdue" | "review_due_soon" | "plan_created" | "plan_updated" | "plan_reviewed" | "high_priority" | "system",
  priority: "urgent" | "high" | "medium" | "low",
  title: string (max 255),
  message: string,
  intervention_plan_id?: string (UUID),
  is_read: boolean,
  read_at?: string (ISO 8601),
  action_url?: string (max 500),
  created_at: string (ISO 8601),
  expires_at?: string (ISO 8601)
}
```

### NotificationListResponse

```typescript
{
  items: Notification[],
  total: number,
  unread_count: number,
  has_more: boolean
}
```

### NotificationStats

```typescript
{
  total: number,
  unread: number,
  by_type: {
    [key: string]: number
  },
  by_priority: {
    [key: string]: number
  },
  urgent_count: number
}
```

### ExportSummary

```typescript
{
  total: number,
  high_priority: number,
  medium_priority: number,
  low_priority: number,
  excel_available: boolean
}
```

---

## Códigos de Status

| Código | Significado                  | Descrição                                       |
| ------ | ---------------------------- | ----------------------------------------------- |
| 200    | OK                           | Requisição bem-sucedida                         |
| 201    | Created                      | Recurso criado com sucesso                      |
| 204    | No Content                   | Requisição bem-sucedida, sem corpo de resposta  |
| 400    | Bad Request                  | Requisição inválida                             |
| 401    | Unauthorized                 | Autenticação necessária                         |
| 403    | Forbidden                    | Sem permissão                                   |
| 404    | Not Found                    | Recurso não encontrado                          |
| 422    | Unprocessable Entity         | Validação falhou                                |
| 429    | Too Many Requests            | Rate limit excedido                             |
| 500    | Internal Server Error        | Erro do servidor                                |
| 501    | Not Implemented              | Funcionalidade não disponível                   |

---

## Exemplos de Uso

### Exemplo 1: Workflow Completo de Notificações

```javascript
// 1. Obter contagem de não lidas
const countResponse = await fetch('/api/v1/notifications/unread-count', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const { unread_count } = await countResponse.json();
console.log(`Você tem ${unread_count} notificações não lidas`);

// 2. Listar notificações não lidas
const listResponse = await fetch('/api/v1/notifications?unread_only=true&limit=20', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const { items } = await listResponse.json();

// 3. Marcar primeira notificação como lida
if (items.length > 0) {
  await fetch(`/api/v1/notifications/${items[0].id}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_read: true })
  });
}

// 4. Marcar todas como lidas
await fetch('/api/v1/notifications/mark-all-read', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Exemplo 2: Exportar Dados

```python
import requests

# Token de autenticação
token = "YOUR_ACCESS_TOKEN"
headers = {
    "Authorization": f"Bearer {token}"
}

# 1. Verificar resumo
summary = requests.get(
    "http://localhost:8000/api/v1/export/pending-review/summary",
    headers=headers
).json()

print(f"Total de planos pendentes: {summary['total']}")
print(f"Alta prioridade: {summary['high_priority']}")

# 2. Exportar CSV filtrado
csv_response = requests.get(
    "http://localhost:8000/api/v1/export/pending-review/csv",
    headers=headers,
    params={
        "priority": "high",
        "limit": 100,
        "include_student": True
    }
)

# Salvar arquivo
with open("planos_alta_prioridade.csv", "wb") as f:
    f.write(csv_response.content)

# 3. Exportar Excel completo
excel_response = requests.get(
    "http://localhost:8000/api/v1/export/pending-review/excel",
    headers=headers,
    params={"limit": 1000}
)

with open("todos_planos_pendentes.xlsx", "wb") as f:
    f.write(excel_response.content)
```

### Exemplo 3: Filtros Avançados

```bash
# Notificações urgentes não lidas
curl -X GET \
  'http://localhost:8000/api/v1/notifications?unread_only=true&priority=urgent' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# Apenas notificações de revisão atrasada
curl -X GET \
  'http://localhost:8000/api/v1/notifications?type=review_overdue' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# Exportar apenas planos de um profissional específico
curl -X GET \
  'http://localhost:8000/api/v1/export/pending-review/csv?professional_id=123e4567-e89b-12d3-a456-426614174000' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  --output planos_profissional.csv
```

---

## Rate Limiting e Cache

### Cache Redis

Os seguintes endpoints são cacheados:

| Endpoint                                 | TTL     | Chave                                      |
| ---------------------------------------- | ------- | ------------------------------------------ |
| `GET /notifications`                     | 5 min   | `notifications:user:{user_id}:list`        |
| `GET /notifications/stats`               | 10 min  | `notifications:user:{user_id}:stats`       |
| `GET /export/pending-review/summary`     | 15 min  | `export:summary:{filters_hash}`            |

### Invalidação de Cache

O cache é invalidado automaticamente quando:
- Notificação é criada, atualizada ou deletada
- Plano de intervenção é modificado
- Usuário marca notificação como lida

### Rate Limiting

**Limites atuais** (por IP):
- Endpoints de listagem: 100 requisições/minuto
- Endpoints de modificação: 50 requisições/minuto
- Endpoints de exportação: 10 requisições/minuto

**Header de resposta:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637654321
```

---

## Ferramentas e Testing

### Swagger UI

Documentação interativa disponível em:
```
http://localhost:8000/docs
```

### ReDoc

Documentação alternativa em:
```
http://localhost:8000/redoc
```

### Postman Collection

Importe a collection OpenAPI:
```
http://localhost:8000/openapi.json
```

### Redis Commander

Visualize o cache em tempo real:
```
http://localhost:8082
```

---

## Suporte e Contato

- **Documentação Completa**: `ENHANCED_FEATURES_README.md`
- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Email**: support@eduautismo.com

---

**Última Atualização**: 2025-11-24
**Versão da API**: 1.0.0
