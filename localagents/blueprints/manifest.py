"""Blueprint manifest: the declarative package format loaded from a blueprint's `blueprint.yaml`.

A manifest is the only thing the marketplace catalog needs to display (name, publisher, tier,
price) and the only thing the loader needs to find and run a blueprint's entry point.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

VALID_TIERS = ("free", "paid")


@dataclass
class BlueprintManifest:
    id: str
    name: str
    version: str
    publisher: str
    entry: str
    tier: str = "free"
    price_usd: float | None = None
    category: str = "general"
    summary: str = ""
    requires: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    homepage: str | None = None

    def __post_init__(self) -> None:
        if self.tier not in VALID_TIERS:
            raise ValueError(f"Unknown tier {self.tier!r} for blueprint {self.id!r}, expected one of {VALID_TIERS}")
        if self.tier == "paid" and (self.price_usd is None or self.price_usd <= 0):
            raise ValueError(f"Paid blueprint {self.id!r} must set a positive price_usd")
        if ":" not in self.entry:
            raise ValueError(f"Blueprint {self.id!r} entry must be 'module:function', got {self.entry!r}")


def load_manifest(path: str | Path) -> BlueprintManifest:
    """Reads and validates a `blueprint.yaml` file. `path` may point at the file itself or at
    the blueprint's package directory (in which case `blueprint.yaml` inside it is used)."""
    manifest_path = Path(path)
    if manifest_path.is_dir():
        manifest_path = manifest_path / "blueprint.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No blueprint manifest found at {manifest_path}")

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    missing = [key for key in ("id", "name", "version", "publisher", "entry") if key not in raw]
    if missing:
        raise ValueError(f"{manifest_path} is missing required field(s): {missing}")

    return BlueprintManifest(
        id=raw["id"],
        name=raw["name"],
        version=raw["version"],
        publisher=raw["publisher"],
        entry=raw["entry"],
        tier=raw.get("tier", "free"),
        price_usd=raw.get("price_usd"),
        category=raw.get("category", "general"),
        summary=raw.get("summary", ""),
        requires=raw.get("requires") or {},
        inputs=raw.get("inputs") or [],
        tags=raw.get("tags") or [],
        homepage=raw.get("homepage"),
    )
