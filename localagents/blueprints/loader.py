"""Loads an installed blueprint package (manifest + entry-point callable) ready to run.

SECURITY: loading a blueprint executes its Python source in-process, with the caller's own
privileges — there is no sandboxing in this version. Only install blueprints from publishers
you trust. The marketplace roadmap (docs/architecture/blueprint-marketplace.md) adds publisher
signature verification and a restricted execution mode before this ships beyond local/dev use.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from localagents.blueprints.license import check_entitlement
from localagents.blueprints.manifest import BlueprintManifest, load_manifest


@dataclass
class Blueprint:
    manifest: BlueprintManifest
    package_dir: Path
    _entry: Callable[..., Any]

    def run(
        self,
        harness: Any,
        *,
        license_token: str | None = None,
        license_secret: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Checks entitlement (raises `EntitlementError` for an unpaid paid-tier blueprint),
        then calls the blueprint's entry point as `entry(harness, **kwargs)`."""
        check_entitlement(self.manifest, license_token, license_secret)
        return self._entry(harness, **kwargs)


def _import_entry(package_dir: Path, entry: str) -> Callable[..., Any]:
    module_name, func_name = entry.split(":", 1)
    module_file = package_dir / (module_name.replace(".", "/") + ".py")

    if module_file.exists():
        spec_name = f"localagents_blueprint_{package_dir.name}_{module_name.replace('.', '_')}"
        spec = importlib.util.spec_from_file_location(spec_name, module_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load blueprint module from {module_file}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec_name] = module
        spec.loader.exec_module(module)
    else:
        module = importlib.import_module(module_name)

    try:
        return getattr(module, func_name)
    except AttributeError as exc:
        raise ImportError(f"Blueprint entry {entry!r} has no attribute {func_name!r}") from exc


def load_blueprint(path: str | Path) -> Blueprint:
    """Loads a blueprint package directory (containing `blueprint.yaml` + its entry module)
    into a runnable `Blueprint`."""
    package_dir = Path(path)
    manifest = load_manifest(package_dir)
    entry = _import_entry(package_dir, manifest.entry)
    return Blueprint(manifest=manifest, package_dir=package_dir, _entry=entry)
