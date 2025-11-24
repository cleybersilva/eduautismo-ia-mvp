# Scripts de Manutenção - EduAutismo IA

Scripts utilitários para manutenção e administração do sistema.

## 📋 Índice

1. [Recalcular needs_review](#recalcular-needs_review)
2. [Criar Usuário Admin](#criar-usuário-admin)
3. [Criar Usuário Simples](#criar-usuário-simples)
4. [Atualizar Email](#atualizar-email)

---

## 🔄 Recalcular needs_review

**Script:** `recalculate_needs_review.py`

Recalcula o campo `needs_review` para todos os planos de intervenção baseado em:
- Frequência de revisão configurada (daily, weekly, monthly, etc.)
- Data da última revisão
- Status do plano (apenas planos ativos precisam revisão)

### Quando Usar

- ✅ Após aplicar a migration que adiciona o campo `needs_review`
- ✅ Após mudanças na lógica de cálculo de revisão
- ✅ Periodicamente como job de manutenção
- ✅ Para corrigir inconsistências nos dados

### Uso Básico

```bash
# Ver o que seria mudado (sem aplicar)
python scripts/recalculate_needs_review.py --dry-run

# Recalcular e aplicar mudanças
python scripts/recalculate_needs_review.py

# Recalcular apenas planos ativos
python scripts/recalculate_needs_review.py --status active
```

### Opções

| Opção | Descrição |
|-------|-----------|
| `--dry-run` | Não persiste mudanças, apenas mostra o que seria alterado |
| `--status STATUS` | Filtrar por status (active, draft, completed, paused, cancelled) |
| `--help` | Mostra ajuda completa |

### Exemplos

```bash
# Dry-run em todos os planos
python scripts/recalculate_needs_review.py --dry-run

# Aplicar mudanças apenas em planos ativos
python scripts/recalculate_needs_review.py --status active

# Aplicar mudanças em todos os planos
python scripts/recalculate_needs_review.py

# Verificar planos completados (geralmente todos serão false)
python scripts/recalculate_needs_review.py --dry-run --status completed
```

### Output Esperado

```
================================================================================
RECÁLCULO DE needs_review - 2025-11-23 23:23:50
================================================================================

Modo: DRY RUN (sem persistir)
Filtro de status: active
Total de planos: 15

  [  1/ 15] ✗→✓ Plano de Comunicação Social                     (False → True)
  [  3/ 15] ✓→✗ Plano de Habilidades Motoras                    (True → False)

================================================================================
ESTATÍSTICAS
================================================================================

Total de planos processados: 15
  • Mudanças necessárias:     2
  • Sem mudanças:             13

Tipos de mudança:
  • True → False:             1
  • False → True:             1

Planos sem mudança:
  • Já com True:              8
  • Já com False:             5

Por Status:
  • ACTIVE         :  15 planos,   2 mudanças,   9 precisam revisão

================================================================================
```

### Como Job Periódico

#### Cron (Linux/Mac)

```bash
# Executar todo dia às 3h da manhã
0 3 * * * cd /path/to/backend && python scripts/recalculate_needs_review.py >> /var/log/needs_review.log 2>&1
```

#### Task Scheduler (Windows)

```powershell
# Criar task que roda diariamente
schtasks /create /tn "RecalculateNeedsReview" /tr "python C:\path\to\backend\scripts\recalculate_needs_review.py" /sc daily /st 03:00
```

#### Docker/Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: recalculate-needs-review
spec:
  schedule: "0 3 * * *"  # 3h da manhã todo dia
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: recalculate
            image: eduautismo-api:latest
            command: ["python", "scripts/recalculate_needs_review.py"]
          restartPolicy: OnFailure
```

### Exit Codes

| Code | Significado |
|------|-------------|
| 0 | Sucesso |
| 1 | Erro durante execução |

---

## 👤 Criar Usuário Admin

**Script:** `create_admin_user.py`

Cria um usuário administrador no sistema.

### Uso

```bash
python scripts/create_admin_user.py
```

---

## 👤 Criar Usuário Simples

**Script:** `create_user_simple.py`

Cria um usuário comum (professor) no sistema.

### Uso

```bash
python scripts/create_user_simple.py
```

---

## ✉️ Atualizar Email

**Script:** `update_email.py`

Atualiza o email de um usuário existente.

### Uso

```bash
python scripts/update_email.py
```

---

## 🔧 Requisitos

Todos os scripts requerem:

- Python 3.11+
- Dependências instaladas: `pip install -r requirements.txt`
- Variáveis de ambiente configuradas (`.env`)
- Acesso ao banco de dados

## 🚨 Boas Práticas

### Antes de Executar em Produção

1. **Sempre teste em desenvolvimento primeiro**
   ```bash
   python scripts/script.py --dry-run
   ```

2. **Faça backup do banco de dados**
   ```bash
   # PostgreSQL
   pg_dump -h localhost -U user -d dbname > backup.sql

   # SQLite
   cp eduautismo.db eduautismo.db.backup
   ```

3. **Execute em horário de baixo tráfego**
   - Preferível: madrugada (2h-5h)
   - Evitar: horário comercial (9h-18h)

4. **Monitore a execução**
   ```bash
   # Com log detalhado
   python scripts/script.py 2>&1 | tee script.log
   ```

5. **Verifique o resultado**
   - Confira as estatísticas exibidas
   - Valide alguns registros manualmente
   - Execute queries de validação

### Segurança

- ⚠️ **Nunca** execute scripts de terceiros sem revisar o código
- ⚠️ **Nunca** compartilhe logs que contenham dados sensíveis
- ⚠️ **Sempre** use `--dry-run` primeiro em produção
- ✅ **Sempre** faça backup antes de scripts que modificam dados

---

## 📞 Suporte

Para problemas ou dúvidas sobre os scripts:

1. Verifique a documentação deste README
2. Execute com `--help` para ver opções disponíveis
3. Revise os logs de erro
4. Contate a equipe de desenvolvimento

---

## 📚 Referências

- [Documentação do Projeto](../README.md)
- [Migration Notes](../alembic/versions/MIGRATION_NOTES.md)
- [Sessão de Desenvolvimento](../SESSAO_20251123.md)

---

**Última atualização:** 2025-11-23
**Mantenedor:** Equipe EduAutismo IA
