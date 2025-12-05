# ✅ Checklist para Commit - Endpoint Pending Review

## 📋 Pre-Commit Checklist

### Código
- [x] Schemas criados e validados (`PendingReviewItem`, `PendingReviewListResponse`)
- [x] Service method implementado (`get_pending_review_plans()`)
- [x] Endpoint criado e documentado
- [x] Imports corretos
- [x] Type hints em todas as funções
- [x] Docstrings completas
- [x] Tratamento de erros adequado
- [x] Validação de parâmetros (Pydantic)

### Qualidade
- [x] Código formatado (Black)
- [x] Imports ordenados (isort)
- [x] Sem erros de lint (Flake8)
- [x] Type checking OK (MyPy)
- [x] Testes criados (8 integration tests)
- [x] Coverage mantido > 60% (73.07%)
- [x] Nenhuma regressão (321 testes passando)

### Documentação
- [x] Docstring OpenAPI completa
- [x] README específico criado
- [x] Changelog atualizado
- [x] Relatório de sessão criado
- [x] Exemplos de uso incluídos

### Git
- [x] Alterações revisadas
- [x] Mensagem de commit preparada
- [ ] Branch feature criada (se necessário)
- [ ] Push para remote
- [ ] Pull request criado (se necessário)

---

## 🎯 Arquivos para Commit

### Modificados (3 arquivos)
```
M  app/schemas/intervention_plan.py           (+48 linhas)
M  app/services/intervention_plan_service.py  (+128 linhas)
M  app/api/routes/intervention_plans.py       (+47 linhas)
```

### Criados (5 arquivos)
```
A  tests/integration/test_intervention_plans_pending_review.py  (267 linhas)
A  PENDING_REVIEW_ENDPOINT.md
A  SESSAO_20251123_PARTE2.md
A  CHANGELOG_PENDING_REVIEW.md
A  COMMIT_CHECKLIST_PENDING_REVIEW.md
```

**Total**: 8 arquivos, ~490 linhas de código

---

## 📝 Mensagem de Commit Sugerida

### Título (Conventional Commits)
```
feat(intervention-plans): adicionar endpoint /pending-review com priorização
```

### Descrição Completa
```
feat(intervention-plans): adicionar endpoint /pending-review com priorização

Implementa novo endpoint GET /api/v1/intervention-plans/pending-review
para listar planos de intervenção que precisam revisão com sistema de
priorização inteligente.

## Funcionalidades

- Sistema de priorização (HIGH/MEDIUM/LOW) baseado em atraso
- Filtros: priority, professional_id, paginação
- Ordenação: prioridade + urgência
- Estatísticas: contagens por prioridade
- Query otimizada com joins
- Documentação OpenAPI completa

## Schemas

- PendingReviewItem: item individual com prioridade
- PendingReviewListResponse: resposta com estatísticas

## Lógica de Priorização

- HIGH: Nunca revisado OU >2x o período da frequência
- MEDIUM: >1x o período da frequência
- LOW: Dentro do período ou recém passou

## Casos de Uso

- Dashboard de revisões pendentes
- Alertas de alta prioridade
- Gestão por profissional
- Navegação paginada

## Testes

- 8 testes de integração criados
- 321 testes passando (sem regressões)
- Coverage: 73.07%

## Documentação

- PENDING_REVIEW_ENDPOINT.md: documentação completa
- SESSAO_20251123_PARTE2.md: relatório detalhado
- CHANGELOG_PENDING_REVIEW.md: changelog

## Breaking Changes

Nenhum. Feature aditiva, sem mudanças em APIs existentes.

## Migration Required

Não. Usa campo `needs_review` já criado em migration anterior.

Closes #[número-da-issue]
```

---

## 🚀 Comandos Git

### 1. Verificar Status
```bash
git status
git diff app/schemas/intervention_plan.py
git diff app/services/intervention_plan_service.py
git diff app/api/routes/intervention_plans.py
```

