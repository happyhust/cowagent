# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CowAgent** is a super AI agent framework that can connect to multiple messaging platforms (WeChat, Feishu, DingTalk, WeCom, QQ, Web, Terminal). It provides an Agent mode with task planning, long-term memory, skills system, and tool calling, as well as a simpler chat mode.

- **Python version**: >= 3.11 (managed via `uv` with Python 3.12 in `.python/`)
- **Dependency management**: `uv` (preferred) or `pip` via `pyproject.toml`. No `requirements.txt` exists.

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `cowagent/__main__.py` | Main entry point - starts the ChannelManager which launches channels |
| `cowagent/config.py` | All configuration definitions, loads `config.json` |
| `cowagent/channel/` | Messaging channel implementations (weixin, feishu, dingtalk, qq, web, terminal, etc.) |
| `cowagent/models/` | LLM bot implementations (OpenAI, Claude, Gemini, Qwen, GLM, DeepSeek, etc.) |
| `cowagent/bridge/` | Glue between channels and models - `Bridge` routes requests, `AgentBridge` handles Agent mode |
| `cowagent/agent/` | Agent system: task planning, memory, skills, tools, protocol definitions |
| `cowagent/plugins/` | Plugin system (hello, keyword, dungeon, role, etc.) |
| `cowagent/cli/` | Cow CLI command-line interface |
| `cowagent/voice/` | Voice/speech recognition and synthesis |
| `cowagent/translate/` | Translation services |
| `cowagent/common/` | Shared utilities (logging, singleton, config, memory) |
| `bridge/` | Frontend UI files (web chat interface) |
| `scripts/` | Shell/PowerShell scripts for service management |

## Architecture

```
python -m cowagent → ChannelManager → Channel(s) → ChatChannel → Bridge/AgentBridge → Model Bot
                                                    ↕ plugins
```

- **Channel Layer** (`channel/`): Each channel (weixin, feishu, etc.) extends `Channel`/`ChatChannel`, handles platform-specific message send/receive
- **Bridge Layer** (`bridge/`): `Bridge` routes to the right bot based on config; `AgentBridge` integrates the Agent system for multi-step reasoning
- **Model Layer** (`models/`): Factory pattern via `create_bot()` - each LLM has its own bot class implementing the `reply()` interface
- **Agent System** (`agent/`): `agent/chat/` for chat service, `agent/memory/` for long-term memory, `agent/skills/` for skill engine, `agent/tools/` for built-in tools (bash, browser, edit, ls, memory, read, scheduler, send, vision, web_fetch, web_search, write), `agent/protocol/` for message/task types
- **Plugin System** (`plugins/`): Event-driven plugins with priority system, loaded by `PluginManager`

## Development Commands

### Run
```bash
python3 -m cowagent           # Standard run
python3 -m cowagent --cmd     # Terminal/CLI mode
cow start                     # Via Cow CLI (requires pip install -e .)
make start                    # Via Makefile (background daemon)
make status                   # Check daemon status
make stop                     # Stop daemon
```

### Install Dependencies
```bash
make init                     # Sync deps with uv (Python 3.12, recommended)
uv sync --all-extras --dev    # uv directly, with all optional deps
pip3 install -e ".[all]"      # pip install with all optional deps
pip3 install -e .             # Core deps only
```

### Lint & Format
```bash
make lint                     # Ruff check + Prettier check for bridge/
make format                   # Ruff format + Prettier format
ruff check cowagent/          # Python lint only
ruff format cowagent/         # Python format only
```

### Test
```bash
make test                     # Run all unit + integration tests
pytest cowagent/tests/ -v     # CowAgent unit tests only
pytest bridge/tests/ -v       # Bridge frontend tests only
pytest tests/ -v              # Integration tests only
```

### Docker
```bash
sudo docker compose -f docker/docker-compose.yml up -d   # Start container
sudo docker logs -f chatgpt-on-wechat                     # View logs
```

## Configuration

- Config lives in `config.json` (copy from `config-template.json`)
- All available config keys are defined in `config.py` under `available_setting`
- Key configs:
  - `channel_type`: comma-separated channel names (weixin, feishu, dingtalk, wecom_bot, web, terminal)
  - `llm_provider`: model provider (openai, claude, gemini, qwen, minimax, etc.)
  - `llm_model`: model name (e.g. "MiniMax-M2.7")
  - `llm_api_key` / `llm_api_base`: API credentials
  - `agent`: enable Agent mode (true/false)
  - `agent_max_context_tokens`, `agent_max_context_turns`, `agent_max_steps`: Agent limits
  - `voice_to_text` / `text_to_voice`: speech engine selection

## Adding a New Channel

1. Create a new directory under `cowagent/channel/your_channel/`
2. Implement a channel class extending `ChatChannel` with `startup()`, `handle_msg()`, `send()` methods
3. Register in `cowagent/channel/channel_factory.py`
4. See `cowagent/channel/feishu/feishu_channel.py` as reference implementation

## Adding a New Model

1. Create bot class in `cowagent/models/` implementing `reply(query, context)` method
2. Register in `cowagent/models/bot_factory.py`
3. Add model type constant in `cowagent/common/const.py`
4. Add routing logic in `cowagent/bridge/bridge.py`

## Adding a New Agent Tool

1. Create tool class in `cowagent/agent/tools/` extending `BaseTool`
2. Register in `cowagent/agent/tools/tool_manager.py`

## Important Patterns

- **Singleton pattern**: `@singleton` decorator from `common/singleton.py` is used extensively (Bridge, PluginManager, etc.)
- **Context passing**: Messages flow as `Context` objects through the system, carrying metadata
- **Reply types**: `Reply` objects with `ReplyType` enum define response formats
- **Multi-channel**: Multiple channels can run simultaneously via `ChannelManager`
- **Thread model**: Each channel runs in its own daemon thread; message processing uses a `ThreadPoolExecutor`

## Testing

- Tests use `pytest`. There is a single integration test file at `tests/test_integration.py` that verifies module imports, config loading, and project structure.
- The `cowagent/tests/` and `bridge/tests/` directories are reserved for unit tests (currently empty).
- Run `make test` to execute all tests, or `pytest <path> -v --tb=short` for a specific directory.
