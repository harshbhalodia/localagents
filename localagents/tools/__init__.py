"""Re-exports Strands' `@tool` decorator so agent authors can `from localagents import tool`
without needing to know it lives in Strands underneath."""
from __future__ import annotations

from strands import tool

__all__ = ["tool"]
