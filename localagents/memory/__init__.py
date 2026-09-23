"""Re-exports Strands' own memory subsystem.

LocalAgents doesn't ship a custom memory-store format — Strands already provides a mature
`MemoryManager` / `MemoryStore` protocol. Plug in any `MemoryStore` implementation (a built-in
Strands one, a community one, or your own) via `build_memory_manager`.
"""
from __future__ import annotations

from strands.memory.memory_manager import MemoryManager
from strands.memory.types import MemoryManagerConfig, MemoryStore

__all__ = ["MemoryManager", "MemoryManagerConfig", "MemoryStore", "build_memory_manager"]


def build_memory_manager(stores: list[MemoryStore], **kwargs: object) -> MemoryManager:
    """Thin convenience wrapper around `strands.memory.MemoryManager(stores=..., **kwargs)`."""
    return MemoryManager(stores=stores, **kwargs)
