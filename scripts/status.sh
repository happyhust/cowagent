#!/bin/bash
# Check CowAgent service status
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/.cowagent.pid"

source "$SCRIPT_DIR/shared.sh"

echo -e "${CYAN}${BOLD}=========================================${NC}"
echo -e "${CYAN}${BOLD}   ${EMOJI_COW} CowAgent Status${NC}"
echo -e "${CYAN}${BOLD}=========================================${NC}"

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}Status:${NC} ✅ Running"
        echo -e "${GREEN}PID:${NC}    ${pid}"
    else
        echo -e "${YELLOW}Status:${NC} ⭐ Stopped (stale PID file)"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${YELLOW}Status:${NC} ⭐ Stopped"
fi

if [ -f "${BASE_DIR}/config.json" ]; then
    model=$(grep -o '"model"[[:space:]]*:[[:space:]]*"[^"]*"' "${BASE_DIR}/config.json" | cut -d'"' -f4)
    channel=$(grep -o '"channel_type"[[:space:]]*:[[:space:]]*"[^"]*"' "${BASE_DIR}/config.json" | cut -d'"' -f4)
    echo -e "${GREEN}Model:${NC}  ${model}"
    echo -e "${GREEN}Channel:${NC} ${channel}"
fi

echo -e "${CYAN}${BOLD}=========================================${NC}"
