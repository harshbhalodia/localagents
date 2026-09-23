"""Resolves a `ModelConfig` into a real Strands model-provider instance.

Provider SDKs (`ollama`, `openai`) are optional extras of `strands-agents`, so each branch
imports its provider lazily — a harness user who only wants Ollama doesn't need the `openai`
package installed, and vice versa.
"""
from __future__ import annotations

from typing import Any

from localagents.harness.config import ModelConfig


def build_model(config: ModelConfig) -> Any:
    params = dict(config.params or {})

    if config.provider == "ollama":
        try:
            from strands.models.ollama import OllamaModel
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "The 'ollama' model provider requires the optional dependency. "
                "Install it with: pip install 'strands-agents[ollama]'"
            ) from exc

        return OllamaModel(config.host, model_id=config.model_id, **params)

    if config.provider == "openai":
        # Also covers any OpenAI-compatible local server (LM Studio, vLLM, etc.) — just point
        # `host` at its base URL, e.g. http://localhost:1234/v1 for LM Studio.
        try:
            from strands.models.openai import OpenAIModel
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "The 'openai' model provider requires the optional dependency. "
                "Install it with: pip install 'strands-agents[openai]'"
            ) from exc

        return OpenAIModel(client_args={"base_url": config.host}, model_id=config.model_id, **params)

    if config.provider == "bedrock":
        from strands.models import BedrockModel

        return BedrockModel(model_id=config.model_id, **params)

    if config.provider == "lmstudio_simple":
        # A non-OpenAI-compatible local endpoint: POST {model, system_prompt, input} -> text.
        # See localagents.models.lmstudio_simple for the full request/response contract.
        from localagents.models.lmstudio_simple import SimpleChatModel

        return SimpleChatModel(config.host, model_id=config.model_id, **params)

    raise ValueError(
        f"Unknown model provider {config.provider!r}. Expected one of: "
        "'ollama', 'openai', 'bedrock', 'lmstudio_simple'."
    )
