SHELL := /bin/sh
.DEFAULT_GOAL := help
.PHONY: help setup check verify test build dev stop doctor clean
help: ## Show commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
doctor: ## Check uv and Git without installation
	@command -v uv >/dev/null
	@command -v git >/dev/null
setup: doctor ## Install locked Python maintenance dependencies
	uv sync --locked
check: ## Validate skill metadata and local documentation links
	uv run --locked python scripts/check.py
verify: check test ## Validate structure and run isolated helper tests
test: ## Run Python contracts; optional integration requires SKILLS_TEST_DATABASE_URL
	uv run --locked python -m unittest discover -s tests -v
build: ## No generated application or distributable build
	@printf 'Skills are published as Markdown; no build is required.\n'
dev: ## No development server
	@printf 'Edit skills and run make check. No service is started.\n'
stop: ## No managed background process
	@printf 'No background processes are managed.\n'
clean: ## No repository artifact deletion
	@printf 'No generated artifacts are managed. Local .venv and .agents/work are preserved.\n'
