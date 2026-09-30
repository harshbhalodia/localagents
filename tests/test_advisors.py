from __future__ import annotations

import pytest

from localagents.advisors import (
    default_loonie_dir,
    list_published,
    load_pack,
    publish_to_dir,
    render_template,
    validate_pack,
)
from localagents.cli import main

GOOD = {
    "id": "acme.job_loss",
    "name": "Job Loss Check",
    "publisher": "Acme",
    "kind": "stress_test",
    "summary": "Checks how long your savings last if income stops.",
    "triggers": ["job loss"],
    "examples": ["What if I lose my job?"],
    "inputs": ["net_worth", "cashflow"],
    "scenarios": [{"id": "s1", "description": "Income stops for 3 months."}],
}


def test_good_pack_has_no_errors():
    report = validate_pack(GOOD)
    assert report.ok
    assert any("disclaimer" in w for w in report.warnings)


@pytest.mark.parametrize(
    "mutation, expected",
    [
        ({"id": ""}, "Missing 'id'"),
        ({"kind": "magic"}, "'kind' must be one of"),
        ({"scenarios": []}, "at least one scenario"),
        ({"scenarios": [{"id": "a", "description": "x"}, {"id": "a", "description": "y"}]}, "unique"),
    ],
)
def test_errors_block_a_pack(mutation, expected):
    report = validate_pack({**GOOD, **mutation})
    assert not report.ok
    assert any(expected in e for e in report.errors)


def test_unknown_inputs_and_missing_triggers_are_warnings_not_errors():
    report = validate_pack({**GOOD, "inputs": ["net_worth", "bank_password"], "triggers": []})
    assert report.ok
    assert any("bank_password" in w for w in report.warnings)
    assert any("triggers" in w for w in report.warnings)


def test_template_is_a_valid_pack(tmp_path):
    path = tmp_path / "starter.yaml"
    path.write_text(render_template(id="me.starter", name="Starter", publisher="Me"), encoding="utf-8")
    pack = load_pack(path)
    assert pack.id == "me.starter" and len(pack.scenarios) == 2 and "net_worth" in pack.inputs


def test_publish_copies_only_valid_packs(tmp_path):
    src = tmp_path / "pack.yaml"
    src.write_text(render_template(id="me.starter", name="Starter", publisher="Me"), encoding="utf-8")
    dest = tmp_path / "advisors"
    published = publish_to_dir(src, dest)
    assert published.name == "me.starter.yaml" and published.exists()
    assert [p.id for p in list_published(dest)] == ["me.starter"]

    bad = tmp_path / "bad.yaml"
    bad.write_text("id: x\n", encoding="utf-8")
    with pytest.raises(ValueError):
        publish_to_dir(bad, dest)


def test_default_dir_honours_override(monkeypatch, tmp_path):
    monkeypatch.setenv("LOONIE_ADVISORS_DIR", str(tmp_path / "custom"))
    assert default_loonie_dir() == tmp_path / "custom"
    monkeypatch.delenv("LOONIE_ADVISORS_DIR")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert default_loonie_dir() == tmp_path / "com.loonie.app" / "backend" / "data" / "advisors"


def test_cli_build_and_publish_flow(tmp_path, capsys):
    pack = tmp_path / "job_loss.yaml"
    assert main(["advisor", "init", str(pack), "--publisher", "Acme Co", "--kind", "stress_test"]) == 0
    assert main(["advisor", "init", str(pack)]) == 1  # refuses to overwrite
    assert main(["advisor", "validate", str(pack)]) == 0
    assert "OK:" in capsys.readouterr().out

    dest = tmp_path / "loonie_advisors"
    assert main(["advisor", "publish", str(pack), "--dir", str(dest)]) == 0
    assert main(["advisor", "list", "--dir", str(dest)]) == 0
    assert "acme_co.job_loss" in capsys.readouterr().out


def test_cli_publish_rejects_invalid(tmp_path, capsys):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: nothing\n", encoding="utf-8")
    assert main(["advisor", "validate", str(bad)]) == 1
    assert main(["advisor", "publish", str(bad), "--dir", str(tmp_path / "out")]) == 1
    assert not (tmp_path / "out").exists() or not list((tmp_path / "out").iterdir())
    assert "error:" in capsys.readouterr().err
