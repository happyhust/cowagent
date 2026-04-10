#!/bin/bash
# Shared utilities for CowAgent scripts

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Emojis
EMOJI_ROCKET="🚀"
EMOJI_COW="🐄"
EMOJI_CHECK="✅"
EMOJI_CROSS="❌"
EMOJI_WARN="⚠️"
EMOJI_STOP="🛑"
EMOJI_WRENCH="🔧"

# Get project root directory
get_base_dir() {
    cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

# Detect and set Python command
detect_python_command() {
    local FOUND_NEWER_VERSION=""
    for cmd in python3 python python3.12 python3.11 python3.10 python3.9 python3.8 python3.7; do
        if command -v $cmd &> /dev/null; then
            local major_version minor_version
            major_version=$($cmd -c 'import sys; print(sys.version_info[0])' 2>/dev/null)
            minor_version=$($cmd -c 'import sys; print(sys.version_info[1])' 2>/dev/null)
            if [[ "$major_version" == "3" ]]; then
                if (( minor_version >= 7 && minor_version <= 12 )); then
                    PYTHON_CMD=$cmd
                    PYTHON_VERSION="${major_version}.${minor_version}"
                    break
                elif (( minor_version >= 13 )); then
                    if [ -z "$FOUND_NEWER_VERSION" ]; then
                        FOUND_NEWER_VERSION="${major_version}.${minor_version}"
                    fi
                fi
            fi
        fi
    done
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${YELLOW}Tried: python3, python, python3.12, python3.11, python3.10, python3.9, python3.8, python3.7${NC}"
        if [ -n "$FOUND_NEWER_VERSION" ]; then
            echo -e "${RED}❌ Found Python $FOUND_NEWER_VERSION, but this project requires Python 3.7-3.12${NC}"
            echo -e "${YELLOW}Python 3.13+ has compatibility issues with some dependencies (web.py, cgi module removed)${NC}"
        else
            echo -e "${RED}❌ No suitable Python found. Please install Python 3.7-3.12${NC}"
        fi
        exit 1
    fi
    export PYTHON_CMD PYTHON_VERSION
    echo -e "${GREEN}✅ Found Python: $PYTHON_CMD (version $PYTHON_VERSION)${NC}"
}

# Check Python version
check_python_version() {
    detect_python_command
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        echo -e "${RED}❌ pip not found for $PYTHON_CMD. Please install pip.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ pip is available for $PYTHON_CMD${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "${GREEN}📦 Installing dependencies...${NC}"
    local PIP_MIRROR=""
    if curl -s --connect-timeout 5 https://pypi.tuna.tsinghua.edu.cn/simple/ > /dev/null 2>&1; then
        PIP_MIRROR="-i https://pypi.tuna.tsinghua.edu.cn/simple"
    fi

    local PIP_EXTRA_ARGS=""
    if $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        PIP_EXTRA_ARGS="--break-system-packages"
        echo -e "${YELLOW}Python 3.11+ detected, using --break-system-packages for pip installations${NC}"
    fi

    echo -e "${YELLOW}Upgrading pip and basic tools...${NC}"
    set +e
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel importlib_metadata --ignore-installed $PIP_EXTRA_ARGS $PIP_MIRROR > /tmp/pip_upgrade.log 2>&1
    [ $? -ne 0 ] && echo -e "${YELLOW}⚠️  Some tools failed to upgrade, but continuing...${NC}"
    set -e
    rm -f /tmp/pip_upgrade.log

    echo -e "${YELLOW}Installing project dependencies...${NC}"
    set +e
    $PYTHON_CMD -m pip install -r requirements.txt $PIP_EXTRA_ARGS $PIP_MIRROR > /tmp/pip_install.log 2>&1
    local exit_code=$?
    set -e
    cat /tmp/pip_install.log

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencies installed successfully.${NC}"
    elif grep -qE "distutils installed project|uninstall-no-record-file|installed by debian" /tmp/pip_install.log; then
        echo -e "${YELLOW}⚠️  Detected system package conflict, retrying with workaround...${NC}"
        local IGNORE_PACKAGES=""
        for pkg in PyYAML setuptools wheel certifi charset-normalizer; do
            IGNORE_PACKAGES="$IGNORE_PACKAGES --ignore-installed $pkg"
        done
        set +e
        $PYTHON_CMD -m pip install -r requirements.txt $IGNORE_PACKAGES $PIP_EXTRA_ARGS $PIP_MIRROR \
            && echo -e "${GREEN}✅ Dependencies installed successfully (workaround applied).${NC}" \
            || echo -e "${YELLOW}⚠️  Some dependencies may have issues, but continuing...${NC}"
        set -e
    elif grep -q "externally-managed-environment" /tmp/pip_install.log; then
        echo -e "${YELLOW}⚠️  Detected externally-managed environment, retrying with --break-system-packages...${NC}"
        set +e
        $PYTHON_CMD -m pip install -r requirements.txt --break-system-packages $PIP_MIRROR \
            && echo -e "${GREEN}✅ Dependencies installed successfully (system packages override applied).${NC}" \
            || echo -e "${YELLOW}⚠️  Some dependencies may have issues, but continuing...${NC}"
        set -e
    else
        echo -e "${YELLOW}⚠️  Installation had errors, but continuing...${NC}"
    fi
    rm -f /tmp/pip_install.log

    echo -e "${YELLOW}Registering cow CLI...${NC}"
    set +e
    $PYTHON_CMD -m pip install -e . $PIP_EXTRA_ARGS $PIP_MIRROR > /dev/null 2>&1
    if command -v cow &> /dev/null; then
        echo -e "${GREEN}✅ cow CLI registered.${NC}"
    else
        echo -e "${YELLOW}⚠️  cow CLI not in PATH, you can still use: $PYTHON_CMD -m cli.cli${NC}"
    fi

    echo -e "${YELLOW}Installing browser tool...${NC}"
    if command -v cow &> /dev/null; then
        cow install-browser > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Browser tool installed.${NC}"
        else
            echo -e "${YELLOW}⚠️  Browser tool installation failed, skipping...${NC}"
        fi
    elif $PYTHON_CMD -c "import playwright" 2>/dev/null; then
        $PYTHON_CMD -m playwright install chromium > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Playwright browser installed.${NC}"
        else
            echo -e "${YELLOW}⚠️  Playwright browser installation failed, skipping...${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Playwright not installed, skipping browser tool...${NC}"
    fi
    set -e
}

# Check if cow CLI is available
has_cow() {
    command -v cow &> /dev/null
}

# Get PID of running process
get_pid() {
    local PID_FILE="${BASE_DIR}/cowagent.pid"
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
            return
        fi
    fi
    ensure_python_cmd
    ps ax | grep -i "cowagent" | grep "${BASE_DIR}" | grep "$PYTHON_CMD" | grep -v grep | awk '{print $1}' | grep -E '^[0-9]+$' | head -1
}

# Ensure PYTHON_CMD is set
ensure_python_cmd() {
    if [ -z "$PYTHON_CMD" ]; then
        detect_python_command > /dev/null 2>&1 || PYTHON_CMD="python3"
    fi
}

# Check if service is running
is_running() {
    [ -n "$(get_pid)" ]
}
