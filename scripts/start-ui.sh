#!/bin/bash
# Start CowAgent Web UI (frontend only)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/.cowagent-ui.pid"
LOG_FILE="${COW_LOG_FILE:-${BASE_DIR}/logs/coweb.log}"

source "$SCRIPT_DIR/shared.sh"

# Get web port from config
get_web_port() {
    if [ -f "${BASE_DIR}/config.json" ]; then
        python3 -c "
import json, sys
try:
    with open('${BASE_DIR}/config.json') as f:
        print(json.load(f).get('web_port', 9899))
except Exception:
    print(9899)
" 2>/dev/null || echo "9899"
    else
        echo "9899"
    fi
}

LOG_DIR=$(dirname "$LOG_FILE")
mkdir -p "$LOG_DIR"

# Check if UI is already running
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}${EMOJI_WARN} Web UI is already running (PID: ${pid})${NC}"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

if [ ! -f "${BASE_DIR}/config.json" ]; then
    echo -e "${RED}${EMOJI_CROSS} config.json not found${NC}"
    exit 1
fi

check_python_version

WEB_PORT=$(get_web_port)

echo -e "${GREEN}${EMOJI_COW} Starting CowAgent Web UI...${NC}"

# Start only the web channel, skip plugin loading (no agent needed for UI)
export COW_CHANNEL=web
export COW_WEB_CONSOLE=false
export COW_SKIP_PLUGINS=true

nohup $PYTHON_CMD -m cowagent >> "${LOG_FILE}" 2>&1 &
echo $! > "$PID_FILE"

sleep 2

if kill -0 "$!" 2>/dev/null; then
    echo -e "${GREEN}${EMOJI_CHECK} CowAgent Web UI started (PID=$(cat "$PID_FILE"))${NC}"
    echo -e "${GREEN}Web UI: http://localhost:${WEB_PORT}${NC}"
    echo -e "${GREEN}Log:  ${LOG_FILE}${NC}"
else
    echo -e "${RED}${EMOJI_CROSS} Web UI failed to start, check ${LOG_FILE}${NC}"
    exit 1
fi
