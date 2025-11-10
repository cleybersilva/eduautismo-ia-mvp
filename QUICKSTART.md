# 🚀 Quick Start Guide - EduAutismo IA

Get the application running in under 5 minutes!

## Prerequisites

✅ Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
✅ OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
✅ 4GB+ RAM available
✅ 10GB+ free disk space

## Step 1: Setup Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: Change OPENAI_API_KEY=sk-your-key-here
nano .env  # or use your preferred editor
```

**IMPORTANT**: You MUST add your OpenAI API key in `.env` for the application to work!

## Step 2: Start Services (2-3 minutes)

```bash
# Using Make (recommended)
make dev

# OR using docker-compose directly
docker-compose up -d
```

The first time will take 2-3 minutes to download images and build containers.

## Step 3: Verify Services (30 seconds)

```bash
# Check if all services are healthy
make health

# OR manually check
docker-compose ps
```

All services should show "healthy" status.

## Step 4: Access the Application

### 🎯 Main Services

| What | URL | Description |
|------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Frontend** | http://localhost:5173 | React application |
| **Health Check** | http://localhost:8000/health | API status |

### 🛠️ Admin Tools (Optional)

Access database management UIs:

| Tool | URL | Credentials |
|------|-----|-------------|
| **Adminer** (PostgreSQL) | http://localhost:8080 | System: PostgreSQL<br>Server: postgres<br>User: eduautismo<br>Password: (from .env) |
| **Mongo Express** | http://localhost:8081 | admin / admin |
| **Redis Commander** | http://localhost:8082 | No credentials needed |

To enable admin tools:
```bash
docker-compose --profile tools up -d
```

## Step 5: Verify Everything Works

### Test API

```bash
# Using curl
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### Test Database

```bash
# Run migrations
make db-migrate

# OR
docker-compose exec api alembic upgrade head
```

### Run Tests

```bash
# Run all tests
make test

# OR
docker-compose exec api pytest -v
```

## Common Commands

```bash
# View logs
make logs              # All services
make logs-api          # API only
make logs-frontend     # Frontend only

# Stop services
make stop

# Restart services
make restart

# Open API shell
make shell-api

# Run database migrations
make db-migrate

# Show all available commands
make help
```

## Troubleshooting

### Services won't start?

```bash
# Check logs for errors
docker-compose logs

# Rebuild everything
docker-compose down -v
docker-compose up -d --build
```

### Port already in use?

Edit `.env` and change the port:
```env
API_PORT=8001  # Instead of 8000
FRONTEND_PORT=5174  # Instead of 5173
```

### Can't connect to database?

```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Wait a few seconds for it to be healthy
docker-compose ps
```

### Out of memory?

Increase Docker memory in Docker Desktop:
- Settings → Resources → Memory
- Set to at least 4GB

## Next Steps

### 1. Configure the Application

Edit `backend/.env.example` for backend-specific settings:
```bash
cd backend
cp .env.example .env
nano .env
```

### 2. Set Up Database

```bash
# Run migrations
make db-migrate

# Seed with sample data (optional)
docker-compose exec api python scripts/seed_database.py
```

### 3. Explore the API

Visit http://localhost:8000/docs to explore all endpoints:
- Student management
- Activity generation
- Assessments
- Authentication

### 4. Start Development

```bash
# Backend code is in backend/app/
# Frontend code is in frontend/src/

# Changes will auto-reload thanks to hot-reload!
```

## Development Workflow

### Making Changes

1. **Backend**: Edit files in `backend/app/`
   - Changes auto-reload (hot-reload enabled)
   - Check logs: `make logs-api`

2. **Frontend**: Edit files in `frontend/src/`
   - Changes auto-reload (Vite HMR enabled)
   - Check logs: `make logs-frontend`

### Adding Dependencies

```bash
# Backend (Python)
docker-compose exec api pip install package-name
# Then update requirements.txt
docker-compose exec api pip freeze > backend/requirements.txt

# Frontend (NPM)
docker-compose exec frontend npm install package-name
```

### Running Commands

```bash
# API shell
make shell-api
# Inside container:
# - pytest
# - alembic upgrade head
# - python scripts/your_script.py

# Database shell
make db-shell
# Inside postgres:
# - \dt (list tables)
# - SELECT * FROM students;
```

## Production Deployment

For production deployment guide, see:
- [Docker Guide](docs/DOCKER.md)
- [Deployment Guide](docs/deployment.md) (if available)

Or use:
```bash
# Build production images
make build-prod

# Start production stack
make prod
```

## Need Help?

- 📖 [Full Docker Guide](docs/DOCKER.md)
- 📊 [Structure Validation](docs/structure-validation.md)
- 📝 [Main README](README.md)
- 🤖 [Claude Guide](CLAUDE.md)

## Useful Links

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**Time to get started**: ~5 minutes
**Prerequisites**: Docker + OpenAI API Key
**Status**: ✅ Ready for development

Happy coding! 🎉
