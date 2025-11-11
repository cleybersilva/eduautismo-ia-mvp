# 📑 CI/CD Workflows Documentation Index

## 🎯 Bem-vindo à Documentação de Workflows

Esta pasta contém toda a documentação sobre os GitHub Actions workflows do projeto, incluindo estrutura, implementação sequencial, e visualizações da pipeline.

---

## 📚 Documentos Disponíveis

### 1. **PIPELINE_STRUCTURE.md** 🏗️
**Propósito**: Entender a estrutura geral de todos os workflows

- Diagrama de cada workflow
- Descrição detalhada de cada job
- Triggers e eventos
- Sequência de execução
- Variáveis de ambiente

**Leia quando**: Precisa entender como os workflows estão organizados

**Tempo de leitura**: ~15 minutos

---

### 2. **SEQUENTIAL_IMPLEMENTATION.md** ⚙️
**Propósito**: Aprender como foi implementada a execução sequencial

- Estatísticas das mudanças
- Detalhes de cada workflow modificado
- Jobs e dependências criadas
- Explicação de `needs:` keyword
- Checklista de verificação

**Leia quando**: Quer entender as mudanças técnicas implementadas

**Tempo de leitura**: ~20 minutos

---

### 3. **VISUAL_GUIDE.md** 📊
**Propósito**: Visualização gráfica e timeline da pipeline

- Diagrama ASCII da pipeline completa
- Timeline estimado de execução
- Fluxo de decisão
- Status check matrix
- Artifacts gerados
- Instruções de monitoramento

**Leia quando**: Prefere visualizações gráficas ou precisa monitorar execução

**Tempo de leitura**: ~15 minutos

---

## 🗂️ Estrutura da Documentação

```
docs/ci-cd-devsecops/workflows/
├── README.md (este arquivo)
├── PIPELINE_STRUCTURE.md       (Estrutura geral)
├── SEQUENTIAL_IMPLEMENTATION.md (Mudanças técnicas)
└── VISUAL_GUIDE.md             (Visualizações)
```

---

## 🚀 Guia Rápido por Cenário

### 📍 "Quero entender o projeto rápido"
1. Leia: **VISUAL_GUIDE.md** (seção: Visualização Completa)
2. Tempo: ~5 minutos

### 📍 "Preciso debugar um workflow que falhou"
1. Leia: **PIPELINE_STRUCTURE.md** (seção: Triggers e Sequência)
2. Leia: **SEQUENTIAL_IMPLEMENTATION.md** (seção: Jobs e Dependências)
3. Tempo: ~20 minutos

### 📍 "Vou adicionar um novo job/workflow"
1. Leia: **SEQUENTIAL_IMPLEMENTATION.md** (seção: Conceitos Chave)
2. Leia: **PIPELINE_STRUCTURE.md** (toda)
3. Tempo: ~30 minutos

### 📍 "Preciso monitorar a execução"
1. Leia: **VISUAL_GUIDE.md** (seção: Timeline e Status Check)
2. Tempo: ~10 minutos

### 📍 "Quer entender dependências entre jobs"
1. Leia: **SEQUENTIAL_IMPLEMENTATION.md** (seção: Conceitos Chave)
2. Leia: **VISUAL_GUIDE.md** (seção: Fluxo de Decisão)
3. Tempo: ~15 minutos

---

## 🔑 Conceitos-Chave

### `needs:` - Dependência Entre Jobs
```yaml
job-b:
  needs: job-a
  # Aguarda job-a terminar com sucesso antes de iniciar
```

### `matrix:` - Paralelização
```yaml
strategy:
  matrix:
    image: ["api", "web"]
# Cria 2 jobs em paralelo: um para "api", outro para "web"
```

### `workflow_call:` - Reutilização
```yaml
on:
  workflow_call:
    # Este workflow pode ser chamado por outro workflow
```

### Jobs Sequenciais vs Paralelos
- **Sequencial** (padrão): Um job inicia após o anterior terminar
- **Paralelo** (com matrix): Múltiplas variações do mesmo job executam juntas

---

## 📊 Estatísticas

