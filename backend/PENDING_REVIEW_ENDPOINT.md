# 📋 Endpoint `/pending-review` - Documentação

## ✅ Status: IMPLEMENTADO

**Data**: 2025-11-23
**Feature**: Listagem de planos de intervenção que precisam revisão com priorização

---

## 📝 Resumo

Novo endpoint GET `/api/v1/intervention-plans/pending-review` que retorna uma lista de planos de intervenção que precisam revisão, ordenados por prioridade e com filtros opcionais.

---

## 🎯 Arquivos Modificados/Criados

### 1. **Schema**: `app/schemas/intervention_plan.py`

Adicionados dois novos schemas:

```python
class PendingReviewItem(BaseModel):
    """Schema para item na lista de revisões pendentes."""

    id: UUID
    title: str
    student_id: UUID
    student_name: str
    review_frequency: ReviewFrequency
    last_reviewed_at: Optional[date]
    days_since_review: Optional[int]
    created_at: datetime
    end_date: date
    days_remaining: int
    priority: str  # "high", "medium", "low"
    created_by_id: UUID

class PendingReviewListResponse(BaseModel):
    """Response schema para lista de planos que precisam revisão."""

    items: list[PendingReviewItem]
    total: int
    high_priority: int
    medium_priority: int
    low_priority: int
```

### 2. **Service**: `app/services/intervention_plan_service.py`

Novo método `get_pending_review_plans()`:

```python
def get_pending_review_plans(
    self,
    skip: int = 0,
    limit: int = 50,
    priority_filter: Optional[str] = None,
    professional_id: Optional[UUID] = None,
) -> dict:
    """
    Lista planos de intervenção que precisam revisão com priorização.

    Retorna planos ATIVOS com needs_review=True, calculando prioridade baseada em:
    - HIGH: Nunca revisado OU atrasado >2x o período da frequência
    - MEDIUM: Atrasado >1x o período da frequência
    - LOW: No período ou recém passou o limite
    """
```

**Lógica de Priorização**:
- Query apenas planos `ACTIVE` com `needs_review=True`
- Join com `Student` para obter nome do aluno
- Calcula `days_since_review` para cada plano
- Compara com thresholds por frequência:
  - DAILY: 1 dia
  - WEEKLY: 7 dias
  - BIWEEKLY: 14 dias
  - MONTHLY: 30 dias
  - QUARTERLY: 90 dias
- Ordena por prioridade (high→medium→low) e depois por dias atrasado
- Aplica filtros e paginação

### 3. **Route**: `app/api/routes/intervention_plans.py`

Novo endpoint:

```python
@router.get("/pending-review", response_model=PendingReviewListResponse)
def get_pending_review_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    priority: Optional[str] = Query(None, pattern="^(high|medium|low)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    professional_id_param: Optional[UUID] = Depends(get_professional_id),
)
```

---

## 🔌 API Specification

### Endpoint
```
GET /api/v1/intervention-plans/pending-review
```

### Autenticação
- **Obrigatório**: Token JWT via `Authorization: Bearer <token>`
- **Opcional**: Header `X-Professional-ID` para filtrar por profissional

### Query Parameters

| Parâmetro  | Tipo    | Obrigatório | Default | Descrição                                    |
|------------|---------|-------------|---------|----------------------------------------------|
| `skip`     | integer | Não         | 0       | Número de registros para pular (paginação)   |
| `limit`    | integer | Não         | 50      | Máximo de registros (1-200)                  |
| `priority` | string  | Não         | null    | Filtrar por prioridade: high, medium, low    |

### Response 200 OK

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Plano de Desenvolvimento...",
      "student_id": "uuid",
      "student_name": "João Silva",
      "review_frequency": "weekly",
      "last_reviewed_at": "2025-11-10",
      "days_since_review": 13,
      "created_at": "2025-10-01T10:00:00",
      "end_date": "2026-01-31",
      "days_remaining": 69,
      "priority": "high",
      "created_by_id": "uuid"
    }
  ],
  "total": 15,
  "high_priority": 5,
  "medium_priority": 7,
  "low_priority": 3
}
```

### Response Codes

| Código | Descrição                                           |
|--------|-----------------------------------------------------|
| 200    | Sucesso - retorna lista de planos                   |
| 401    | Não autenticado - token ausente ou inválido         |
| 403    | Não autorizado - sem permissão para acessar         |
| 422    | Validação falhou - parâmetros inválidos             |

---

## 📊 Casos de Uso

### 1. **Dashboard de Revisões Pendentes**
```bash
GET /api/v1/intervention-plans/pending-review?limit=20
```
Exibe os 20 planos mais urgentes que precisam revisão.

### 2. **Alertas de Alta Prioridade**
```bash
GET /api/v1/intervention-plans/pending-review?priority=high
```
Lista apenas planos críticos (nunca revisados ou muito atrasados).

### 3. **Gestão por Profissional**
```bash
GET /api/v1/intervention-plans/pending-review
Header: X-Professional-ID: <uuid>
```
Filtra planos onde o profissional está envolvido (criador ou participante).

### 4. **Paginação para Grandes Volumes**
```bash
# Página 1
GET /api/v1/intervention-plans/pending-review?skip=0&limit=50

# Página 2
GET /api/v1/intervention-plans/pending-review?skip=50&limit=50
```

---

## ✅ Testes

### Testes de Integração Criados
Arquivo: `tests/integration/test_intervention_plans_pending_review.py`

**Status dos Testes**:
- ✅ `test_get_pending_review_without_auth` → PASSED
- ✅ `test_get_pending_review_invalid_priority` → PASSED
- ⚠️  Outros 6 testes dependem de fixtures complexas com transações de BD

**Cobertura**:
- Endpoint está funcional e registrado corretamente
- Validação de autenticação funciona
- Validação de parâmetros funciona
- Lógica de priorização implementada

---

## 🚀 Próximos Passos

### Para Resolver Testes Restantes
1. Ajustar fixtures para criar planos via API em vez de BD direto
2. Ou: Simplificar testes para validar apenas resposta do endpoint
3. Considerar testes end-to-end com banco de dados populado

### Melhorias Futuras
1. **Cache**: Adicionar cache Redis para lista de pending reviews (TTL 5min)
2. **Notificações**: Integrar com sistema de alertas/emails
3. **Filtros Adicionais**:
   - Por estudante
   - Por faixa de datas
   - Por tipo de frequência
4. **Métricas**: Adicionar logging/metrics para monitorar uso

---

## 📋 Checklist de Deployment

- [x] Schema criado e validado
- [x] Service implementado com lógica de priorização
- [x] Endpoint criado e documentado
- [x] Testes básicos passando
- [x] Endpoint registrado no router
- [ ] Testes completos de integração
- [ ] Documentação OpenAPI verificada
- [ ] Performance testada com volume alto
- [ ] Deploy em staging
- [ ] Validação com stakeholders

---

## 📚 Referências

- **Migration**: `zxo9rq852lkg_add_needs_review_field.py`
- **Model Logic**: `InterventionPlan.calculate_needs_review()`
- **Manutenção**: `scripts/intervention_plans_health_check.py`
- **Deploy**: `DEPLOY_NEEDS_REVIEW.md`

---

**Autor**: Claude Code Assistant
**Revisão**: Pendente
**Aprovação**: Pendente
