# Repository Guidelines

## Project Structure & Module Organization
Repo = FastAPI backend (`backend/app`, `backend/tests`, `backend/alembic`) + Vite/React frontend (`frontend/src`); `Dockerfile.api`, `Dockerfile.web`, `docker-compose.yml`, and the root `Makefile` run the containers. Shared assets (ml_models/, scripts/, docs/, Postman collection) stay at the root, IaC in `terraform/`, and generated artifacts live under the gitignored `logs/`.

## Build, Test, and Development Commands
Use `make dev`, `make stop`, `make db-migrate`, `make test`, and `make lint` for stack control, migrations, tests, and linting. Frontend work runs in `frontend/` (`npm install`, `npm run dev`, `npm run build`). Launch Adminer/Mongo Express/Redis Commander only when required via `docker-compose --profile tools up -d`.

## Coding Style & Naming Conventions
Backend Python follows Black (4-space PEP 8), isort (stdlib → third-party → local), flake8, and type-hinted public APIs. Modules stay `snake_case`, Pydantic models `PascalCase`, env vars `UPPER_SNAKE_CASE`, and schemas/DTOs live under `backend/app/schemas`. Frontend React uses ESLint + Prettier; components use `PascalCase`, hooks/utilities `camelCase`, and shared state resides in `src/stores`.

## Testing Guidelines
`backend/tests/{unit,integration}` host the Pytest suites; name files `test_<feature>.py` and keep coverage ≥85 % (`docker-compose exec api pytest --cov=app`). Frontend unit tests run via `npm run test`; snapshots live under `__tests__/`. Execute `scripts/test_routes.sh` before every PR and record fixtures in `docs/TESTING.md`.

## Commit & Pull Request Guidelines
Commits stay terse and imperative (e.g., `Add teacher activity seed data`) with optional scopes (`auth: fix JWT refresh`). Before each PR run `make lint test` plus `npm run lint`/`npm test` (or the relevant frontend command) and summarize the results. PRs must link their issue, describe UX impact, attach UI captures when relevant, and note config or migration steps (`make db-migrate`). Keep secrets out of Git and document new endpoints.

## Role-Specific Guidance
- **Backend Agents**: Keep routes/services under `backend/app` in sync with schemas and Alembic migrations (`make db-migrate`); refresh seed scripts whenever models change.
- **Frontend Agents**: Organize pages, components, and hooks inside `frontend/src`, mirror backend contracts, and cover state changes with Vitest + React Testing Library.
- **ML & Infra Agents**: Version trained artifacts in `ml_models/` with short README notes, log training configs under `docs/`, and update Docker/Terraform/CI together while documenting new env vars.

## Security & Configuration Notes
Copy `.env.example` ➝ `.env` at the repo root and inside `backend/` when running the API outside Docker. Never commit `.env`, API keys, or generated credentials—use AWS Secrets Manager/SSM. Scrub student identifiers before sharing datasets/logs and keep dumps inside gitignored `logs/` or `backups/`.
