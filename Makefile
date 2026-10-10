# ═══════════════════════════════════════════════
#  GrabVid Makefile
# ═══════════════════════════════════════════════

.PHONY: install install-gui install-all dev test clean lint format run-gui help

PYTHON ?= python3
PIP ?= pip3

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install core (CLI only)
	$(PIP) install -e .

install-gui: ## Install with GUI support
	$(PIP) install -e ".[gui]"

install-all: ## Install everything
	$(PIP) install -e ".[all]"

dev: ## Install dev dependencies
	$(PIP) install -e ".[dev]"

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

lint: ## Run linter
	ruff check src/

format: ## Format code
	black src/ tests/

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run-gui: ## Launch the GUI
	$(PYTHON) -m src.gui.app

cli: ## Run CLI help
	$(PYTHON) -m src.cli.main
