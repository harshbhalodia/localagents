"""`localagents` command-line interface — scaffold, validate, list, and run blueprints.

    localagents blueprint init <dir> [--id ID] [--publisher NAME]
    localagents blueprint validate <dir>
    localagents blueprint list [--dir DIR]
    localagents blueprint run <dir> [--config config.yaml] [--license TOKEN] [--license-secret SECRET]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from localagents.blueprints.loader import load_blueprint
from localagents.blueprints.manifest import load_manifest
from localagents.blueprints.registry import LocalRegistry
from localagents.harness import Harness

_TEMPLATE_MANIFEST = """\
id: {id}
name: {name}
version: 0.1.0
publisher: {publisher}
tier: free
category: stress_test
summary: Describe what this blueprint stress-tests and for whom.
entry: agent:run
inputs: []
tags: []
"""

_TEMPLATE_AGENT = '''"""Blueprint entry point — the loader calls `run(harness, **kwargs)`."""
from localagents.agents import register


@register("{id}")
def run(harness, snapshot=None, **kwargs):
    agent = harness.build_agent(
        system_prompt="You are a financial stress-test advisor. Only reason from the figures "
        "you are given — never invent numbers."
    )
    result = agent(f"Review this data and summarize risks and resilience:\\n{{snapshot}}")
    return str(result)
'''


def _cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.directory)
    target.mkdir(parents=True, exist_ok=True)
    blueprint_id = args.id or target.name
    (target / "blueprint.yaml").write_text(
        _TEMPLATE_MANIFEST.format(id=blueprint_id, name=blueprint_id, publisher=args.publisher),
        encoding="utf-8",
    )
    (target / "agent.py").write_text(_TEMPLATE_AGENT.format(id=blueprint_id), encoding="utf-8")
    print(f"Scaffolded blueprint {blueprint_id!r} at {target}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        manifest = load_manifest(args.directory)
    except Exception as exc:  # noqa: BLE001 - CLI boundary: report any failure to the user
        print(f"Invalid blueprint: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {manifest.id} v{manifest.version} ({manifest.tier}) by {manifest.publisher}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    registry = LocalRegistry(args.dir)
    entries = registry.list()
    if not entries:
        print(f"No blueprints installed under {registry.blueprints_dir}")
        return 0
    for entry in entries:
        manifest = entry.manifest
        price = f"${manifest.price_usd}" if manifest.tier == "paid" else "free"
        print(f"{manifest.id:30} v{manifest.version:10} {price:8} {manifest.publisher} — {manifest.summary}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    blueprint = load_blueprint(args.directory)
    harness = Harness.from_file(args.config)
    result = blueprint.run(harness, license_token=args.license, license_secret=args.license_secret)
    print(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="localagents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    blueprint_parser = subparsers.add_parser("blueprint", help="Manage blueprints")
    blueprint_sub = blueprint_parser.add_subparsers(dest="blueprint_command", required=True)

    init_parser = blueprint_sub.add_parser("init", help="Scaffold a new blueprint package")
    init_parser.add_argument("directory")
    init_parser.add_argument("--id", default=None)
    init_parser.add_argument("--publisher", default="you")
    init_parser.set_defaults(func=_cmd_init)

    validate_parser = blueprint_sub.add_parser("validate", help="Validate a blueprint manifest")
    validate_parser.add_argument("directory")
    validate_parser.set_defaults(func=_cmd_validate)

    list_parser = blueprint_sub.add_parser("list", help="List installed blueprints")
    list_parser.add_argument("--dir", dest="dir", default="./blueprints")
    list_parser.set_defaults(func=_cmd_list)

    run_parser = blueprint_sub.add_parser("run", help="Run a blueprint's entry point")
    run_parser.add_argument("directory")
    run_parser.add_argument("--config", default=None)
    run_parser.add_argument("--license", default=None)
    run_parser.add_argument("--license-secret", dest="license_secret", default=None)
    run_parser.set_defaults(func=_cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
