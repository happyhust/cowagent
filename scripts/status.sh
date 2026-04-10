#!/bin/bash
# Check CowAgent service status
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/.cowagent.pid"
UI_PID_FILE="${BASE_DIR}/.cowagent-ui.pid"

source "$SCRIPT_DIR/shared.sh"

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

echo -e "${CYAN}${BOLD}=========================================${NC}"
echo -e "${CYAN}${BOLD}   ${EMOJI_COW} CowAgent Status${NC}"
echo -e "${CYAN}${BOLD}=========================================${NC}"

# Backend status
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}Backend:${NC}  ✅ Running (PID=${pid})"
    else
        echo -e "${YELLOW}Backend:${NC}  ⭐ Stopped (stale PID)"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${YELLOW}Backend:${NC}  ⭐ Stopped"
fi

# Web UI status
WEB_PORT=$(get_web_port)
if [ -f "$UI_PID_FILE" ]; then
    pid=$(cat "$UI_PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}Web UI:${NC}  ✅ Running (PID=${pid}, :${WEB_PORT})"
    else
        echo -e "${YELLOW}Web UI:${NC}  ⭐ Stopped (stale PID)"
        rm -f "$UI_PID_FILE"
    fi
else
    echo -e "${YELLOW}Web UI:${NC}  ⭐ Stopped (run 'make start-ui')"
fi

echo -e "${CYAN}${BOLD}-----------------------------------------${NC}"

if [ -f "${BASE_DIR}/config.json" ]; then
    model=$(grep -o '"model"[[:space:]]*:[[:space:]]*"[^"]*"' "${BASE_DIR}/config.json" | cut -d'"' -f4)
    channel=$(grep -o '"channel_type"[[:space:]]*:[[:space:]]*"[^"]*"' "${BASE_DIR}/config.json" | cut -d'"' -f4)
    echo -e "${GREEN}Model:${NC}   ${model}"
    echo -e "${GREEN}Channel:${NC}  ${channel}"
fi

echo -e "${CYAN}${BOLD}=========================================${NC}"
