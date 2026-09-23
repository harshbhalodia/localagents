from __future__ import annotations

from pathlib import Path

from localagents.harness.config import HarnessConfig, ModelConfig, load_config


def test_load_config_defaults_when_no_path_given():
    config = load_config(None)
    assert config == HarnessConfig()
    assert config.model.provider == "ollama"
    assert config.model.host == "http://localhost:11434"


def test_load_config_defaults_when_file_missing(tmp_path: Path):
    config = load_config(tmp_path / "does-not-exist.yaml")
    assert config == HarnessConfig()


def test_load_config_reads_yaml(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
name: my-app
model:
  provider: openai
  model_id: gpt-4o-mini
  host: http://localhost:1234/v1
  params:
    temperature: 0.2
load_tools_from_directory: true
sessions_dir: ./custom-sessions
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.name == "my-app"
    assert config.model == ModelConfig(
        provider="openai",
        model_id="gpt-4o-mini",
        host="http://localhost:1234/v1",
        params={"temperature": 0.2},
    )
    assert config.load_tools_from_directory is True
    assert config.sessions_dir == "./custom-sessions"
