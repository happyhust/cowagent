#!/bin/bash
# Install and configure CowAgent (interactive)
set -e
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BASE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

source "$SCRIPT_DIR/shared.sh"

# Select model
select_model() {
    echo ""
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo -e "${CYAN}${BOLD}   Select AI Model${NC}"
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo -e "${YELLOW}1) MiniMax (MiniMax-M2.7, MiniMax-M2.5, etc.)${NC}"
    echo -e "${YELLOW}2) Zhipu AI (glm-5-turbo, glm-5, etc.)${NC}"
    echo -e "${YELLOW}3) Kimi (kimi-k2.5, kimi-k2, etc.)${NC}"
    echo -e "${YELLOW}4) Doubao (doubao-seed-2-0-code-preview-260215, etc.)${NC}"
    echo -e "${YELLOW}5) Qwen (qwen3.6-plus, qwen3.5-plus, qwen3-max, qwq-plus, etc.)${NC}"
    echo -e "${YELLOW}6) Claude (claude-sonnet-4-6, claude-opus-4-6, etc.)${NC}"
    echo -e "${YELLOW}7) Gemini (gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, etc.)${NC}"
    echo -e "${YELLOW}8) OpenAI GPT (gpt-5.4, gpt-5.2, gpt-4.1, etc.)${NC}"
    echo -e "${YELLOW}9) LinkAI (access multiple models via one API)${NC}"
    echo ""
    while true; do
        read -p "Enter your choice [press Enter for default: 1 - MiniMax]: " model_choice
        model_choice=${model_choice:-1}
        case "$model_choice" in
            1|2|3|4|5|6|7|8|9) break ;;
            *) echo -e "${RED}Invalid choice. Please enter 1-9.${NC}" ;;
        esac
    done
}

read_model_config() {
    local provider=$1 default_model=$2 key_var=$3
    echo -e "${GREEN}Configuring ${provider}...${NC}"
    read -p "Enter ${provider} API Key: " _api_key
    read -p "Enter model name [press Enter for default: ${default_model}]: " model_name
    model_name=${model_name:-$default_model}
    MODEL_NAME="$model_name"
    eval "${key_var}=\"\$_api_key\""
}

read_api_base() {
    local base_var=$1 default_url=$2
    read -p "Enter API Base URL [press Enter for default: ${default_url}]: " api_base
    api_base=${api_base:-$default_url}
    eval "${base_var}=\"\$api_base\""
}

configure_model() {
    case "$model_choice" in
        1) read_model_config "MiniMax" "MiniMax-M2.7" "MINIMAX_KEY" ;;
        2) read_model_config "Zhipu AI" "glm-5-turbo" "ZHIPU_KEY" ;;
        3) read_model_config "Kimi (Moonshot)" "kimi-k2.5" "MOONSHOT_KEY" ;;
        4) read_model_config "Doubao (Volcengine Ark)" "doubao-seed-2-0-code-preview-260215" "ARK_KEY" ;;
        5) read_model_config "Qwen (DashScope)" "qwen3.6-plus" "DASHSCOPE_KEY" ;;
        6)
            read_model_config "Claude" "claude-sonnet-4-6" "CLAUDE_KEY"
            read_api_base "CLAUDE_BASE" "https://api.anthropic.com/v1"
            ;;
        7)
            read_model_config "Gemini" "gemini-3.1-pro-preview" "GEMINI_KEY"
            read_api_base "GEMINI_BASE" "https://generativelanguage.googleapis.com"
            ;;
        8)
            read_model_config "OpenAI GPT" "gpt-5.4" "OPENAI_KEY"
            read_api_base "OPENAI_BASE" "https://api.openai.com/v1"
            ;;
        9)
            read_model_config "LinkAI" "MiniMax-M2.7" "LINKAI_KEY"
            USE_LINKAI="true"
            ;;
    esac
}

# Select channel
select_channel() {
    echo ""
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo -e "${CYAN}${BOLD}   Select Communication Channel${NC}"
    echo -e "${CYAN}${BOLD}=========================================${NC}"
    echo -e "${YELLOW}1) Weixin (微信)${NC}"
    echo -e "${YELLOW}2) Feishu (飞书)${NC}"
    echo -e "${YELLOW}3) DingTalk (钉钉)${NC}"
    echo -e "${YELLOW}4) WeCom Bot (企微智能机器人)${NC}"
    echo -e "${YELLOW}5) QQ (QQ 机器人)${NC}"
    echo -e "${YELLOW}6) WeCom App (企微自建应用)${NC}"
    echo -e "${YELLOW}7) Web (网页)${NC}"
    echo ""
    while true; do
        read -p "Enter your choice [press Enter for default: 1 - Weixin]: " channel_choice
        channel_choice=${channel_choice:-1}
        case "$channel_choice" in
            1|2|3|4|5|6|7) break ;;
            *) echo -e "${RED}Invalid choice. Please enter 1-7.${NC}" ;;
        esac
    done
}

