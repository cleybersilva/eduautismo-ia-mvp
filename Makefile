# ============================================================================
# EduAutismo IA - Makefile
# Convenient commands for development and deployment
# ============================================================================

.PHONY: help
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)EduAutismo IA - Available Commands$(NC)'
	@echo ''
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''

# ============================================================================
# Setup Commands
# ============================================================================

setup: ## Initial project setup
	@echo '$(BLUE)Setting up project...$(NC)'
	@cp -n .env.example .env || true
	@echo '$(YELLOW)Please edit .env and add your OpenAI API key$(NC)'
	@echo '$(GREEN)Setup complete! Run "make dev" to start$(NC)'

install-deps: ## Install all dependencies
	@echo '$(BLUE)Installing backend dependencies...$(NC)'
	@cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@echo '$(BLUE)Installing frontend dependencies...$(NC)'
	@cd frontend && npm install
	@echo '$(GREEN)Dependencies installed!$(NC)'

# ============================================================================
# Docker Commands
# ============================================================================

dev: ## Start development environment
	@echo '$(BLUE)Starting development environment...$(NC)'
	@docker-compose up -d
	@echo '$(GREEN)Services started!$(NC)'
	@echo 'API: http://localhost:8000/docs'
	@echo 'Frontend: http://localhost:5173'

dev-build: ## Build and start development environment
	@echo '$(BLUE)Building and starting development environment...$(NC)'
	@docker-compose up -d --build
	@echo '$(GREEN)Services built and started!$(NC)'

stop: ## Stop all services
	@echo '$(BLUE)Stopping services...$(NC)'
	@docker-compose down
	@echo '$(GREEN)Services stopped!$(NC)'

restart: ## Restart all services
	@echo '$(BLUE)Restarting services...$(NC)'
	@docker-compose restart
	@echo '$(GREEN)Services restarted!$(NC)'

clean: ## Stop services and remove volumes (WARNING: deletes all data!)
	@echo '$(RED)WARNING: This will delete all data!$(NC)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo '$(GREEN)Services stopped and volumes removed!$(NC)'; \
	fi

logs: ## View logs from all services
	@docker-compose logs -f

logs-api: ## View API logs
	@docker-compose logs -f api

logs-frontend: ## View frontend logs
	@docker-compose logs -f frontend

logs-db: ## View database logs
	@docker-compose logs -f postgres

ps: ## Show running services
	@docker-compose ps

# ============================================================================
# Database Commands
# ============================================================================

db-migrate: ## Run database migrations
	@echo '$(BLUE)Running migrations...$(NC)'
	@docker-compose exec api alembic upgrade head
	@echo '$(GREEN)Migrations complete!$(NC)'

db-rollback: ## Rollback last migration
	@echo '$(BLUE)Rolling back migration...$(NC)'
	@docker-compose exec api alembic downgrade -1
	@echo '$(GREEN)Rollback complete!$(NC)'

db-shell: ## Connect to PostgreSQL shell
	@docker-compose exec postgres psql -U eduautismo -d eduautismo_dev

db-backup: ## Backup database
	@echo '$(BLUE)Backing up database...$(NC)'
	@mkdir -p backups
	@docker-compose exec postgres pg_dump -U eduautismo eduautismo_dev > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo '$(GREEN)Backup created in backups/ directory$(NC)'

