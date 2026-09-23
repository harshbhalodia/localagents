"""Builds a configured `strands.Agent` from LocalAgents config — the minimal glue LocalAgents
adds on top of the Strands Agents SDK (model selection, local-first session persistence)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from strands import Agent

from localagents.harness.config import HarnessConfig, load_config
from localagents.models.registry import build_model
from localagents.sessions.manager import build_session_manager


class Harness:
    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> Harness:
        return cls(load_config(path))

    def build_agent(self, session_id: str | None = None, **agent_kwargs: Any) -> Agent:
        """Constructs a `strands.Agent` wired to the configured model provider. Pass
        `session_id` to persist conversation state under `sessions_dir` between runs; omit it
        for a one-off, in-memory-only agent. Any extra kwarg is forwarded to `strands.Agent`
        (e.g. `tools=[...]`, `system_prompt=...`), overriding the harness defaults below."""
        agent_kwargs.setdefault("model", build_model(self.config.model))
        agent_kwargs.setdefault("load_tools_from_directory", self.config.load_tools_from_directory)
        if session_id and "session_manager" not in agent_kwargs:
            agent_kwargs["session_manager"] = build_session_manager(session_id, self.config.sessions_dir)

        return Agent(**agent_kwargs)
