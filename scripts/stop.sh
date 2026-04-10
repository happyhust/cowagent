#!/bin/bash
# Stop CowAgent service
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/cowagent.pid"

source "$SCRIPT_DIR/shared.sh"

# Get web port from config (default 9899)
get_web_port() {
    if [ -f "${BASE_DIR}/config.json" ]; then
        # Use python to read JSON safely (avoids jq dependency)
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

# Kill process listening on a given port
kill_port() {
    local port=$1
    local pid=""
    # Try lsof first
    if command -v lsof &> /dev/null; then
        pid=$(lsof -ti :"$port" 2>/dev/null | head -1)
    fi
    # Fallback to ss
    if [ -z "$pid" ] && command -v ss &> /dev/null; then
        pid=$(ss -tlnp "sport = :$port" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
    fi
    # Fallback to netstat
    if [ -z "$pid" ] && command -v netstat &> /dev/null; then
        pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | grep -oP '[0-9]+/' | head -1 | tr -d '/')
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

echo -e "${GREEN}${EMOJI_STOP} Stopping CowAgent...${NC}"

# Try PID file first
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        sleep 2
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$PID_FILE"
            echo -e "${GREEN}${EMOJI_CHECK} CowAgent stopped (PID=$pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  Process not stopped, forcing termination...${NC}"
            kill -9 "$pid"
            rm -f "$PID_FILE"
            echo -e "${GREEN}${EMOJI_CHECK} CowAgent force stopped (PID=$pid)${NC}"
        fi
    else
        echo -e "${YELLOW}Stale PID file, cleaning up.${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Fallback: grep for process
if is_running; then
    pid=$(get_pid)
    echo -e "${GREEN}Found running process (PID: ${pid})${NC}"
    kill "$pid"
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Process not stopped, forcing termination...${NC}"
        kill -9 "$pid"
    fi
    echo -e "${GREEN}${EMOJI_CHECK} CowAgent stopped${NC}"
fi

# Kill web service process on the configured port
WEB_PORT=$(get_web_port)
kill_port "$WEB_PORT"

echo -e "${GREEN}${EMOJI_CHECK} Done.${NC}"
