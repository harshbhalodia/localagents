"""Blueprint discovery: a local installed-blueprints directory today, with an interface shaped
so a hosted marketplace registry API can be swapped in later without changing callers — see
docs/architecture/blueprint-marketplace.md.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from localagents.blueprints.manifest import BlueprintManifest, load_manifest


@dataclass
class RegistryEntry:
    manifest: BlueprintManifest
    path: Path


class LocalRegistry:
    """Discovers blueprints installed under a local directory (one subfolder per blueprint,
    each containing a `blueprint.yaml`). This is what LocalAgents actually reads from at run
    time — a hosted marketplace only needs to get files into this directory (download +
    extract into `blueprints_dir`); it never needs its own runtime protocol."""

    def __init__(self, blueprints_dir: str | Path = "./blueprints") -> None:
        self.blueprints_dir = Path(blueprints_dir)

    def list(self) -> list[RegistryEntry]:
        if not self.blueprints_dir.exists():
            return []
        entries = []
        for child in sorted(self.blueprints_dir.iterdir()):
            manifest_file = child / "blueprint.yaml"
            if child.is_dir() and manifest_file.exists():
                entries.append(RegistryEntry(manifest=load_manifest(manifest_file), path=child))
        return entries

    def get(self, blueprint_id: str) -> RegistryEntry:
        for entry in self.list():
            if entry.manifest.id == blueprint_id:
                return entry
        raise KeyError(f"Blueprint {blueprint_id!r} is not installed under {self.blueprints_dir}")


@dataclass
class MarketplaceIndexEntry:
    """One row of a marketplace catalog listing — what a "browse blueprints" UI shows,
    independent of whether it's installed locally yet."""

    id: str
    name: str
    version: str
    publisher: str
    tier: str
    price_usd: float | None
    category: str
    summary: str
    download_url: str


def load_catalog(catalog_path: str | Path) -> list[MarketplaceIndexEntry]:
    """Reads a marketplace catalog JSON file: `{"blueprints": [...]}` (or a bare list). Today
    this is a local file (e.g. bundled with the app or fetched once ahead of time); tomorrow
    it's the response body of a hosted registry's `GET /catalog` — same shape either way."""
    raw = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    items = raw.get("blueprints", raw) if isinstance(raw, dict) else raw
    return [MarketplaceIndexEntry(**item) for item in items]