configure_channel() {
    case "$channel_choice" in
        1)
            CHANNEL_TYPE="weixin"
            ACCESS_INFO="Weixin channel configured. Scan QR code in terminal or web console to login."
            ;;
        2)
            CHANNEL_TYPE="feishu"
            echo -e "${GREEN}Configure Feishu (WebSocket mode)...${NC}"
            read -p "Enter Feishu App ID: " fs_app_id
            read -p "Enter Feishu App Secret: " fs_app_secret
            FEISHU_APP_ID="$fs_app_id"
            FEISHU_APP_SECRET="$fs_app_secret"
            ACCESS_INFO="Feishu channel configured (WebSocket mode)"
            ;;
        3)
            CHANNEL_TYPE="dingtalk"
            echo -e "${GREEN}Configure DingTalk...${NC}"
            read -p "Enter DingTalk Client ID: " dt_client_id
            read -p "Enter DingTalk Client Secret: " dt_client_secret
            DT_CLIENT_ID="$dt_client_id"
            DT_CLIENT_SECRET="$dt_client_secret"
            ACCESS_INFO="DingTalk channel configured"
            ;;
        4)
            CHANNEL_TYPE="wecom_bot"
            echo -e "${GREEN}Configure WeCom Bot...${NC}"
            read -p "Enter WeCom Bot ID: " wecom_bot_id
            read -p "Enter WeCom Bot Secret: " wecom_bot_secret
            WECOM_BOT_ID="$wecom_bot_id"
            WECOM_BOT_SECRET="$wecom_bot_secret"
            ACCESS_INFO="WeCom Bot channel configured"
            ;;
        5)
            CHANNEL_TYPE="qq"
            echo -e "${GREEN}Configure QQ Bot...${NC}"
            read -p "Enter QQ App ID: " qq_app_id
            read -p "Enter QQ App Secret: " qq_app_secret
            QQ_APP_ID="$qq_app_id"
            QQ_APP_SECRET="$qq_app_secret"
            ACCESS_INFO="QQ Bot channel configured"
            ;;
        6)
            CHANNEL_TYPE="wechatcom_app"
            echo -e "${GREEN}Configure WeCom App...${NC}"
            read -p "Enter WeChat Corp ID: " corp_id
            read -p "Enter WeChat Com App Token: " com_token
            read -p "Enter WeChat Com App Secret: " com_secret
            read -p "Enter WeChat Com App Agent ID: " com_agent_id
            read -p "Enter WeChat Com App AES Key: " com_aes_key
            read -p "Enter WeChat Com App Port [press Enter for default: 9898]: " com_port
            com_port=${com_port:-9898}
            WECHATCOM_CORP_ID="$corp_id"
            WECHATCOM_TOKEN="$com_token"
            WECHATCOM_SECRET="$com_secret"
            WECHATCOM_AGENT_ID="$com_agent_id"
            WECHATCOM_AES_KEY="$com_aes_key"
            WECHATCOM_PORT="$com_port"
            ACCESS_INFO="WeCom App channel configured on port ${com_port}"
            ;;
        7)
            CHANNEL_TYPE="web"
            read -p "Enter web port [press Enter for default: 9899]: " web_port
            web_port=${web_port:-9899}
            WEB_PORT="$web_port"
            ACCESS_INFO="Web interface will be available at: http://localhost:${web_port}/chat"
            ;;
    esac
}