```
Total de Workflows:         5
Total de Jobs:              14
Total de Dependências:      13
Pontos de Paralelização:    4 (matrix de imagens)
Tempo Estimado Completo:    45-60 minutos

Workflows por tipo:
├─ Security (01):  6 jobs sequenciais
├─ Backend (02):   2 jobs sequenciais
├─ Frontend (03):  2 jobs sequenciais
├─ Container (04): 2 jobs sequenciais + 2 paralelos (matrix)
└─ Build (05):     2 jobs sequenciais + 2 paralelos (matrix)
```

---

## ✅ Checklist de Implementação

```
Verificação geral da pipeline:

☑ Todos os 5 workflows existem
☑ Todos têm `needs:` configurado
☑ Sem ciclos de dependência
☑ Matrix strategy funciona para api, web
☑ Upload-artifact está v4
☑ CodeQL está v3
☑ Docker COPY paths corretos
☑ Primeiro push dispara workflows
☑ Jobs executam em sequência
☑ Artifacts aparecem no GitHub
☑ Branch protection ativado
☑ Status checks funcionam
```

---

## 🔗 Links Úteis

### GitHub Actions
- [Documentação Oficial](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Event Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)

### Ferramenta mencionadas na Pipeline
- [Trivy](https://aquasecurity.github.io/trivy/) - Vulnerability Scanner
- [Grype](https://github.com/anchore/grype) - Container Security
- [Syft](https://github.com/anchore/syft) - SBOM Generator
- [Gitleaks](https://gitleaks.io/) - Secret Detection
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret Scanning
- [Bandit](https://bandit.readthedocs.io/) - Python Security
- [Black](https://black.readthedocs.io/) - Python Formatter
- [isort](https://pycqa.github.io/isort/) - Python Import Sorter
- [flake8](https://flake8.pycqa.org/) - Python Linter
- [mypy](https://www.mypy-lang.org/) - Python Type Checker
- [ESLint](https://eslint.org/) - JavaScript Linter
- [Prettier](https://prettier.io/) - JavaScript Formatter

---

## 📞 Suporte

### Problemas Comuns

**❌ Problema**: "Job falha com timeout"
- **Solução**: Aumentar timeout em `.github/workflows/` ou otimizar steps
- **Docs**: Ver SEQUENTIAL_IMPLEMENTATION.md

**❌ Problema**: "Matriz não funciona como esperado"
- **Solução**: Verificar sintaxe do matrix em PIPELINE_STRUCTURE.md
- **Docs**: VISUAL_GUIDE.md - Status Check Matrix

**❌ Problema**: "Artifacts não aparecem"
- **Solução**: Verificar paths de upload em PIPELINE_STRUCTURE.md
- **Docs**: VISUAL_GUIDE.md - Artifacts Gerados

**❌ Problema**: "Dependência não funciona"
- **Solução**: Validar sintaxe `needs:` em SEQUENTIAL_IMPLEMENTATION.md
- **Docs**: SEQUENTIAL_IMPLEMENTATION.md - Conceitos Chave

---

## 🎓 Aprenda com Exemplos

### Exemplo 1: Adicionar novo job sequencial
1. Abra **SEQUENTIAL_IMPLEMENTATION.md**
2. Procure "01-security-scan.yml"
3. Veja como `needs: gitleaks` foi adicionado a `trufflehog`
4. Replique o padrão para seu novo job

### Exemplo 2: Adicionar matrix
1. Abra **PIPELINE_STRUCTURE.md**
2. Procure "04-container-scan.yml"
3. Veja como `matrix: image: ["api", "web"]` paralleliza
4. Replique para seus jobs

### Exemplo 3: Debugar sequência
1. Abra **VISUAL_GUIDE.md**
2. Procure "Status Check Matrix"
3. Compare com seu GitHub Actions UI
4. Identifique desvios

---

## 📝 Changelog

### v1.0 - 2024
- ✅ Implementação inicial de dependências sequenciais
- ✅ Criação de documentação de workflows
- ✅ Adição de visualizações gráficas
- ✅ Consolidação em pasta docs/

---

## 🙏 Notas Finais

Esta documentação foi criada para facilitar:
- ✅ Onboarding de novo devs
- ✅ Troubleshooting de CI/CD issues
- ✅ Manutenção futura dos workflows
- ✅ Evolução da pipeline

**Se encontrar inconsistências ou tiver sugestões**, por favor abra uma issue ou PR!

---

**Última atualização**: 2024
**Status**: ✅ Documentação Completa e Organizada
**Localização**: `docs/ci-cd-devsecops/workflows/`
