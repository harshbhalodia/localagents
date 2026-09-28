"""Blueprints: versioned, distributable packages of agent logic (system prompts, scenario
assumptions, orchestration) that plug into a `Harness` at runtime.

A blueprint is the unit the marketplace lists, licenses, and installs — never raw model
weights or user data. See docs/architecture/blueprint-marketplace.md for the full design.
"""
from __future__ import annotations

from localagents.blueprints.license import EntitlementError, License, check_entitlement
from localagents.blueprints.loader import Blueprint, load_blueprint
from localagents.blueprints.manifest import BlueprintManifest, load_manifest
from localagents.blueprints.registry import LocalRegistry, MarketplaceIndexEntry, RegistryEntry, load_catalog

__all__ = [
    "Blueprint",
    "BlueprintManifest",
    "EntitlementError",
    "License",
    "LocalRegistry",
    "MarketplaceIndexEntry",
    "RegistryEntry",
    "check_entitlement",
    "load_blueprint",
    "load_catalog",
    "load_manifest",
]
