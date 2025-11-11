# Diretrizes do Repositório

## Estrutura do Projeto e Organização de Módulos
Repo = Backend FastAPI (`backend/app`, `backend/tests`, `backend/alembic`) + Frontend Vite/React (`frontend/src`); `Dockerfile.api`, `Dockerfile.web`, `docker-compose.yml` e o `Makefile` raiz executam os containers. Recursos compartilhados (ml_models/, scripts/, docs/, coleção Postman) ficam na raiz, IaC em `terraform/`, e artefatos gerados ficam sob `logs/` (gitignored).

## Comandos de Build, Teste e Desenvolvimento
Use `make dev`, `make stop`, `make db-migrate`, `make test` e `make lint` para controle da stack, migrações, testes e linting. Trabalho no frontend roda em `frontend/` (`npm install`, `npm run dev`, `npm run build`). Inicie Adminer/Mongo Express/Redis Commander apenas quando necessário via `docker-compose --profile tools up -d`.

## Estilo de Código e Convenções de Nomenclatura
Backend Python segue Black (PEP8 com 4 espaços), isort (stdlib → third-party → local), flake8, e APIs públicas com type hints. Módulos usam `snake_case`, modelos Pydantic `PascalCase`, variáveis de ambiente `UPPER_SNAKE_CASE`, e schemas/DTOs ficam em `backend/app/schemas`. Frontend React usa ESLint + Prettier; componentes usam `PascalCase`, hooks/utilitários `camelCase`, e estado compartilhado reside em `src/stores`.

## Diretrizes de Testes
`backend/tests/{unit,integration}` hospedam as suítes Pytest; nomeie arquivos `test_<feature>.py` e mantenha cobertura ≥85% (`docker-compose exec api pytest --cov=app`). Testes unitários do frontend rodam via `npm run test`; snapshots ficam em `__tests__/`. Execute `scripts/test_routes.sh` antes de cada PR e registre fixtures em `docs/TESTING.md`.

## Diretrizes de Commit e Pull Request
Commits devem ser concisos e imperativos (ex: `Add teacher activity seed data`) com escopos opcionais (`auth: fix JWT refresh`). Antes de cada PR execute `make lint test` mais `npm run lint`/`npm test` (ou comando frontend relevante) e resuma os resultados. PRs devem linkar sua issue, descrever impacto na UX, anexar capturas de UI quando relevante, e anotar passos de config ou migração (`make db-migrate`). Mantenha secrets fora do Git e documente novos endpoints.

## Orientações Específicas por Função
- **Agentes Backend**: Mantenha routes/services em `backend/app` sincronizados com schemas e migrações Alembic (`make db-migrate`); atualize scripts de seed sempre que modelos mudarem.
- **Agentes Frontend**: Organize páginas, componentes e hooks dentro de `frontend/src`, espelhe contratos do backend, e cubra mudanças de estado com Vitest + React Testing Library.
- **Agentes ML & Infra**: Versione artefatos treinados em `ml_models/` com notas README curtas, registre configs de treinamento em `docs/`, e atualize Docker/Terraform/CI juntos documentando novas variáveis de ambiente.

## Notas de Segurança e Configuração
Copie `.env.example` ➝ `.env` na raiz do repo e dentro de `backend/` ao executar a API fora do Docker. Nunca commite `.env`, chaves de API ou credenciais geradas—use AWS Secrets Manager/SSM. Remova identificadores de alunos antes de compartilhar datasets/logs e mantenha dumps dentro de `logs/` ou `backups/` (gitignored).
