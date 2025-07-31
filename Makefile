.PHONY: help install install-dev run test format lint type-check clean setup

help: ## Show this help message
	@echo "Interview Assistant - Development Commands"
	@echo "=========================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial setup of the project
	@echo "Setting up Interview Assistant project..."
	poetry install
	poetry run pre-commit install
	@echo "✅ Setup complete! Run 'make run' to start the application."

install: ## Install production dependencies
	poetry install --only main

install-dev: ## Install all dependencies including development
	poetry install

run: ## Run the Streamlit application
	poetry run streamlit run run_app.py

test: ## Run tests
	poetry run pytest

format: ## Format code with Black
	poetry run black .

lint: ## Lint code with flake8
	poetry run flake8 .

type-check: ## Run type checking with mypy
	poetry run mypy .

check: format lint type-check ## Run all code quality checks

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

update: ## Update all dependencies
	poetry update

add-dep: ## Add a new dependency (usage: make add-dep PKG=package-name)
	poetry add $(PKG)

add-dev: ## Add a new development dependency (usage: make add-dev PKG=package-name)
	poetry add --group dev $(PKG)

shell: ## Activate Poetry shell
	poetry shell

build: ## Build the project
	poetry build

publish: ## Publish to PyPI (if configured)
	poetry publish 