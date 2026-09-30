"""`localagents` command-line interface — build advisors for apps, and scaffold, validate, list and run blueprints.

    localagents advisor init <file.yaml> [--id ID] [--name NAME] [--publisher NAME] [--kind KIND]
    localagents advisor validate <file.yaml>
    localagents advisor publish <file.yaml> [--to loonie | --dir DIR]
    localagents advisor list [--to loonie | --dir DIR]

    localagents blueprint init <dir> [--id ID] [--publisher NAME]
    localagents blueprint validate <dir>
    localagents blueprint list [--dir DIR]
    localagents blueprint run <dir> [--config config.yaml] [--license TOKEN] [--license-secret SECRET]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from localagents.advisors import (
    KINDS,
    default_loonie_dir,
    list_published,
    load_pack,
    publish_to_dir,
    render_template,
    validate_pack,
)
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


def _advisor_dir(args: argparse.Namespace) -> Path:
    return Path(args.dir) if args.dir else default_loonie_dir()


def _cmd_advisor_init(args: argparse.Namespace) -> int:
    target = Path(args.file)
    if target.exists() and not args.force:
        print(f"{target} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1
    stem = target.stem
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_template(
            id=args.id or f"{args.publisher.lower().replace(' ', '_')}.{stem}",
            name=args.name or stem.replace("_", " ").replace("-", " ").title(),
            publisher=args.publisher,
            kind=args.kind,
        ),
        encoding="utf-8",
    )
    print(f"Created {target}. Edit it, then run: localagents advisor validate {target}")
    return 0


def _cmd_advisor_validate(args: argparse.Namespace) -> int:
    import yaml

    try:
        raw = yaml.safe_load(Path(args.file).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"Could not read {args.file}: {exc}", file=sys.stderr)
        return 1
    report = validate_pack(raw)
    for problem in report.errors:
        print(f"error: {problem}", file=sys.stderr)
    for note in report.warnings:
        print(f"tip:   {note}")
    if not report.ok:
        return 1
    pack = load_pack(args.file)
    print(f"OK: {pack.name} v{pack.version} ({pack.kind}) with {len(pack.scenarios)} scenario(s)")
    return 0


def _cmd_advisor_publish(args: argparse.Namespace) -> int:
    destination = _advisor_dir(args)
    try:
        published = publish_to_dir(args.file, destination)
    except ValueError as exc:
        print(f"Not published: {exc}", file=sys.stderr)
        return 1
    print(f"Published to {published}")
    print("Loonie picks it up on its next request. Ask Pilot one of the pack's example questions to try it.")
    return 0


def _cmd_advisor_list(args: argparse.Namespace) -> int:
    destination = _advisor_dir(args)
    packs = list_published(destination)
    if not packs:
        print(f"No advisors published in {destination}")
        return 0
    for pack in packs:
        print(f"{pack.id:36} v{pack.version:8} {pack.kind:12} {pack.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="localagents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    advisor_parser = subparsers.add_parser("advisor", help="Build advisors and publish them to an app such as Loonie")
    advisor_sub = advisor_parser.add_subparsers(dest="advisor_command", required=True)

    a_init = advisor_sub.add_parser("init", help="Create a starter advisor pack")
    a_init.add_argument("file")
    a_init.add_argument("--id", default=None)
    a_init.add_argument("--name", default=None)
    a_init.add_argument("--publisher", default="you")
    a_init.add_argument("--kind", choices=KINDS, default="stress_test")
    a_init.add_argument("--force", action="store_true")
    a_init.set_defaults(func=_cmd_advisor_init)

    a_validate = advisor_sub.add_parser("validate", help="Check a pack and get tips to improve it")
    a_validate.add_argument("file")
    a_validate.set_defaults(func=_cmd_advisor_validate)

    a_publish = advisor_sub.add_parser("publish", help="Validate a pack and ship it to an app")
    a_publish.add_argument("file")
    a_publish.add_argument("--to", choices=["loonie"], default="loonie", help="Target app")
    a_publish.add_argument("--dir", default=None, help="Advisors folder to publish into (default: the installed Loonie app)")
    a_publish.set_defaults(func=_cmd_advisor_publish)

    a_list = advisor_sub.add_parser("list", help="List advisors already published to an app")
    a_list.add_argument("--to", choices=["loonie"], default="loonie")
    a_list.add_argument("--dir", default=None)
    a_list.set_defaults(func=_cmd_advisor_list)

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
