"""Integration tests for CowAgent.

These tests verify that the overall system works correctly, including:
- Module imports across all packages
- Entry point loading
- Configuration loading
- Cross-module integration
"""

import os
import sys


class TestModuleImports:
    """Verify all core modules can be imported without errors."""

    def test_import_config(self):
        from cowagent.config import conf, load_config

    def test_import_common_log(self):
        from cowagent.common.log import logger

    def test_import_common_const(self):
        from cowagent.common import const

    def test_import_singleton(self):
        from cowagent.common.singleton import singleton

    def test_import_expired_dict(self):
        from cowagent.common.expired_dict import ExpiredDict

    def test_import_sorted_dict(self):
        from cowagent.common.sorted_dict import SortedDict

    def test_import_dequeue(self):
        from cowagent.common.dequeue import Dequeue

    def test_import_utils(self):
        from cowagent.common.utils import (
            fsize,
            split_string_by_utf8_length,
            get_path_suffix,
            remove_markdown_symbol,
            expand_path,
        )

    def test_import_reply(self):
        from cowagent.bridge.reply import Reply, ReplyType

    def test_import_context(self):
        from cowagent.bridge.context import Context, ContextType

    def test_import_channel_factory(self):
        from cowagent.channel import channel_factory

    def test_import_bot_factory(self):
        from cowagent.models.bot_factory import create_bot

    def test_import_bridge(self):
        from cowagent.bridge.bridge import Bridge

    def test_import_agent_bridge(self):
        from cowagent.bridge.agent_bridge import AgentBridge

    def test_import_tool_manager(self):
        from cowagent.agent.tools.tool_manager import ToolManager

    def test_import_base_tool(self):
        from cowagent.agent.tools.base_tool import BaseTool

    def test_import_plugin_manager(self):
        from cowagent.plugins.plugin_manager import PluginManager

    def test_import_voice_factory(self):
        from cowagent.voice.factory import create_voice

    def test_import_translate_factory(self):
        from cowagent.translate.factory import create_translator

    def test_import_cli(self):
        from cowagent.cli.cli import main

    def test_import_protocol(self):
        from cowagent.agent.protocol.models import LLMRequest, LLMModel
        from cowagent.agent.protocol.task import Task, TaskType, TaskStatus
        from cowagent.agent.protocol.result import AgentResult, AgentActionType


class TestConfigLoading:
    """Test configuration loading end-to-end."""

    def test_load_config_from_template(self):
        """Config should load from template if config.json doesn't exist."""
        from cowagent.config import load_config, conf

        # This should not raise
        load_config()
        cfg = conf()
        assert cfg is not None

    def test_config_has_channel_type(self):
        from cowagent.config import conf

        cfg = conf()
        assert "channel_type" in cfg


class TestProjectStructure:
    """Verify the project directory structure is correct."""

    def test_cowagent_package_exists(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assert os.path.isdir(os.path.join(root, "cowagent"))

    def test_scripts_dir_exists(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assert os.path.isdir(os.path.join(root, "scripts"))

    def test_skills_dir_exists(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assert os.path.isdir(os.path.join(root, "skills"))

    def test_bridge_dir_exists(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assert os.path.isdir(os.path.join(root, "bridge"))

    def test_logs_dir_exists(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assert os.path.isdir(os.path.join(root, "logs"))

    def test_main_entry_point(self):
        """Verify __main__.py exists and is importable."""
        root = os.path.dirname(os.path.dirname(__file__))
        main_py = os.path.join(root, "cowagent", "__main__.py")
        assert os.path.exists(main_py), "cowagent/__main__.py should exist"
