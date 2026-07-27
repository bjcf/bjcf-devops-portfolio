.DEFAULT_GOAL := help
APP_DIR := app

.PHONY: help install test lint run docker-build compose-up compose-down helm-lint tf-validate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install app dev dependencies
	cd $(APP_DIR) && pip install -r requirements-dev.txt

test: ## Run unit tests
	cd $(APP_DIR) && pytest

lint: ## Lint the app with ruff
	cd $(APP_DIR) && ruff check .

run: ## Run the API locally with hot reload
	cd $(APP_DIR) && uvicorn app.main:app --reload

docker-build: ## Build the container image
	docker build -t bjcf-devops-portfolio:local $(APP_DIR)

compose-up: ## Start API + Prometheus + Grafana
	docker compose up --build

compose-down: ## Stop the local stack
	docker compose down -v

helm-lint: ## Lint and render the Helm chart
	helm lint deploy/helm/api && helm template api deploy/helm/api > /dev/null

tf-validate: ## Format-check and validate Terraform
	cd infra/terraform && terraform fmt -check -recursive && terraform init -backend=false && terraform validate
