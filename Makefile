.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .pytest_cache

.PHONY: black
black: ## Run black.
	poetry run black aws_lambda_script || true

.PHONY: ruff
ruff: ## Run ruff without fixing.
	poetry run ruff check aws_lambda_script || true

.PHONY: pylint
pylint: ## Run pylint.
	poetry run pylint aws_lambda_script || true

.PHONY: lint
lint:  ## Run Python linter
	make black
	make ruff
	make pylint

.PHONY: mypy
mypy:  ## Run mypy.
	poetry run mypy aws_lambda_script

.PHONY: install
install:  ## Install the dependencies excluding dev.
	poetry install --only main --no-root

.PHONY: install-dev
install-dev:  ## Install the dependencies including dev.
	poetry install --only dev --no-root

.PHONY: pytest
pytest:  ## Run pytest
	poetry run pytest