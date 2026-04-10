# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CowAgent** is a super AI agent framework that can connect to multiple messaging platforms (WeChat, Feishu, DingTalk, WeCom, QQ, Web, Terminal). It provides an Agent mode with task planning, long-term memory, skills system, and tool calling, as well as a simpler chat mode.

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `app.py` | Main entry point - starts the ChannelManager which launches channels |
| `config.py` | All configuration definitions, loads `config.json` |
| `channel/` | Messaging channel implementations (weixin, feishu, dingtalk, qq, web, terminal, etc.) |
| `models/` | LLM bot implementations (OpenAI, Claude, Gemini, Qwen, GLM, DeepSeek, etc.) |
| `bridge/` | Glue between channels and models - `Bridge` routes requests, `AgentBridge` handles Agent mode |
| `agent/` | Agent system: task planning, memory, skills, tools, protocol definitions |
| `plugins/` | Plugin system (hello, keyword, dungeon, role, etc.) |
| `cli/` | Cow CLI command-line interface |
| `voice/` | Voice/speech recognition and synthesis |
| `translate/` | Translation services |
| `common/` | Shared utilities (logging, singleton, config, memory) |

## Architecture

```
app.py → ChannelManager → Channel(s) → ChatChannel → Bridge/AgentBridge → Model Bot
                                                    ↕ plugins
```

- **Channel Layer** (`channel/`): Each channel (weixin, feishu, etc.) extends `Channel`/`ChatChannel`, handles platform-specific message send/receive
- **Bridge Layer** (`bridge/`): `Bridge` routes to the right bot based on config; `AgentBridge` integrates the Agent system for multi-step reasoning
- **Model Layer** (`models/`): Factory pattern via `create_bot()` - each LLM has its own bot class implementing the `reply()` interface
- **Agent System** (`agent/`): `agent/chat/` for chat service, `agent/memory/` for long-term memory, `agent/skills/` for skill engine, `agent/tools/` for built-in tools (bash, read, write, edit, browser, web_search, etc.), `agent/protocol/` for message/task types
- **Plugin System** (`plugins/`): Event-driven plugins with priority system, loaded by `PluginManager`

## Development Commands

### Run
```bash
python3 app.py           # Standard run
python3 app.py --cmd     # Terminal/CLI mode
cow start                # Via Cow CLI (requires pip install -e .)
```

### Install Dependencies
```bash
pip3 install -r requirements.txt           # Core dependencies
pip3 install -r requirements-optional.txt  # Optional dependencies
pip3 install -e .                          # Install Cow CLI
```

### Docker
```bash
sudo docker compose up -d    # Start container
sudo docker logs -f chatgpt-on-wechat   # View logs
```

## Configuration

- Config lives in `config.json` (copy from `config-template.json`)
- All available config keys are defined in `config.py` under `available_setting`
- Key configs: `channel_type`, `model`, `*_api_key`, `agent` (enable Agent mode), `agent_workspace`

## Adding a New Channel

1. Create a new directory under `channel/your_channel/`
2. Implement a channel class extending `ChatChannel` with `startup()`, `handle_msg()`, `send()` methods
3. Register in `channel/channel_factory.py`
4. See `channel/feishu/feishu_channel.py` as reference implementation

## Adding a New Model

1. Create bot class in `models/` implementing `reply(query, context)` method
2. Register in `models/bot_factory.py`
3. Add model type constant in `common/const.py`
4. Add routing logic in `bridge/bridge.py`

## Adding a New Agent Tool

1. Create tool class in `agent/tools/` extending `BaseTool`
2. Register in `agent/tools/tool_manager.py`

## Important Patterns

- **Singleton pattern**: `@singleton` decorator from `common/singleton.py` is used extensively (Bridge, PluginManager, etc.)
- **Context passing**: Messages flow as `Context` objects through the system, carrying metadata
- **Reply types**: `Reply` objects with `ReplyType` enum define response formats
- **Multi-channel**: Multiple channels can run simultaneously via `ChannelManager`
- **Thread model**: Each channel runs in its own daemon thread; message processing uses a `ThreadPoolExecutor`
