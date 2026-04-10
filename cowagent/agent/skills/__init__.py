"""
Skills module for agent system.

This module provides the framework for loading, managing, and executing skills.
Skills are markdown files with frontmatter that provide specialized instructions
for specific tasks.
"""

from cowagent.agent.skills.types import (
    Skill,
    SkillEntry,
    SkillMetadata,
    SkillInstallSpec,
    LoadSkillsResult,
)
from cowagent.agent.skills.loader import SkillLoader
from cowagent.agent.skills.manager import SkillManager
from cowagent.agent.skills.service import SkillService
from cowagent.agent.skills.formatter import format_skills_for_prompt

__all__ = [
    "Skill",
    "SkillEntry",
    "SkillMetadata",
    "SkillInstallSpec",
    "LoadSkillsResult",
    "SkillLoader",
    "SkillManager",
    "SkillService",
    "format_skills_for_prompt",
]
