#!/bin/bash
# Stop CowAgent Web UI (standalone frontend server)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/.cowagent-ui.pid"

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

kill_port() {
    local port=$1
    local pid=""
    if command -v lsof &> /dev/null; then
        pid=$(lsof -ti :"$port" 2>/dev/null | head -1)
    fi
    if [ -z "$pid" ] && command -v ss &> /dev/null; then
        pid=$(ss -tlnp "sport = :$port" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
    fi
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Killing process on port ${port} (PID=$pid)...${NC}"
        kill "$pid" 2>/dev/null
        sleep 1
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
    fi
}

echo -e "${GREEN}${EMOJI_STOP} Stopping CowAgent Web UI...${NC}"

# Try PID file first
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        sleep 2
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$PID_FILE"
            echo -e "${GREEN}${EMOJI_CHECK} Web UI stopped (PID=$pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  Process not stopped, forcing termination...${NC}"
            kill -9 "$pid"
            rm -f "$PID_FILE"
            echo -e "${GREEN}${EMOJI_CHECK} Web UI force stopped (PID=$pid)${NC}"
        fi
    else
        echo -e "${YELLOW}Stale PID file, cleaning up.${NC}"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${YELLOW}Web UI: not running (no PID file)${NC}"
fi

# Fallback: kill process on web port (only if main backend is NOT running)
if [ -f "${BASE_DIR}/.cowagent.pid" ]; then
    main_pid=$(cat "${BASE_DIR}/.cowagent.pid")
    if kill -0 "$main_pid" 2>/dev/null; then
        echo -e "${YELLOW}Backend is running, skipping port cleanup to avoid stopping backend${NC}"
    else
        WEB_PORT=$(get_web_port)
        kill_port "$WEB_PORT"
    fi
else
    WEB_PORT=$(get_web_port)
    kill_port "$WEB_PORT"
fi

echo -e "${GREEN}${EMOJI_CHECK} Done.${NC}"
