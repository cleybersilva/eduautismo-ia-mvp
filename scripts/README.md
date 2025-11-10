# Diretório de Scripts

Este diretório contém scripts utilitários para o projeto EduAutismo IA.

## Scripts de Validação de Estrutura

### check_structure.py

**Propósito:** Validar estrutura do projeto e criar arquivos ausentes com templates.

**Recursos:**
- ✅ Valida estrutura de diretórios
- ✅ Valida existência de arquivos
- ✅ Criação de arquivos baseada em prioridade (1=Crítico, 2=Importante, 3=Opcional)
- ✅ Templates inteligentes de arquivos (Models, Schemas, Services, Routes, Tests)
- ✅ Relatórios detalhados com saída colorida
- ✅ Inserção automática de TODO para customização

**Início Rápido:**
```bash
# Apenas validar
python scripts/check_structure.py --report-only

# Criar arquivos críticos
python scripts/check_structure.py --create-missing --priority 1

# Criar arquivos críticos + importantes
python scripts/check_structure.py --create-missing --priority 2
```

**Documentação Completa:** Veja [docs/structure-validation.md](../docs/structure-validation.md)

### validate_structure.sh

**Propósito:** Fluxo completo de validação com múltiplas verificações.

**Recursos:**
- ✅ Verificação de versão Python
- ✅ Validação de estrutura
- ✅ Verificação de estrutura de pacotes
- ✅ Verificação de arquivos críticos
- ✅ Validação de sintaxe Python
- ✅ Relatório de status do Git

**Início Rápido:**
```bash
# Validar tudo
./scripts/validate_structure.sh

# Auto-corrigir com arquivos de Prioridade 1
./scripts/validate_structure.sh --fix

# Auto-corrigir com arquivos de Prioridade 1 e 2
./scripts/validate_structure.sh --fix --priority 2
```

### test_routes.sh

**Propósito:** Testar automaticamente todos os endpoints da API.

**Recursos:**
- ✅ Testes de conectividade
- ✅ Testes de health checks (5 endpoints)
- ✅ Testes de autenticação completa (registro, login, refresh, reset)
- ✅ Testes de endpoints protegidos
- ✅ Testes de documentação
- ✅ Saída colorida e relatório detalhado
- ✅ Contador de testes com taxa de sucesso

**Início Rápido:**
```bash
# Tornar executável (primeira vez)
chmod +x scripts/test_routes.sh

# Executar testes
./scripts/test_routes.sh

# Testar servidor customizado
./scripts/test_routes.sh http://seu-servidor:8000
```

**Documentação Completa:** Veja [docs/TESTING.md](../docs/TESTING.md)

## Organização de Diretórios

```
scripts/
├── README.md                    # Este arquivo
├── check_structure.py           # Script principal de validação
├── validate_structure.sh        # Script de fluxo completo
├── test_routes.sh               # Script de teste de rotas da API
│
├── setup/                       # Scripts de configuração e instalação
│   ├── check-requirements.sh
│   ├── install.sh
│   ├── quick-start.sh
│   └── test-all.sh
│
├── deployment/                  # Scripts de deploy
│   ├── deploy-dev.sh
│   └── stop-dev.sh
│
├── backup/                      # Utilitários de backup
│
├── database/                    # Scripts de gerenciamento de banco de dados
│
└── ml/                          # Treinamento e gerenciamento de modelos ML

```

## Outros Scripts

### Scripts de Configuração (setup/)

**check-requirements.sh**
- Verifica se todas as ferramentas necessárias estão instaladas
- Valida versões de Python, Node.js, Docker

**install.sh**
- Script completo de instalação
- Configura ambientes backend e frontend

**quick-start.sh**
- Inicialização rápida do projeto
- Executa migrations do banco de dados e inicia serviços

**test-all.sh**
- Executa todas as suítes de teste
- Testes de backend e frontend

### Scripts de Deploy (deployment/)

**deploy-dev.sh**
- Deploy para ambiente de desenvolvimento
- Gerencia containers e serviços Docker

**stop-dev.sh**
- Para serviços de desenvolvimento
- Limpa containers

## Exemplos de Uso

### Configuração Completa de Novo Projeto

```bash
# 1. Criar estrutura do projeto
python scripts/check_structure.py --create-missing --priority 2

# 2. Validar tudo
./scripts/validate_structure.sh

# 3. Instalar dependências
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Executar testes
pytest backend/tests/
```

