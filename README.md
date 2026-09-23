# LocalAgents Harness

**An open agent harness for building, running, extending, and composing AI agents — locally
or in the cloud.**

LocalAgents is thin, local-first glue on top of the [Strands Agents SDK](https://strandsagents.com/):
a small YAML config format for wiring up a model provider and local session persistence, a
registry for sharing reusable agent presets across projects, and re-exports of the pieces most
callers need day to day — so you don't have to re-learn Strands' full API surface to get a
working agent running against a local model.

## Why

Most agent frameworks assume a cloud model provider and a cloud-hosted memory/session store.
LocalAgents flips the default: point it at a local Ollama server or an OpenAI-compatible local
endpoint (LM Studio, vLLM, text-generation-webui, ...) and it persists sessions to your own
disk, with no account, API key, or network dependency required to get started. Cloud providers
(OpenAI, Amazon Bedrock, ...) are still fully supported when you want them.

LocalAgents itself is [Apache-2.0 licensed](LICENSE) and depends on `strands-agents` as an
ordinary pip dependency — it does not vendor or modify Strands' source.

## Relationship to Loonie

LocalAgents is being extracted as shared, reusable infrastructure out of
[Loonie](https://github.com/harshbhalodia/loonie), a personal-finance app that uses it to power
its in-app AI features. Loonie remains the flagship consumer of this harness, but LocalAgents
itself is a general-purpose, standalone project — not Loonie-specific.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e ".[ollama]"

copy config.example.yaml config.yaml   # Windows; `cp` on macOS/Linux
# Edit config.yaml if your Ollama server isn't at the default host/model.

python examples/basic_agent.py
```

```python
from localagents import Harness

harness = Harness.from_file("config.yaml")
agent = harness.build_agent(session_id="my-session")
result = agent("What is the square root of 1764?")
print(result)
```

## Project layout

```
localagents/
├── harness/    # YAML config loading + the Harness class that builds a strands.Agent
├── agents/     # Registry for reusable, named agent presets
├── models/     # Resolves config -> a real Strands model-provider instance (lazy imports)
├── tools/      # Re-exports Strands' @tool decorator
├── memory/     # Re-exports Strands' MemoryManager/MemoryStore + a build helper
└── sessions/   # Local-first session persistence via Strands' FileSessionManager
examples/       # Runnable example agent scripts
tests/          # pytest suite
```

## Status

Early alpha (`0.1.0`). The API surface may change without notice until `1.0`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities.

## License

Apache License 2.0 — see [LICENSE](LICENSE). LocalAgents depends on `strands-agents`
(Apache-2.0) and other third-party packages as ordinary pip dependencies; their own licenses
govern their respective source code.
