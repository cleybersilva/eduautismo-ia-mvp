# 📚 Sistema de Atualização Automática de Documentação

Este documento explica como funciona o sistema de atualização automática do **README.md** e **CLAUDE.md**.

## 🎯 Objetivo

Manter a documentação sempre atualizada automaticamente quando houver mudanças no código, estrutura ou configurações do projeto.

## 🔧 Componentes

### 1. Script Python (`scripts/update_docs.py`)

Script inteligente que:
- ✅ Atualiza versão e data no CLAUDE.md automaticamente
- ✅ Verifica paths desatualizados (src/ vs app/)
- ✅ Detecta comandos incorretos
- ✅ Valida URLs do repositório
- ✅ Identifica referências ao Streamlit ao invés do React/Vite

**Uso:**
```bash
# Atualizar documentação
python scripts/update_docs.py

# Apenas verificar (sem modificar)
python scripts/update_docs.py --check-only
```

### 2. GitHub Action - Atualização Automática (`09-update-docs.yml`)

**Quando executa:**
- ✅ Após push para `main` ou `develop`
- ✅ Quando há mudanças em:
  - Código Python (`backend/**/*.py`)
  - Código React (`frontend/**/*.jsx`, `frontend/**/*.tsx`)
  - Workflows (`.github/workflows/**`)
  - Terraform (`terraform/**`)
  - Dependências (`package.json`, `requirements.txt`)
- ✅ Manualmente via "workflow_dispatch"

**O que faz:**
1. Verifica se documentação precisa atualização
2. Executa script de atualização
3. Commita mudanças automaticamente se necessário
4. Push automático com mensagem `[skip ci]`

**Mensagem de commit:**
```
docs: atualização automática de documentação [skip ci]

- README.md e CLAUDE.md atualizados automaticamente
- Versão e data atualizadas
- Verificações de consistência executadas

🤖 Atualizado por GitHub Actions
```

### 3. GitHub Action - Verificação em PRs (`10-check-docs-updated.yml`)

**Quando executa:**
- ✅ Em Pull Requests (opened, synchronize, reopened)
- ✅ Quando há mudanças em código relevante

**O que faz:**
1. Verifica se documentação está consistente
2. Falha o PR se encontrar problemas
3. Comenta no PR com instruções de correção
4. Mostra o que precisa ser corrigido

**Exemplo de comentário:**
```markdown
## ⚠️ Documentação Desatualizada

A documentação precisa ser atualizada para refletir as mudanças no código.

### Como corrigir:
1. Execute localmente: `python scripts/update_docs.py`
2. Ou aguarde a atualização automática após o merge

### O que verificamos:
- ✅ Paths e imports corretos (app/ vs src/)
- ✅ Comandos atualizados
- ✅ URLs corretas do repositório
- ✅ Versões e datas atualizadas
```

### 4. Pre-commit Hook (Opcional) (`scripts/pre-commit-docs`)

Hook do Git que verifica documentação **antes** de cada commit.

**Instalação:**
```bash
# Copiar hook
cp scripts/pre-commit-docs .git/hooks/pre-commit

# Tornar executável
chmod +x .git/hooks/pre-commit
```

**Comportamento:**
- ✅ Executa antes de cada `git commit`
- ✅ Verifica se documentação está atualizada
- ❌ Bloqueia commit se encontrar problemas
- 💡 Sugere comandos para corrigir

**Pular verificação (não recomendado):**
```bash
git commit --no-verify -m "sua mensagem"
```

## 🚀 Fluxo de Trabalho

### Cenário 1: Desenvolvimento Local

```bash
# 1. Fazer mudanças no código
vim backend/app/services/new_service.py

# 2. Antes de commitar, atualizar docs (se hook não instalado)
python scripts/update_docs.py

# 3. Verificar mudanças
git diff README.md CLAUDE.md

# 4. Commitar tudo junto
git add .
git commit -m "feat: adicionar novo serviço"

# 5. Push
git push origin feature/nova-feature
```

### Cenário 2: Pull Request

