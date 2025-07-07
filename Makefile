.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: uv
uv:  ## Install uv if it's not present.
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: install
install: uv  ## Install the virtual environment and install the pre-commit hooks
	@echo "Creating virtual environment using uv"
	@uv sync --dev
	@uv run pre-commit install

.PHONY: fix
fix: uv  ## Fix lint errors
	@echo "Fix lint errors"
	@uv run ruff check ./src ./tests --fix
	@uv run ruff format ./src ./tests

.PHONY: lint
lint: uv   ## Run linters
	@echo "Linting code"
	@uv run ruff check ./src ./tests
	@uv run mypy ./src ./tests
	@uv run deptry ./src


.PHONY: test
test: uv  ## Run tests
	@echo "Testing code"
	@uv run pytest

.PHONY: make-migration
make-migration:  ## Generate migration
	@if [ -z "$(NAME)" ]; then \
        echo "Error: use MIGRATION_NAME: make make-migration NAME=add_users"; \
        exit 1; \
    fi
	@set -a && source .env && set +a && \
	alembic --config src/social_network/database/migrations/alembic.ini revision -m "$(NAME)"


.PHONY: migrate
migrate:  ## Apply migrations
	@set -a && source .env && set +a && \
	alembic --config src/social_network/database/migrations/alembic.ini upgrade head


.PHONY: rollback-migration
rollback-migration:  ## Rollback migration
	@set -a && source .env && set +a && \
	alembic --config src/social_network/database/migrations/alembic.ini downgrade -1
