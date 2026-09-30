"""Where published packs go. Loonie reads packs from an `advisors` folder in its data directory."""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from localagents.advisors.pack import AdvisorPack, load_pack

LOONIE_APP_ID = "com.loonie.app"


def default_loonie_dir() -> Path:
    """The installed Windows app's advisors folder (override with LOONIE_ADVISORS_DIR)."""
    override = os.environ.get("LOONIE_ADVISORS_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / LOONIE_APP_ID / "backend" / "data" / "advisors"


def _file_name(pack: AdvisorPack) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", pack.id) + ".yaml"


def publish_to_dir(pack_file: str | Path, destination: str | Path) -> Path:
    """Validates the pack and copies it into `destination`; returns the published file.

    Loonie notices the new file on its next request, so the advisor is available straight away.
    """
    pack = load_pack(pack_file)
    target_dir = Path(destination)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / _file_name(pack)
    shutil.copyfile(pack_file, target)
    return target


def list_published(directory: str | Path) -> list[AdvisorPack]:
    folder = Path(directory)
    if not folder.exists():
        return []
    packs = []
    for path in sorted([*folder.glob("*.yaml"), *folder.glob("*.yml")]):
        try:
            packs.append(load_pack(path))
        except ValueError:
            continue
    return packs
