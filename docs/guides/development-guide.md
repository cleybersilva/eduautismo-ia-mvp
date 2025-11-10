# 📝 Guia de Desenvolvimento

Este guia fornece informações detalhadas sobre o desenvolvimento do projeto EduAutismo IA.

## Estrutura do Projeto

```
eduautismo-ia-mvp/
├── backend/           # API e serviços em FastAPI
├── frontend/         # Interface em React
├── ml_models/        # Modelos de ML
├── scripts/          # Scripts de utilidade
└── terraform/        # IaC para AWS
```

## Stack Tecnológico

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### Frontend
- React
- Vite
- TailwindCSS
- React Query

### Machine Learning
- PyTorch
- Scikit-learn
- Transformers
- NLTK

### Infraestrutura
- AWS
- Docker
- Terraform
- GitHub Actions

## Padrões de Código

### Python
- Black para formatação
- isort para imports
- Flake8 para linting
- MyPy para type checking
- pytest para testes

### JavaScript/TypeScript
- ESLint
- Prettier
- Jest para testes
- React Testing Library

## Fluxo de Desenvolvimento

1. Crie uma nova branch a partir da main
2. Implemente suas mudanças
3. Execute os testes
4. Faça o commit seguindo conventional commits
5. Abra um PR para review

## Boas Práticas

### Commits
```
feat: adiciona novo recurso
fix: corrige bug
docs: atualiza documentação
style: formatação de código
refactor: refatoração de código
test: adiciona/atualiza testes
chore: manutenção geral
```

### Testes
- Mantenha cobertura acima de 85%
- Teste casos de borda
- Use fixtures para dados de teste
- Mock chamadas externas

### Documentação
- Docstrings em Python (Google style)
- JSDoc para JavaScript
- README atualizado
- Documentação da API

## Ambiente Local

### Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
pip install -r requirements-dev.txt
```

### Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### Banco de Dados
```bash
docker-compose up -d db
alembic upgrade head
```

## CI/CD

- Testes automatizados
- Análise de código
- Build e deploy
- Versionamento semântico

## Recursos

- [Documentação da API](./api-docs.md)
- [Guia de ML](./ml/README.md)
- [Arquitetura](./architecture.md)
- [Troubleshooting](./troubleshooting.md)