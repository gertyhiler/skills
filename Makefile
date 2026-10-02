SHELL := /bin/sh
.DEFAULT_GOAL := help
.PHONY: help setup check verify test build dev stop doctor clean
help: ## Show commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
doctor: ## Check Python and Git without installation
	@command -v python3 >/dev/null
	@command -v git >/dev/null
setup: doctor ## Install validation dependencies into an isolated local venv
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements-dev.txt
check: ## Validate skill metadata and local documentation links
	.venv/bin/python scripts/check.py
verify: check ## Structural verification; behavioral scenarios remain separate
test: ## Explain behavioral verification boundary
	@printf 'No executable workflow tests: review changed skills against scoped scenarios. make check validates structure only.\n'
build: ## No generated application or distributable build
	@printf 'Skills are published as Markdown; no build is required.\n'
dev: ## No development server
	@printf 'Edit skills and run make check. No service is started.\n'
stop: ## No managed background process
	@printf 'No background processes are managed.\n'
clean: ## No repository artifact deletion
	@printf 'No generated artifacts are managed. Local .venv and .agents/work are preserved.\n'
