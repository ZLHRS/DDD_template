.PHONY: help env-setup docker-build docker-up docker-down docker-logs app-shell db-shell db-migrate dev

help:
	@echo "backend-template commands"
	@echo "  make env-setup    - copy .env.example to .env"
	@echo "  make docker-build - build docker image"
	@echo "  make docker-up    - start app and postgres"
	@echo "  make docker-down  - stop containers"
	@echo "  make docker-logs  - tail container logs"
	@echo "  make app-shell    - open shell in app container"
	@echo "  make db-shell     - open shell in postgres container"
	@echo "  make db-migrate   - apply alembic migrations"
	@echo "  make dev          - run docker-compose in foreground"

env-setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file"; \
	else \
		echo ".env already exists"; \
	fi

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

app-shell:
	docker-compose exec app sh

db-shell:
	docker-compose exec postgres psql -U postgres -d backend_template_db

db-migrate:
	docker-compose exec app alembic upgrade head

dev:
	docker-compose up

.DEFAULT_GOAL := help