create_config_file() {
    echo -e "${GREEN}📝 Generating config.json...${NC}"
    CHANNEL_TYPE="$CHANNEL_TYPE" \
    MODEL_NAME="$MODEL_NAME" \
    OPENAI_KEY="${OPENAI_KEY:-}" \
    OPENAI_BASE="${OPENAI_BASE:-https://api.openai.com/v1}" \
    CLAUDE_KEY="${CLAUDE_KEY:-}" \
    CLAUDE_BASE="${CLAUDE_BASE:-https://api.anthropic.com/v1}" \
    GEMINI_KEY="${GEMINI_KEY:-}" \
    GEMINI_BASE="${GEMINI_BASE:-https://generativelanguage.googleapis.com}" \
    ZHIPU_KEY="${ZHIPU_KEY:-}" \
    MOONSHOT_KEY="${MOONSHOT_KEY:-}" \
    ARK_KEY="${ARK_KEY:-}" \
    DASHSCOPE_KEY="${DASHSCOPE_KEY:-}" \
    MINIMAX_KEY="${MINIMAX_KEY:-}" \
    USE_LINKAI="${USE_LINKAI:-false}" \
    LINKAI_KEY="${LINKAI_KEY:-}" \
    FEISHU_APP_ID="${FEISHU_APP_ID:-}" \
    FEISHU_APP_SECRET="${FEISHU_APP_SECRET:-}" \
    WEB_PORT="${WEB_PORT:-}" \
    DT_CLIENT_ID="${DT_CLIENT_ID:-}" \
    DT_CLIENT_SECRET="${DT_CLIENT_SECRET:-}" \
    WECOM_BOT_ID="${WECOM_BOT_ID:-}" \
    WECOM_BOT_SECRET="${WECOM_BOT_SECRET:-}" \
    QQ_APP_ID="${QQ_APP_ID:-}" \
    QQ_APP_SECRET="${QQ_APP_SECRET:-}" \
    WECHATCOM_CORP_ID="${WECHATCOM_CORP_ID:-}" \
    WECHATCOM_TOKEN="${WECHATCOM_TOKEN:-}" \
    WECHATCOM_SECRET="${WECHATCOM_SECRET:-}" \
    WECHATCOM_AGENT_ID="${WECHATCOM_AGENT_ID:-}" \
    WECHATCOM_AES_KEY="${WECHATCOM_AES_KEY:-}" \
    WECHATCOM_PORT="${WECHATCOM_PORT:-}" \
    $PYTHON_CMD -c "
import json, os
e = os.environ.get
base = {
    'channel_type': e('CHANNEL_TYPE'),
    'model': e('MODEL_NAME'),
    'open_ai_api_key': e('OPENAI_KEY', ''),
    'open_ai_api_base': e('OPENAI_BASE'),
    'claude_api_key': e('CLAUDE_KEY', ''),
    'claude_api_base': e('CLAUDE_BASE'),
    'gemini_api_key': e('GEMINI_KEY', ''),
    'gemini_api_base': e('GEMINI_BASE'),
    'zhipu_ai_api_key': e('ZHIPU_KEY', ''),
    'moonshot_api_key': e('MOONSHOT_KEY', ''),
    'ark_api_key': e('ARK_KEY', ''),
    'dashscope_api_key': e('DASHSCOPE_KEY', ''),
    'minimax_api_key': e('MINIMAX_KEY', ''),
    'voice_to_text': 'openai',
    'text_to_voice': 'openai',
    'voice_reply_voice': False,
    'speech_recognition': True,
    'group_speech_recognition': False,
    'use_linkai': e('USE_LINKAI') == 'true',
    'linkai_api_key': e('LINKAI_KEY', ''),
    'linkai_app_code': '',
    'agent': True,
    'agent_max_context_tokens': 40000,
    'agent_max_context_turns': 30,
    'agent_max_steps': 15,
}
channel_map = {
    'feishu': {'feishu_app_id': 'FEISHU_APP_ID', 'feishu_app_secret': 'FEISHU_APP_SECRET'},
    'web': {'web_port': ('WEB_PORT', int)},
    'dingtalk': {'dingtalk_client_id': 'DT_CLIENT_ID', 'dingtalk_client_secret': 'DT_CLIENT_SECRET'},
    'wecom_bot': {'wecom_bot_id': 'WECOM_BOT_ID', 'wecom_bot_secret': 'WECOM_BOT_SECRET'},
    'qq': {'qq_app_id': 'QQ_APP_ID', 'qq_app_secret': 'QQ_APP_SECRET'},
    'wechatcom_app': {'wechatcom_corp_id': 'WECHATCOM_CORP_ID', 'wechatcomapp_token': 'WECHATCOM_TOKEN', 'wechatcomapp_secret': 'WECHATCOM_SECRET', 'wechatcomapp_agent_id': 'WECHATCOM_AGENT_ID', 'wechatcomapp_aes_key': 'WECHATCOM_AES_KEY', 'wechatcomapp_port': ('WECHATCOM_PORT', int)},
}
ch = e('CHANNEL_TYPE')
for key, spec in channel_map.get(ch, {}).items():
    if isinstance(spec, tuple):
        env_name, conv = spec
        base[key] = conv(e(env_name))
    else:
        base[key] = e(spec, '')
with open('config.json', 'w') as f:
    json.dump(base, f, indent=2, ensure_ascii=False)
"
    echo -e "${GREEN}✅ Configuration file created successfully.${NC}"
}

# Main
echo -e "${CYAN}${BOLD}=========================================${NC}"
echo -e "${CYAN}${BOLD}   ${EMOJI_COW} CowAgent Installation${NC}"
echo -e "${CYAN}${BOLD}=========================================${NC}"
echo ""

if [ -f "${BASE_DIR}/config.json" ]; then
    echo -e "${GREEN}✅ Project already configured${NC}"
    read -p "Reconfigure? [y/N]: " redo
    if [[ ! $redo == [Yy]* ]]; then
        exit 0
    fi
    backup_file="${BASE_DIR}/config.json.backup.$(date +%s)"
    cp "${BASE_DIR}/config.json" "${backup_file}"
    echo -e "${GREEN}✅ Backed up config to: ${backup_file}${NC}"
fi

check_python_version
install_dependencies
select_model
configure_model
select_channel
configure_channel
create_config_file

echo ""
read -p "Start CowAgent now? [Y/n]: " start_now
if [[ ! $start_now == [Nn]* ]]; then
    "$SCRIPT_DIR/start.sh"
else
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo -e "${YELLOW}Run './scripts/start.sh' to start.${NC}"
fi
