#!/bin/bash
# Initialize CowAgent: install dependencies and register cow CLI (non-interactive)
set -e
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

source "$SCRIPT_DIR/shared.sh"

echo -e "${GREEN}${EMOJI_WRENCH} Initializing CowAgent...${NC}"
check_python_version
install_dependencies
echo -e "${GREEN}${EMOJI_CHECK} Initialization complete.${NC}"
