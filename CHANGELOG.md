# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `localagents.blueprints` — a marketplace-ready package format for distributable agent logic:
  `BlueprintManifest`/`load_manifest` (blueprint.yaml parsing + validation), `LocalRegistry`/
  `load_catalog` (installed-blueprint discovery + marketplace catalog parsing), `load_blueprint`
  (imports a package's entry point), and offline HMAC-signed license tokens
  (`sign`/`verify`/`check_entitlement`) gating paid-tier blueprints.
- `localagents` CLI (`localagents/cli.py`, new `[project.scripts]` entry point):
  `blueprint init/validate/list/run`.
- Two example blueprints under `examples/blueprints/`: `loonie_core_stress_test` (free,
  in-house, 3-scenario stress test) and `maple_trust_advisory_stress_test` (paid, fictional-bank
  demo publisher, 5-scenario stress test) — plus `examples/stress_test_blueprint.py` wiring one
  against a real Loonie backend snapshot.
- `docs/architecture/blueprint-marketplace.md` (full marketplace architecture, trust model, and
  Loonie app-integration plan) and `docs/guides/onboarding-users.md` /
  `docs/guides/publishing-a-blueprint.md`.
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
