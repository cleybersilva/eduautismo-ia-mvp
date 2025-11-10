# Docker Setup Guide - EduAutismo IA

## Overview

This project uses Docker and Docker Compose to provide a consistent development and production environment. The setup includes:

- **FastAPI Backend** (Python 3.11)
- **React Frontend** (Node 20 + Vite)
- **PostgreSQL** (Database)
- **MongoDB** (Logs & Analytics)
- **Redis** (Cache & Sessions)
- **Admin Tools** (Adminer, Mongo Express, Redis Commander)

## Prerequisites

- Docker Desktop 20.10+ or Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for Docker
- At least 10GB free disk space

### Installation

**macOS:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
Download from [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository (if not already done)
cd eduautismo-ia-mvp

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key (REQUIRED)
nano .env  # or use your preferred editor
```

**IMPORTANT**: Add your OpenAI API key to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Start All Services

```bash
# Start everything (first time will download images)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access the Application

Once all services are healthy (this may take 1-2 minutes):

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | - |
| **Frontend** | http://localhost:5173 | - |
| **Adminer (DB UI)** | http://localhost:8080 | System: PostgreSQL<br>Server: postgres<br>User: eduautismo<br>Password: (from .env) |
| **Mongo Express** | http://localhost:8081 | admin / admin |
| **Redis Commander** | http://localhost:8082 | - |

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data!)
docker-compose down -v
```

## Architecture

### Services

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                         │
│                   (eduautismo-network)                      │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │PostgreSQL│   │ MongoDB  │   │  Redis   │               │
│  │  :5432   │   │  :27017  │   │  :6379   │               │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘               │
│       │              │              │                       │
│       │         ┌────┴──────────────┴────┐                 │
│       │         │                        │                 │
│       └─────────┤   FastAPI Backend      │                 │
│                 │       :8000            │                 │
│                 └───────────┬────────────┘                 │
│                             │                              │
│                    ┌────────┴─────────┐                    │
│                    │                  │                    │
│              ┌─────┴─────┐      ┌────┴────┐               │
│              │  Frontend │      │  Admin  │               │
│              │   :5173   │      │  Tools  │               │
│              └───────────┘      └─────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Stage Builds

Both Dockerfiles use multi-stage builds for optimization:

**Dockerfile.api** (Backend):
1. `base` - System dependencies
2. `dependencies` - Python packages
3. `development` - Dev tools + hot-reload
4. `builder` - Build artifacts
5. `production` - Optimized production image

**Dockerfile.web** (Frontend):
1. `base` - Node.js setup
2. `dependencies` - NPM packages
3. `development` - Dev server with hot-reload
4. `builder` - Build production assets
5. `production` - Nginx serving static files

## Development Workflow

### Running in Development Mode

```bash
# Start with hot-reload
docker-compose up -d

# View real-time logs
docker-compose logs -f api
docker-compose logs -f frontend

# Make code changes - they will auto-reload!
# Backend: Edit files in backend/
# Frontend: Edit files in frontend/
```

### Running Commands Inside Containers

```bash
# Backend shell
docker-compose exec api bash

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests
docker-compose exec api pytest

# Frontend shell
docker-compose exec frontend sh

# Install new NPM package
docker-compose exec frontend npm install package-name
```

### Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U eduautismo -d eduautismo_dev

# Backup database
docker-compose exec postgres pg_dump -U eduautismo eduautismo_dev > backup.sql

# Restore database
docker-compose exec -T postgres psql -U eduautismo eduautismo_dev < backup.sql

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec api alembic upgrade head
```

### Debugging

```bash
# View service logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres

# Check service health
docker-compose ps

# Inspect container
docker-compose exec api env
docker inspect eduautismo-api

# Check resource usage
docker stats
```

## Production Deployment

### Building Production Images

```bash
# Build production API image
docker build \
  --target production \
  --build-arg PYTHON_VERSION=3.11 \
  -t eduautismo-api:1.0.0 \
  -f Dockerfile.api .

# Build production Frontend image
docker build \
  --target production \
  --build-arg NODE_VERSION=20 \
  --build-arg VITE_API_URL=https://api.eduautismo.com \
  -t eduautismo-web:1.0.0 \
  -f Dockerfile.web .

# Tag for registry
docker tag eduautismo-api:1.0.0 your-registry.com/eduautismo-api:1.0.0
docker tag eduautismo-web:1.0.0 your-registry.com/eduautismo-web:1.0.0

# Push to registry
docker push your-registry.com/eduautismo-api:1.0.0
docker push your-registry.com/eduautismo-web:1.0.0
```

