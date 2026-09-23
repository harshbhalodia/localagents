"""Registry of named, reusable agent presets (e.g. a system prompt + default tools), so
applications across the LocalAgents ecosystem can share agent definitions instead of
duplicating system-prompt strings.

Example:
    from localagents.agents import register, get

    @register("assistant")
    def build_assistant(harness):
        return harness.build_agent(system_prompt="You are a helpful assistant.")
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

_REGISTRY: dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that registers a factory function under `name`."""

    def decorator(factory: Callable[..., Any]) -> Callable[..., Any]:
        _REGISTRY[name] = factory
        return factory

    return decorator


def get(name: str) -> Callable[..., Any]:
    """Looks up a registered agent-preset factory by name."""
    if name not in _REGISTRY:
        raise KeyError(f"No agent preset registered under {name!r}. Known presets: {available()}")
    return _REGISTRY[name]


def available() -> list[str]:
    """Lists the names of all currently registered agent presets."""
    return sorted(_REGISTRY)
