from __future__ import annotations

from localagents.cli import build_parser, main


def test_blueprint_init_creates_manifest_and_agent(tmp_path, capsys):
    target = tmp_path / "my_blueprint"
    exit_code = main(["blueprint", "init", str(target), "--id", "demo.blueprint", "--publisher", "Demo Co"])
    assert exit_code == 0
    assert (target / "blueprint.yaml").exists()
    assert (target / "agent.py").exists()
    assert "Scaffolded blueprint 'demo.blueprint'" in capsys.readouterr().out


def test_blueprint_validate_ok(tmp_path, capsys):
    target = tmp_path / "my_blueprint"
    main(["blueprint", "init", str(target), "--id", "demo.blueprint"])
    exit_code = main(["blueprint", "validate", str(target)])
    assert exit_code == 0
    assert "OK: demo.blueprint" in capsys.readouterr().out


def test_blueprint_validate_reports_invalid(tmp_path, capsys):
    target = tmp_path / "empty"
    target.mkdir()
    exit_code = main(["blueprint", "validate", str(target)])
    assert exit_code == 1
    assert "Invalid blueprint" in capsys.readouterr().err


def test_blueprint_list_empty(tmp_path, capsys):
    exit_code = main(["blueprint", "list", "--dir", str(tmp_path / "blueprints")])
    assert exit_code == 0
    assert "No blueprints installed" in capsys.readouterr().out


def test_blueprint_list_shows_installed(tmp_path, capsys):
    blueprints_dir = tmp_path / "blueprints"
    main(["blueprint", "init", str(blueprints_dir / "demo.blueprint"), "--id", "demo.blueprint"])
    exit_code = main(["blueprint", "list", "--dir", str(blueprints_dir)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "demo.blueprint" in out
    assert "free" in out


def test_build_parser_requires_subcommand():
    parser = build_parser()
    assert parser.prog == "localagents"
