from __future__ import annotations

import pytest

from localagents.blueprints.loader import load_blueprint
from localagents.blueprints.registry import LocalRegistry, load_catalog


def _write_blueprint(base_dir, blueprint_id, tier="free", price_usd=None):
    package_dir = base_dir / blueprint_id
    package_dir.mkdir(parents=True)
    price_line = f"price_usd: {price_usd}\n" if price_usd is not None else ""
    (package_dir / "blueprint.yaml").write_text(
        f"id: {blueprint_id}\nname: {blueprint_id}\nversion: 0.1.0\npublisher: Demo Co\n"
        f"entry: agent:run\ntier: {tier}\n{price_line}",
        encoding="utf-8",
    )
    (package_dir / "agent.py").write_text(
        "def run(harness, **kwargs):\n    return 'ran ' + str(kwargs)\n", encoding="utf-8"
    )
    return package_dir


def test_load_blueprint_and_run_free(tmp_path):
    package_dir = _write_blueprint(tmp_path, "demo.free")
    blueprint = load_blueprint(package_dir)
    assert blueprint.manifest.id == "demo.free"
    assert blueprint.run(harness=None, snapshot={"a": 1}) == "ran {'snapshot': {'a': 1}}"


def test_run_paid_blueprint_without_license_raises(tmp_path):
    package_dir = _write_blueprint(tmp_path, "demo.paid", tier="paid", price_usd=4.99)
    blueprint = load_blueprint(package_dir)
    with pytest.raises(Exception, match="paid blueprint"):
        blueprint.run(harness=None)


def test_local_registry_list_and_get(tmp_path):
    _write_blueprint(tmp_path, "demo.one")
    _write_blueprint(tmp_path, "demo.two", tier="paid", price_usd=9.99)
    registry = LocalRegistry(tmp_path)

    entries = registry.list()
    assert {entry.manifest.id for entry in entries} == {"demo.one", "demo.two"}
    assert registry.get("demo.one").manifest.tier == "free"
    assert registry.get("demo.two").manifest.tier == "paid"


def test_local_registry_get_missing_raises(tmp_path):
    registry = LocalRegistry(tmp_path)
    with pytest.raises(KeyError):
        registry.get("does.not.exist")


def test_local_registry_missing_dir_returns_empty(tmp_path):
    registry = LocalRegistry(tmp_path / "nonexistent")
    assert registry.list() == []


def test_load_catalog_from_json_object(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(
        '{"blueprints": [{"id": "demo", "name": "Demo", "version": "0.1.0", "publisher": "Demo Co", '
        '"tier": "free", "price_usd": null, "category": "stress_test", "summary": "s", '
        '"download_url": "https://example.invalid/demo.zip"}]}',
        encoding="utf-8",
    )
    entries = load_catalog(catalog_file)
    assert len(entries) == 1
    assert entries[0].id == "demo"
    assert entries[0].tier == "free"
