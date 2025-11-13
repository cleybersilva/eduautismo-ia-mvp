# 📚 Documentação do EduAutismo IA

## Estrutura da Documentação

```
docs/
├── INDEX.md                # Índice principal
├── README.md              # Este arquivo
├── guides/               # Guias detalhados
│   ├── quickstart.md     # Guia de início rápido
│   ├── development-guide.md   # Guia de desenvolvimento
│   ├── architecture.md   # Arquitetura do sistema
│   ├── api-docs.md      # Documentação da API
│   └── troubleshooting.md    # Solução de problemas
├── backend/             # Documentação do backend
├── infrastructure/      # Documentação de infraestrutura
├── ml/                 # Documentação de Machine Learning
└── scripts/            # Documentação de scripts
```

## Guias Principais

1. [Índice da Documentação](./INDEX.md)
2. [Guia de Início Rápido](./guides/quickstart.md)
3. [Guia de Desenvolvimento](./guides/development-guide.md)
4. [Documentação da API](./guides/api-docs.md)
5. [Arquitetura](./guides/architecture.md)

## 🧪 Documentação de Testes

### Testes Manuais e API
- [TESTING.md](./TESTING.md) - Guia completo de testes manuais
  - Testes com cURL
  - Testes com Postman
  - Endpoints da API
  - Autenticação

### Testes Automatizados (NOVO!)
- [TESTING_AUTOMATED.md](./TESTING_AUTOMATED.md) - **Guia completo de testes automatizados**
  - ✅ **82.25% de cobertura de código**
  - ✅ **306 testes** (280 unit + 26 integration)
  - ✅ Configuração SQLite in-memory
  - ✅ Tipos portáveis (GUID, StringArray, PortableJSON)
  - ✅ Fixtures e utilitários
  - ✅ Boas práticas
  - ✅ Troubleshooting

## Convenções

### Formatação
- Use Markdown para toda documentação
- Siga o Google Style para docstrings
- Mantenha links relativos
- Inclua exemplos de código

### Organização
- Um tópico por arquivo
- Nomes de arquivos em kebab-case
- Mantenha índices atualizados
- Use hierarquia lógica

### Manutenção
- Atualize junto com o código
- Valide links regularmente
- Revise periodicamente
- Mantenha exemplos atuais

## Contribuindo

1. Faça as alterações em uma branch
2. Siga as convenções de formatação
3. Atualize índices relacionados
4. Abra um PR para review

## Validação

Execute o script de validação da documentação:
```bash
./scripts/validate-docs.sh
```

## Links Úteis

- [Página do Projeto](https://github.com/cleybersilva/eduautismo-ia-mvp)
- [Reportar Problemas](https://github.com/cleybersilva/eduautismo-ia-mvp/issues)
- [Wiki do Projeto](https://github.com/cleybersilva/eduautismo-ia-mvp/wiki)