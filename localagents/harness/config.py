"""Loads LocalAgents harness configuration from a YAML file, falling back to local-first
defaults (Ollama on localhost) if no file is given or found — no cloud account required to
get started."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ModelConfig:
    provider: str = "ollama"
    model_id: str = "llama3"
    host: str = "http://localhost:11434"
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessConfig:
    name: str = "localagents"
    model: ModelConfig = field(default_factory=ModelConfig)
    load_tools_from_directory: bool = False
    sessions_dir: str = "./data/sessions"


def load_config(path: str | Path | None = None) -> HarnessConfig:
    """Reads a YAML config file if it exists; returns local-only defaults otherwise."""
    if path is None:
        return HarnessConfig()

    config_path = Path(path)
    if not config_path.exists():
        return HarnessConfig()

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    model_raw = raw.get("model", {})
    return HarnessConfig(
        name=raw.get("name", "localagents"),
        model=ModelConfig(
            provider=model_raw.get("provider", "ollama"),
            model_id=model_raw.get("model_id", "llama3"),
            host=model_raw.get("host", "http://localhost:11434"),
            params=model_raw.get("params") or {},
        ),
        load_tools_from_directory=bool(raw.get("load_tools_from_directory", False)),
        sessions_dir=raw.get("sessions_dir", "./data/sessions"),
    )
