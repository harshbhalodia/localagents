# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project scaffold: `pyproject.toml` (hatchling build, Apache-2.0), `.gitignore`,
  `config.example.yaml`.
- `localagents.harness` — YAML-driven `HarnessConfig`/`ModelConfig` and a `Harness` class that
  builds a configured `strands.Agent`.
- `localagents.models` — provider registry resolving config into `OllamaModel`, `OpenAIModel`
  (also covers OpenAI-compatible local servers such as LM Studio), or `BedrockModel`
  instances, with lazy imports for optional provider extras.
- `localagents.sessions` — local-first session persistence via Strands' `FileSessionManager`.
- `localagents.memory` — thin re-export of Strands' `MemoryManager`/`MemoryStore`.
- `localagents.tools` — re-export of Strands' `@tool` decorator.
- `localagents.agents` — registry for named, reusable agent presets.
- `examples/basic_agent.py` — minimal runnable example.
- Project documentation: `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- Test suite covering config loading, the agent-preset registry, and the model registry's
  error handling.

[Unreleased]: https://github.com/harshbhalodia/localagents/commits/main
