SHELL := /bin/sh
.DEFAULT_GOAL := help
.PHONY: help setup check verify test build dev stop doctor clean
help: ## Show commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
doctor: ## Check Python, Node and Git without installation
	@command -v python3 >/dev/null
	@command -v git >/dev/null
	@command -v node >/dev/null
setup: doctor ## Install local Python and Node validation dependencies
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements-dev.txt
	npm ci
check: ## Validate skill metadata and local documentation links
	.venv/bin/python scripts/check.py
verify: check test ## Validate structure and run isolated helper tests
test: ## Run helper tests; optional integration requires SKILLS_TEST_DATABASE_URL
	npm test
build: ## No generated application or distributable build
	@printf 'Skills are published as Markdown; no build is required.\n'
dev: ## No development server
	@printf 'Edit skills and run make check. No service is started.\n'
stop: ## No managed background process
	@printf 'No background processes are managed.\n'
clean: ## No repository artifact deletion
	@printf 'No generated artifacts are managed. Local .venv and .agents/work are preserved.\n'
