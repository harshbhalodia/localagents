"""LocalAgents Harness — an open agent harness for building, running, and composing AI agents.

Thin, local-first glue on top of the Strands Agents SDK: YAML-driven model/session config,
an agent-preset registry, and re-exports of the pieces most callers need day to day.
"""
from __future__ import annotations

from localagents.harness.config import HarnessConfig, ModelConfig, load_config
from localagents.harness.core import Harness
from localagents.tools import tool

__version__ = "0.1.0"

__all__ = ["Harness", "HarnessConfig", "ModelConfig", "__version__", "load_config", "tool"]