db-restore: ## Restore database from latest backup
	@echo '$(BLUE)Restoring database...$(NC)'
	@docker-compose exec -T postgres psql -U eduautismo eduautismo_dev < $$(ls -t backups/*.sql | head -1)
	@echo '$(GREEN)Database restored!$(NC)'

db-reset: ## Reset database (WARNING: deletes all data!)
	@echo '$(RED)WARNING: This will delete all database data!$(NC)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v postgres; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose exec api alembic upgrade head; \
		echo '$(GREEN)Database reset complete!$(NC)'; \
	fi

# ============================================================================
# Testing Commands
# ============================================================================

test: ## Run all tests
	@echo '$(BLUE)Running tests...$(NC)'
	@docker-compose exec api pytest -v
	@echo '$(GREEN)Tests complete!$(NC)'

test-unit: ## Run unit tests only
	@docker-compose exec api pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@docker-compose exec api pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	@docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term
	@echo '$(GREEN)Coverage report generated in htmlcov/$(NC)'

lint: ## Run linting checks
	@echo '$(BLUE)Running linters...$(NC)'
	@docker-compose exec api flake8 app/
	@docker-compose exec api black app/ --check
	@docker-compose exec api isort app/ --check-only

format: ## Format code
	@echo '$(BLUE)Formatting code...$(NC)'
	@docker-compose exec api black app/
	@docker-compose exec api isort app/
	@echo '$(GREEN)Code formatted!$(NC)'

# ============================================================================
# Shell Access Commands
# ============================================================================

shell-api: ## Open shell in API container
	@docker-compose exec api bash

shell-frontend: ## Open shell in frontend container
	@docker-compose exec frontend sh

shell-db: ## Open shell in database container
	@docker-compose exec postgres bash

# ============================================================================
# Build Commands
# ============================================================================

build: ## Build all images
	@echo '$(BLUE)Building images...$(NC)'
	@docker-compose build
	@echo '$(GREEN)Build complete!$(NC)'

build-api: ## Build API image only
	@docker-compose build api

build-frontend: ## Build frontend image only
	@docker-compose build frontend

build-prod: ## Build production images
	@echo '$(BLUE)Building production images...$(NC)'
	@docker build --target production -t eduautismo-api:prod -f Dockerfile.api .
	@docker build --target production -t eduautismo-web:prod -f Dockerfile.web .
	@echo '$(GREEN)Production images built!$(NC)'

# ============================================================================
# Validation Commands
# ============================================================================

validate: ## Validate project structure
	@python scripts/check_structure.py --report-only

validate-fix: ## Validate and create missing files
	@python scripts/check_structure.py --create-missing --priority 2

health: ## Check health of all services
	@echo '$(BLUE)Checking service health...$(NC)'
	@docker-compose ps
	@echo ''
	@curl -sf http://localhost:8000/health > /dev/null && echo '$(GREEN)✓ API is healthy$(NC)' || echo '$(RED)✗ API is not responding$(NC)'
	@curl -sf http://localhost:5173 > /dev/null && echo '$(GREEN)✓ Frontend is healthy$(NC)' || echo '$(RED)✗ Frontend is not responding$(NC)'

# ============================================================================
# Cleanup Commands
# ============================================================================

clean-docker: ## Clean Docker system (remove unused images, containers, etc)
	@echo '$(BLUE)Cleaning Docker system...$(NC)'
	@docker system prune -f
	@echo '$(GREEN)Docker system cleaned!$(NC)'

clean-all: ## Clean everything (Docker + volumes + cache)
	@echo '$(RED)WARNING: This will remove all Docker data and caches!$(NC)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker system prune -a -f; \
		rm -rf backend/__pycache__ backend/.pytest_cache; \
		rm -rf frontend/node_modules frontend/dist; \
		echo '$(GREEN)Everything cleaned!$(NC)'; \
	fi

# ============================================================================
# Utility Commands
# ============================================================================

urls: ## Show all service URLs
	@echo '$(BLUE)Service URLs:$(NC)'
	@echo 'API Documentation: http://localhost:8000/docs'
	@echo 'API Health Check: http://localhost:8000/health'
	@echo 'Frontend: http://localhost:5173'
	@echo 'Adminer (DB): http://localhost:8080'
	@echo 'Mongo Express: http://localhost:8081'
	@echo 'Redis Commander: http://localhost:8082'

stats: ## Show Docker resource usage
	@docker stats --no-stream

info: ## Show system information
	@echo '$(BLUE)System Information:$(NC)'
	@docker --version
	@docker-compose --version
	@echo ''
	@docker-compose ps

# ============================================================================
# Production Commands
# ============================================================================

prod: ## Start production environment
	@echo '$(BLUE)Starting production environment...$(NC)'
	@docker-compose -f docker-compose.prod.yml up -d
	@echo '$(GREEN)Production services started!$(NC)'

prod-logs: ## View production logs
	@docker-compose -f docker-compose.prod.yml logs -f

prod-stop: ## Stop production environment
	@docker-compose -f docker-compose.prod.yml down

# ============================================================================
# Documentation
# ============================================================================

docs: ## Generate and open documentation
	@echo '$(BLUE)Documentation available at:$(NC)'
	@echo 'API Docs: http://localhost:8000/docs'
	@echo 'Project README: ./README.md'
	@echo 'Docker Guide: ./docs/DOCKER.md'
	@echo 'Structure Validation: ./docs/structure-validation.md'
