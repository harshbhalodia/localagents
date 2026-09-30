"""Advisor packs: the declarative bundles Loonie (and future apps) load to gain a new stress test,
plan or decision aid. Build one here, validate it, and publish it to an app with one command.

A pack is plain YAML. It never contains code, so an app can load it safely.
"""
from localagents.advisors.pack import (
    KINDS,
    LOONIE_SCOPES,
    AdvisorPack,
    PackReport,
    load_pack,
    render_template,
    validate_pack,
)
from localagents.advisors.targets import default_loonie_dir, list_published, publish_to_dir

__all__ = [
    "KINDS",
    "LOONIE_SCOPES",
    "AdvisorPack",
    "PackReport",
    "default_loonie_dir",
    "list_published",
    "load_pack",
    "publish_to_dir",
    "render_template",
    "validate_pack",
]
