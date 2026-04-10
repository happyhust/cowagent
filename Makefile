.PHONY: start stop restart status clean init install help

BASE_DIR := $(shell pwd)

.DEFAULT_GOAL := help

start:
	@$(BASE_DIR)/scripts/start.sh

stop:
	@$(BASE_DIR)/scripts/stop.sh

restart: stop start

status:
	@$(BASE_DIR)/scripts/status.sh

# Install and configure (interactive wizard)
install:
	@$(BASE_DIR)/scripts/install.sh

# Install dependencies only (non-interactive)
init:
	@$(BASE_DIR)/scripts/init.sh

# Clean logs and temp files
clean:
	@echo "Cleaning logs..."
	@rm -f nohup.out run.log cowagent.pid
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."

help:
	@echo "CowAgent Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  start      Start the service"
	@echo "  stop       Stop the service"
	@echo "  restart    Restart the service"
	@echo "  status     Check service status"
	@echo "  clean      Remove logs and __pycache__"
	@echo "  init       Install dependencies (non-interactive)"
	@echo "  install    Interactive setup wizard (model, channel, config)"
	@echo "  help       Show this help message"
