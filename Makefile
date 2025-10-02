
.PHONY: help build up down logs clean setup

help: ## Show this help message
	@echo "CRM Agent - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create .env and build images
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

clean: ## Remove containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

shell: ## Open shell in CRM agent container
	docker-compose exec crm-agent /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U crm_user -d crm_database

restart: ## Restart all services
	docker-compose restart

status: ## Show status of all services
	docker-compose ps