### Fluxo de Trabalho Diário de Desenvolvimento

```bash
# Antes de começar a trabalhar
./scripts/validate_structure.sh

# Antes de commitar
python scripts/check_structure.py --report-only
git status
git add .
git commit -m "Sua mensagem"
```

### Integração CI/CD

```yaml
# .github/workflows/validate.yml
- name: Validar Estrutura
  run: python scripts/check_structure.py --report-only
```

## Permissões de Scripts

Torne os scripts executáveis:

```bash
chmod +x scripts/*.sh
chmod +x scripts/**/*.sh
```

## Adicionando Novos Scripts

Ao adicionar novos scripts:

1. Escolha o subdiretório apropriado
2. Siga convenções de nomenclatura (minúsculas, hífens)
3. Adicione linha shebang (`#!/bin/bash` ou `#!/usr/bin/env python3`)
4. Documente neste README
5. Torne executável com `chmod +x`
6. Adicione tratamento de erros (`set -e` para scripts bash)

### Template para Scripts Bash

```bash
#!/bin/bash
#
# Nome do Script - Breve Descrição
#
# Uso:
#   ./nome-do-script.sh [opções]
#
# Opções:
#   --help    Mostrar esta mensagem de ajuda

set -e  # Sair em caso de erro

# Conteúdo do script aqui
```

### Template para Scripts Python

```python
#!/usr/bin/env python3
"""
Nome do Script - Breve Descrição

Uso:
    python nome_do_script.py [opções]
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Descrição')
    # Adicionar argumentos
    args = parser.parse_args()

    # Lógica do script aqui


if __name__ == '__main__':
    main()
```

## Solução de Problemas

### Problemas de Permissão

```bash
# Corrigir todos os scripts de uma vez
find scripts/ -type f -name "*.sh" -exec chmod +x {} \;
find scripts/ -type f -name "*.py" -exec chmod +x {} \;
```

### Problemas de Importação Python

```bash
# Definir PYTHONPATH para raiz do projeto
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Ou executar da raiz do projeto
cd /caminho/para/eduautismo-ia-mvp
python scripts/check_structure.py
```

### Script Não Encontrado

```bash
# Sempre execute da raiz do projeto
pwd  # Deve ser: /caminho/para/eduautismo-ia-mvp

# Use caminho completo ou ./
python scripts/check_structure.py  # ✅
python check_structure.py          # ❌
```

## Dependências

A maioria dos scripts requer:
- **Python 3.11+** para scripts Python
- **Bash 4.0+** para scripts shell
- **Git** para operações de controle de versão
- **Docker** (opcional, para scripts de deploy)

## Códigos de Saída

Scripts usam códigos de saída padrão:
- `0` - Sucesso
- `1` - Aviso ou problemas menores
- `2` - Erro ou problemas maiores

Use em CI/CD:
```bash
./scripts/validate_structure.sh
if [ $? -ne 0 ]; then
    echo "Validação falhou"
    exit 1
fi
```

## Melhores Práticas

1. **Sempre execute da raiz do projeto**
2. **Verifique códigos de saída em automação**
3. **Revise saída do script antes de agir nas sugestões**
4. **Use flag `--help` quando disponível**
5. **Teste scripts em desenvolvimento antes de usar em produção**
6. **Mantenha scripts focados e com propósito único**
7. **Documente todas as opções e uso**

## Contribuindo

Ao contribuir com novos scripts:
1. Siga padrões e convenções existentes
2. Adicione documentação abrangente
3. Inclua exemplos de uso
4. Adicione tratamento de erros
5. Teste completamente
6. Atualize este README

## Suporte

Para problemas com scripts:
1. Verifique saída do script para mensagens de erro
2. Revise esta documentação
3. Verifique [docs/structure-validation.md](../docs/structure-validation.md) para scripts de validação
4. Revise [docs/troubleshooting.md](../docs/troubleshooting.md) se disponível
5. Abra uma issue no GitHub

## Scripts Futuros

Adições planejadas:
- [ ] Script de seed do banco de dados
- [ ] Automação de treinamento de modelos ML
- [ ] Benchmarking de performance
- [ ] Scanning de segurança
- [ ] Testes automatizados com cobertura
- [ ] Scripts de deploy em produção
- [ ] Utilitários de backup e restore

## Licença

Todos os scripts são parte do projeto EduAutismo IA e seguem a mesma Licença MIT.
