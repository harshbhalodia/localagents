# Contributing to LocalAgents

Thanks for considering a contribution! LocalAgents is a small, early-stage project, so the
process is intentionally lightweight.

## Reporting issues

Search [existing issues](https://github.com/harshbhalodia/localagents/issues) before opening a
new one. Include the version of `localagents` and `strands-agents` you're using, your Python
version, and a minimal repro if possible. For security vulnerabilities, see
[SECURITY.md](SECURITY.md) instead of opening a public issue.

## Development setup

```bash
git clone https://github.com/harshbhalodia/localagents.git
cd localagents
python -m venv .venv
.venv\Scripts\activate   # Windows; `source .venv/bin/activate` on macOS/Linux
pip install -e ".[dev,ollama]"
```

## Running tests and lint

```bash
pytest
ruff check .
```

## Pull requests

1. Fork the repo and create a branch off `main`.
2. Keep changes focused — one logical change per PR.
3. Add or update tests for any behavior change.
4. Make sure `pytest` and `ruff check .` both pass.
5. Open a PR describing what changed and why.

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE), the same license that covers the rest of the project.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you're
expected to uphold it.