```bash
# 1. Criar PR
gh pr create --title "Nova feature"

# 2. GitHub Action verifica automaticamente
# ❌ Se docs desatualizados: PR falha + comentário com instruções
# ✅ Se docs ok: PR passa

# 3. Se necessário, corrigir localmente
python scripts/update_docs.py
git add README.md CLAUDE.md
git commit -m "docs: atualizar documentação"
git push
```

### Cenário 3: Merge para Main

```bash
# 1. PR aprovado e merged
gh pr merge 123

# 2. GitHub Action executa automaticamente
# 3. Se necessário, commita atualização dos docs
# 4. README.md e CLAUDE.md sempre atualizados em main
```

## 🔍 O Que é Verificado

### Paths Desatualizados
```python
# ❌ Incorreto
uvicorn src.api.main:app
from src.services import StudentService
pytest --cov=src

# ✅ Correto
uvicorn app.main:app
from app.services import StudentService
pytest --cov=app
```

### Frontend Desatualizado
```bash
# ❌ Incorreto
streamlit run src/web/app.py
http://localhost:8501

# ✅ Correto
npm run dev
http://localhost:5173
```

### URLs Genéricas
```markdown
❌ https://github.com/your-org/eduautismo-ia
✅ https://github.com/cleybersilva/eduautismo-ia-mvp
```

### Versão e Data
```markdown
# CLAUDE.md é atualizado automaticamente:
**Versão**: 1.1.0 → 1.1.1 (auto-incrementa)
**Última Atualização**: 2025-01-16 → 2025-01-17 (data atual)
```

## 📋 Checklist de Manutenção

Quando fazer mudanças estruturais:

- [ ] Executar `python scripts/update_docs.py`
- [ ] Revisar mudanças em README.md
- [ ] Revisar mudanças em CLAUDE.md
- [ ] Verificar se todos os paths estão corretos
- [ ] Confirmar que comandos estão funcionais
- [ ] Commitar junto com as mudanças de código

## 🛠️ Customização

### Adicionar Novas Verificações

Edite `scripts/update_docs.py`:

```python
def check_outdated_paths(self, content: str) -> List[str]:
    """Verifica paths desatualizados na documentação."""
    issues = []

    # Adicionar nova verificação
    if 'seu_padrao_antigo' in content:
        issues.append("❌ Descrição do problema")

    return issues
```

### Mudar Trigger do Workflow

Edite `.github/workflows/09-update-docs.yml`:

```yaml
on:
  push:
    branches:
      - main
      # Adicionar mais branches
      - staging
    paths:
      # Adicionar mais paths para monitorar
      - 'backend/**/*.py'
      - 'seu_novo_path/**'
```

## 🐛 Troubleshooting

### Documentação não atualiza automaticamente

**Problema:** GitHub Action não commitou mudanças.

**Solução:**
1. Verificar logs do workflow
2. Confirmar permissões: `contents: write`
3. Executar manualmente:
   ```bash
   python scripts/update_docs.py
   ```

### Pre-commit hook não funciona

**Problema:** Hook não executa.

**Soluções:**
```bash
# 1. Verificar se está executável
chmod +x .git/hooks/pre-commit

# 2. Verificar se está no lugar certo
ls -la .git/hooks/pre-commit

# 3. Testar manualmente
bash .git/hooks/pre-commit
```

### Script falha com erro de encoding

**Problema:** Erro ao ler arquivos.

**Solução:**
```bash
# Garantir encoding UTF-8
export PYTHONIOENCODING=utf-8
python scripts/update_docs.py
```

## 📞 Suporte

- **Issues**: [github.com/cleybersilva/eduautismo-ia-mvp/issues](https://github.com/cleybersilva/eduautismo-ia-mvp/issues)
- **Discussões**: [github.com/cleybersilva/eduautismo-ia-mvp/discussions](https://github.com/cleybersilva/eduautismo-ia-mvp/discussions)

---

**Última Atualização**: 2025-01-16
**Versão**: 1.0.0