### Production docker-compose

For production, create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: your-registry.com/eduautismo-api:1.0.0
    environment:
      ENV: production
      DEBUG: false
      # ... other production env vars
    restart: always

  frontend:
    image: your-registry.com/eduautismo-web:1.0.0
    ports:
      - "80:80"
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Admin Tools

### Adminer (Database UI)

Access at http://localhost:8080

Features:
- Browse database tables
- Execute SQL queries
- Import/Export data
- View table relationships

### Mongo Express (MongoDB UI)

Access at http://localhost:8081

Features:
- Browse collections
- Execute queries
- View documents
- Database statistics

### Redis Commander

Access at http://localhost:8082

Features:
- View keys
- Execute Redis commands
- Monitor performance
- Manage data

**Note**: Admin tools are only enabled with profile `tools`:
```bash
docker-compose --profile tools up -d
```

## Environment Variables

### Required Variables

```env
OPENAI_API_KEY=sk-...          # REQUIRED: OpenAI API key
POSTGRES_PASSWORD=...           # Database password
SECRET_KEY=...                  # Application secret (min 32 chars)
JWT_SECRET_KEY=...              # JWT signing key (min 32 chars)
```

### Optional Variables

```env
ENV=development                 # Environment: development/staging/production
DEBUG=true                      # Enable debug mode
LOG_LEVEL=INFO                  # Logging level
AWS_ACCESS_KEY_ID=...          # AWS credentials (optional)
SENTRY_DSN=...                 # Sentry monitoring (optional)
```

See `.env.example` for complete list.

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or :5173, :5432, etc.

# Kill the process or change port in .env
API_PORT=8001
```

### Database Connection Issues

```bash
# Check if postgres is healthy
docker-compose ps postgres

# Check connectivity
docker-compose exec api pg_isready -h postgres -U eduautismo

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
```

### Out of Memory

```bash
# Increase Docker memory limit in Docker Desktop settings
# Recommended: 4GB minimum, 8GB ideal

# Or reduce services
docker-compose up -d api postgres  # Only essential services
```

### Slow Build Times

```bash
# Use BuildKit (faster)
DOCKER_BUILDKIT=1 docker-compose build

# Build in parallel
docker-compose build --parallel

# Use cache from registry
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### Frontend Not Hot-Reloading

```bash
# Check volume mounts
docker-compose exec frontend ls -la /app

# Restart with clean state
docker-compose restart frontend
```

## Performance Optimization

### Reduce Image Size

```bash
# Use multi-stage builds (already implemented)
# Remove unnecessary files in .dockerignore

# Check image sizes
docker images | grep eduautismo

# Analyze image layers
docker history eduautismo-api:latest
```

### Faster Builds

```bash
# Use BuildKit
export DOCKER_BUILDKIT=1

# Cache dependencies separately
# (already implemented in Dockerfiles)

# Use docker-compose build cache
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### Network Performance

```bash
# Use host network for local dev (Linux only)
network_mode: "host"

# Or optimize bridge network
docker network inspect eduautismo-network
```

## Best Practices

### Security

1. **Never commit `.env`** - Always use `.env.example`
2. **Change default passwords** - Use strong passwords in production
3. **Run as non-root** - Already implemented in Dockerfiles
4. **Scan images** - Use `docker scan eduautismo-api:latest`
5. **Keep images updated** - Regularly rebuild with latest base images

### Development

1. **Use volumes** - For hot-reload during development
2. **Health checks** - Monitor service health
3. **Resource limits** - Set memory/CPU limits in production
4. **Logging** - Use structured logging
5. **Backups** - Regular database backups

### Production

1. **Use secrets** - Docker secrets or external secret management
2. **Enable monitoring** - Sentry, Datadog, or similar
3. **Load balancing** - Use multiple replicas
4. **Auto-restart** - `restart: always` policy
5. **Regular updates** - Keep dependencies updated

## Common Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service]

# Rebuild services
docker-compose build

# Restart service
docker-compose restart [service]

# Execute command
docker-compose exec [service] [command]

# View resource usage
docker stats

# Clean up
docker system prune -a

# View networks
docker network ls

# View volumes
docker volume ls
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Docker](https://vitejs.dev/guide/static-deploy.html)

## Support

For Docker-related issues:
1. Check logs: `docker-compose logs`
2. Review this documentation
3. Check [troubleshooting section](#troubleshooting)
4. Open an issue on GitHub

---

**Last Updated**: 2025-01-09
**Docker Version**: 24.0+
**Docker Compose Version**: 2.0+