### 2. Adicionar Arquivos
```bash
# Arquivos modificados
git add app/schemas/intervention_plan.py
git add app/services/intervention_plan_service.py
git add app/api/routes/intervention_plans.py

# Arquivos novos
git add tests/integration/test_intervention_plans_pending_review.py
git add PENDING_REVIEW_ENDPOINT.md
git add SESSAO_20251123_PARTE2.md
git add CHANGELOG_PENDING_REVIEW.md
git add COMMIT_CHECKLIST_PENDING_REVIEW.md
```

### 3. Commit
```bash
git commit -m "feat(intervention-plans): adicionar endpoint /pending-review com priorização

Implementa novo endpoint GET /api/v1/intervention-plans/pending-review
para listar planos de intervenção que precisam revisão com sistema de
priorização inteligente.

✨ Features:
- Sistema de priorização (HIGH/MEDIUM/LOW)
- Filtros: priority, professional_id, paginação
- Ordenação inteligente
- Estatísticas por prioridade

📊 Tests:
- 8 integration tests
- 321 passing (sem regressões)
- 73.07% coverage

📚 Docs:
- OpenAPI documentation
- Detailed README
- Session report
- Changelog

🤖 Generated with Claude Code
"
```

### 4. Push (se aplicável)
```bash
# Se estiver em feature branch
git push origin feature/pending-review-endpoint

# Se estiver em main (apenas se aprovado)
git push origin main
```

---

## 🔍 Validação Local

### Executar Testes
```bash
# Todos os testes
python -m pytest

# Apenas unit tests
python -m pytest tests/unit/ -v

# Apenas novos testes
python -m pytest tests/integration/test_intervention_plans_pending_review.py -v

# Com coverage
python -m pytest --cov=app --cov-report=html
```

### Verificar Código
```bash
# Formatar
black app/ tests/ --line-length=120
isort app/ tests/

# Lint
flake8 app/ tests/ --max-line-length=120

# Type checking
mypy app/ --ignore-missing-imports
```

### Testar Endpoint Manualmente
```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Em outro terminal, testar
curl -X GET "http://localhost:8000/api/v1/intervention-plans/pending-review" \
  -H "Authorization: Bearer <seu-token>"

# Testar com filtro
curl -X GET "http://localhost:8000/api/v1/intervention-plans/pending-review?priority=high&limit=10" \
  -H "Authorization: Bearer <seu-token>"
```

### Verificar Docs
```bash
# OpenAPI UI
# Abrir navegador: http://localhost:8000/docs

# ReDoc
# Abrir navegador: http://localhost:8000/redoc
```

---

## ⚠️ Pré-requisitos para Merge

### Code Review
- [ ] Aprovação de pelo menos 1 reviewer
- [ ] Todas as conversas resolvidas
- [ ] CI/CD passou

### Testes
- [ ] Todos os testes passando
- [ ] Coverage >= 60%
- [ ] Testes manuais executados

### Documentação
- [ ] README atualizado (se necessário)
- [ ] CHANGELOG atualizado
- [ ] OpenAPI docs verificadas

### Deploy
- [ ] Plano de deploy revisado
- [ ] Rollback plan definido
- [ ] Stakeholders notificados

---

## 📋 Post-Merge Checklist

### Staging
- [ ] Deploy em staging
- [ ] Smoke tests
- [ ] Validação funcional
- [ ] Testes de carga (se aplicável)

### Production
- [ ] Deploy em production
- [ ] Smoke tests em prod
- [ ] Monitoramento ativo
- [ ] Métricas coletadas
- [ ] Alertas configurados

### Comunicação
- [ ] Equipe notificada
- [ ] Documentação de API publicada
- [ ] Release notes criadas (se aplicável)
- [ ] Stakeholders informados

---

## 🎉 Status Atual

✅ **PRONTO PARA COMMIT**

- Código completo e testado
- Documentação completa
- Testes passando
- Coverage adequado
- Sem regressões
- Pronto para code review

---

**Data**: 2025-11-23
**Feature**: Endpoint /pending-review
**Status**: ✅ Ready for Review
**Next Step**: Criar PR ou commit direto
