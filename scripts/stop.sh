#!/bin/bash
# Stop CowAgent service (backend + Web UI)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PID_FILE="${BASE_DIR}/.cowagent.pid"
UI_PID_FILE="${BASE_DIR}/.cowagent-ui.pid"

source "$SCRIPT_DIR/shared.sh"

# Get web port from config (default 9899)
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

# Scan and kill orphan python cowagent processes when PID file is stale
scan_and_kill() {
    local pids
    # Only match python processes running cowagent (not shell scripts or tail)
    pids=$(ps ax 2>/dev/null | grep "python.*cowagent" | grep -v grep | awk '{print $1}')
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}Found orphan cowagent processes via scan: $pids${NC}"
        for pid in $pids; do
            kill "$pid" 2>/dev/null
        done
        sleep 2
        # Force kill any survivors
        for pid in $pids; do
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}Force killing orphan PID=$pid${NC}"
                kill -9 "$pid" 2>/dev/null
            fi
        done
    fi
}

# Stop a process by PID file
stop_by_pid_file() {
    local pid_file=$1
    local label=$2

    if [ ! -f "$pid_file" ]; then
        return 1
    fi

    local pid
    pid=$(cat "$pid_file")
    if ! kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}${label}: Stale PID file ($pid), cleaning up.${NC}"
        rm -f "$pid_file"
        return 1
    fi

    kill "$pid" 2>/dev/null
    sleep 2
    if ! kill -0 "$pid" 2>/dev/null; then
        rm -f "$pid_file"
        echo -e "${GREEN}${EMOJI_CHECK} ${label} stopped (PID=$pid)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  ${label} not stopped, forcing termination...${NC}"
        kill -9 "$pid" 2>/dev/null
        rm -f "$pid_file"
        echo -e "${GREEN}${EMOJI_CHECK} ${label} force stopped (PID=$pid)${NC}"
        return 0
    fi
}

echo -e "${GREEN}${EMOJI_STOP} Stopping CowAgent...${NC}"

# 1. Stop backend
if stop_by_pid_file "$PID_FILE" "Backend"; then
    :
else
    # Fallback: grep for process
    ensure_python_cmd
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        echo -e "${GREEN}Found running process (PID: ${pid})${NC}"
        kill "$pid"
        sleep 3
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Process not stopped, forcing termination...${NC}"
            kill -9 "$pid"
        fi
        echo -e "${GREEN}${EMOJI_CHECK} Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend: not running${NC}"
    fi
fi

# 2. Stop Web UI (standalone)
if stop_by_pid_file "$UI_PID_FILE" "Web UI"; then
    :
else
    echo -e "${YELLOW}Web UI: not running (standalone)${NC}"
fi

# 3. Process scan: kill orphan cowagent processes when PID files are stale
scan_and_kill

# 4. Kill web service process on the configured port
WEB_PORT=$(get_web_port)
kill_port "$WEB_PORT"

echo -e "${GREEN}${EMOJI_CHECK} Done.${NC}"
