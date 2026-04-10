# CowAgent uses uv for Python environment management
# uv will create a venv with Python 3.12 and install dependencies

.PHONY: start stop restart status clean format lint test help start-ui stop-ui uv-sync

BASE_DIR := $(shell pwd)

.DEFAULT_GOAL := help

start:
	@$(BASE_DIR)/scripts/start.sh

stop:
	@$(BASE_DIR)/scripts/stop.sh

restart: stop start

status:
	@$(BASE_DIR)/scripts/status.sh

# Start Web UI (frontend only, requires backend running)
start-ui:
	@$(BASE_DIR)/scripts/start-ui.sh

# Stop Web UI
stop-ui:
	@$(BASE_DIR)/scripts/stop-ui.sh

# Sync dependencies with uv (creates venv with Python 3.12 if needed)
uv-sync:
	@uv python install 3.12 --install-dir "$(BASE_DIR)/.python" 2>/dev/null || true
	@uv sync --python "$(BASE_DIR)/.python/3.12" --all-extras --dev 2>/dev/null \
		|| uv sync --all-extras

# Install and configure (interactive wizard)
install:
	@$(BASE_DIR)/scripts/install.sh

# Install dependencies only (non-interactive)
init: uv-sync

# Clean logs and temp files
clean:
	@echo "Cleaning logs..."
	@rm -f nohup.out run.log cowagent.pid
	@rm -rf logs/*
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."

# Format code with ruff (auto-installs if missing)
format:
	@command -v ruff >/dev/null 2>&1 || pip3 install ruff
	ruff format cowagent/ scripts/
	@command -v prettier >/dev/null 2>&1 || npm install -g prettier
	@if [ -d bridge ] && find bridge -type f \( -name "*.html" -o -name "*.js" -o -name "*.ts" -o -name "*.css" -o -name "*.json" \) | grep -q .; then \
		prettier --write "bridge/**/*.{html,js,ts,css,json}" --log-level warn; \
	fi

# Lint code with ruff (auto-installs if missing)
lint:
	@command -v ruff >/dev/null 2>&1 || pip3 install ruff
	ruff check cowagent/ scripts/
	@command -v prettier >/dev/null 2>&1 || npm install -g prettier
	@if [ -d bridge ] && find bridge -type f \( -name "*.html" -o -name "*.js" -o -name "*.ts" -o -name "*.css" \) | grep -q .; then \
		prettier --check "bridge/**/*.{html,js,ts,css}"; \
	fi

# Run tests: unit tests first, then integration tests
test:
	@command -v pytest >/dev/null 2>&1 || pip3 install pytest
	@echo "===== Running cowagent/ unit tests ====="
	pytest cowagent/tests/ -v --tb=short
	@echo ""
	@echo "===== Running bridge/ unit tests ====="
	pytest bridge/tests/ -v --tb=short
	@echo ""
	@echo "===== Running integration tests ====="
	pytest tests/ -v --tb=short

help:
	@echo "CowAgent Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  start      Start the backend service"
	@echo "  stop       Stop the service"
	@echo "  restart    Restart the service"
	@echo "  status     Check service status"
	@echo "  start-ui   Start Web UI (frontend, requires backend)"
	@echo "  stop-ui    Stop Web UI"
	@echo "  uv-sync    Sync dependencies with uv (Python 3.12)"
	@echo "  clean      Remove logs and __pycache__"
	@echo "  init       Install dependencies via uv"
	@echo "  install    Interactive setup wizard (model, channel, config)"
	@echo "  format     Format code (Python + frontend)"
	@echo "  lint       Lint code (Python + frontend)"
	@echo "  test       Run unit tests + integration tests"
	@echo "  help       Show this help message"
