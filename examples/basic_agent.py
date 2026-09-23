"""Minimal LocalAgents example: build an agent from config (or local-first defaults) and ask
it something.

By default this targets a local Ollama server (http://localhost:11434, model "llama3"). Copy
config.example.yaml to config.yaml at the repo root and edit `model.provider`/`model.host` to
point at a different local endpoint instead (e.g. LM Studio's OpenAI-compatible server at
http://localhost:1234/v1 with provider: openai).

Run:
    python examples/basic_agent.py
"""
from __future__ import annotations

from pathlib import Path

from localagents import Harness

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def main() -> None:
    harness = Harness.from_file(CONFIG_PATH)
    agent = harness.build_agent(session_id="examples-basic-agent")
    result = agent("What is the square root of 1764?")
    print(result)


if __name__ == "__main__":
    main()
