from __future__ import annotations

import pytest

from localagents.blueprints.manifest import BlueprintManifest, load_manifest


def test_load_manifest_from_file(tmp_path):
    manifest_file = tmp_path / "blueprint.yaml"
    manifest_file.write_text(
        "id: demo.blueprint\nname: Demo\nversion: 0.1.0\npublisher: Demo Co\nentry: agent:run\n",
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_file)
    assert manifest.id == "demo.blueprint"
    assert manifest.tier == "free"
    assert manifest.price_usd is None


def test_load_manifest_from_directory(tmp_path):
    (tmp_path / "blueprint.yaml").write_text(
        "id: demo.blueprint\nname: Demo\nversion: 0.1.0\npublisher: Demo Co\nentry: agent:run\n",
        encoding="utf-8",
    )
    manifest = load_manifest(tmp_path)
    assert manifest.id == "demo.blueprint"


def test_load_manifest_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "does_not_exist")


def test_load_manifest_missing_required_field(tmp_path):
    manifest_file = tmp_path / "blueprint.yaml"
    manifest_file.write_text("id: demo.blueprint\nname: Demo\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required field"):
        load_manifest(manifest_file)


def test_paid_tier_requires_price():
    with pytest.raises(ValueError, match="positive price_usd"):
        BlueprintManifest(
            id="demo", name="Demo", version="0.1.0", publisher="Demo Co", entry="agent:run", tier="paid"
        )


def test_invalid_tier_rejected():
    with pytest.raises(ValueError, match="Unknown tier"):
        BlueprintManifest(
            id="demo", name="Demo", version="0.1.0", publisher="Demo Co", entry="agent:run", tier="premium"
        )


def test_entry_must_have_colon():
    with pytest.raises(ValueError, match="module:function"):
        BlueprintManifest(id="demo", name="Demo", version="0.1.0", publisher="Demo Co", entry="agent.run")
