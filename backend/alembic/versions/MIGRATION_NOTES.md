# Migration Notes

## 20251123_2115 - Add needs_review Field

**Revision ID:** `zxo9rq852lkg`
**Parent Revision:** `0a32abc79858`
**Date:** 2025-11-23 21:15:00

### Objetivo

Adicionar o campo `needs_review` à tabela `intervention_plans` que estava definido no modelo ORM mas ausente no schema do banco de dados.

### Mudanças

#### Upgrade
```sql
ALTER TABLE intervention_plans
ADD COLUMN needs_review BOOLEAN NOT NULL DEFAULT false;
```

#### Downgrade
```sql
ALTER TABLE intervention_plans
DROP COLUMN needs_review;
```

### Campo: needs_review

- **Tipo:** Boolean
- **Nullable:** False
- **Default:** false
- **Propósito:** Indicar quando um plano de intervenção precisa de revisão baseado na frequência configurada (`review_frequency`)

### Lógica de Negócio

O campo `needs_review` é calculado automaticamente pelo serviço baseado em:
1. Frequência de revisão configurada (`daily`, `weekly`, `biweekly`, `monthly`, `quarterly`)
2. Data da última revisão (`last_reviewed_at`)
3. Data atual

**Exemplo:**
```python
# Um plano com review_frequency=WEEKLY que não foi revisado há 8 dias
# terá needs_review=True
```

### Aplicação em Produção

#### Passo 1: Backup
```bash
# Fazer backup do banco antes de aplicar migration
pg_dump -h <host> -U <user> -d <database> > backup_before_needs_review.sql
```

#### Passo 2: Aplicar Migration
```bash
cd backend
alembic upgrade head
```

#### Passo 3: Verificar
```bash
# Verificar se a coluna foi criada
psql -h <host> -U <user> -d <database> -c "\d intervention_plans"
```

#### Passo 4: Validar Dados
```sql
-- Verificar que todos os registros têm needs_review=false por padrão
SELECT COUNT(*), needs_review
FROM intervention_plans
GROUP BY needs_review;
```

### Rollback (se necessário)

```bash
# Reverter a migration
alembic downgrade -1
```

### Impacto

- **Tabelas Afetadas:** `intervention_plans`
- **Downtime:** Nenhum (operação DDL rápida com default)
- **Compatibilidade:** 100% backwards compatible (campo tem default)
- **Performance:** Impacto mínimo (coluna Boolean com índice implícito)

### Testes

A migration foi validada com:
```bash
# Sintaxe Python
python3 -m py_compile alembic/versions/20251123_2115_zxo9rq852lkg_add_needs_review_field.py

# Testes de integração
pytest tests/integration/test_intervention_plans_api.py -v
```

### Considerações

1. **Valores Existentes:** Todos os planos existentes terão `needs_review=false` após a migration
2. **Cálculo Assíncrono:** Um job/task deve calcular o valor real de `needs_review` após a migration
3. **Índice:** Considere adicionar índice se queries filtradas por `needs_review` forem frequentes:
   ```sql
   CREATE INDEX ix_intervention_plans_needs_review
   ON intervention_plans(needs_review)
   WHERE needs_review = true;
   ```

### Próximos Passos (Opcional)

1. Adicionar índice parcial para `needs_review=true` (se necessário)
2. Criar job periódico para recalcular `needs_review` automaticamente
3. Adicionar alertas para planos com `needs_review=true` há muito tempo

---

**Autor:** Sistema
**Aprovado por:** Revisar antes de produção
**Status:** ✅ Pronto para produção
