#!/bin/bash
# Start CowAgent service
set -e
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

# Log file path — override via environment variable if needed
LOG_FILE="${COW_LOG_FILE:-$HOME/cow/cowagent.log}"

source "$SCRIPT_DIR/shared.sh"

start_project() {
    local LOG_DIR
    LOG_DIR=$(dirname "$LOG_FILE")
    mkdir -p "$LOG_DIR"

    nohup $PYTHON_CMD "${BASE_DIR}/app.py" >> "${LOG_FILE}" 2>&1 &
    echo $! > "${BASE_DIR}/cowagent.pid"
    echo -e "${GREEN}${EMOJI_COW} CowAgent started (PID=$(cat "${BASE_DIR}/cowagent.pid"))${NC}"
    echo -e "${GREEN}Log: ${LOG_FILE}${NC}"

    sleep 2
    echo ""
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo -e "${GREEN}${EMOJI_CHECK} CowAgent is now running in background!${NC}"
    echo -e "${GREEN}${EMOJI_CHECK} Process will continue after closing terminal.${NC}"
    echo -e "${CYAN}Weixin channel configured. Scan QR code in terminal or web console to login.${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}Management Commands:${NC}"
    echo -e "  ${GREEN}./scripts/stop.sh${NC}        Stop the service"
    echo -e "  ${GREEN}./scripts/start.sh${NC}       Start the service"
    echo -e "  ${GREEN}./scripts/install.sh${NC}     Install dependencies"
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo ""

    echo -e "${YELLOW}Showing recent logs (Ctrl+C to exit, agent keeps running):${NC}"
    sleep 2
    tail -n 30 -f "${LOG_FILE}"
}

if [ ! -f "${BASE_DIR}/config.json" ]; then
    echo -e "${RED}${EMOJI_CROSS} config.json not found${NC}"
    echo -e "${YELLOW}Please run './scripts/install.sh' to configure first${NC}"
    exit 1
fi

if is_running; then
    echo -e "${YELLOW}${EMOJI_WARN} CowAgent is already running (PID: $(get_pid))${NC}"
    echo -e "${YELLOW}Use './scripts/stop.sh && ./scripts/start.sh' to restart${NC}"
    exit 0
fi

check_python_version
start_project
