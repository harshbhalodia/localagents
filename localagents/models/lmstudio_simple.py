"""A Strands `Model` implementation for a simple, single-shot local inference endpoint:
`POST <host> {model, system_prompt, input, temperature, max_output_tokens}` -> a JSON response
containing the generated text (LM Studio's Responses-API-shaped custom endpoint, e.g.
`http://localhost:1234/api/v1/chat`, or any similarly-shaped local proxy).

This endpoint is non-streaming and has no native tool-calling protocol, so `tool_specs` are
accepted for interface compatibility but ignored. Pair this provider with agents that ground
themselves in pre-fetched facts (see `localagents.agents.wealth_advisor`) rather than relying on
the model to call tools itself.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any, TypeVar

import httpx
from strands.models.model import Model
from strands.types.content import Messages

T = TypeVar("T")


def _extract_text(payload: dict[str, Any], response_field: str = "output") -> str | None:
    """Mirrors Loonie's own `ai_provider.py::_extract_text` so this provider recognizes the
    same response shapes already verified working against the user's local endpoint."""
    node: Any = payload
    for part in response_field.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            node = None
            break
    if isinstance(node, str):
        return node

    output = payload.get("output")
    if isinstance(output, list):
        for item in reversed(output):
            if isinstance(item, dict) and item.get("type") == "message" and isinstance(item.get("content"), str):
                return item["content"]
        for item in reversed(output):
            if isinstance(item, dict) and item.get("type") not in ("reasoning", None) and isinstance(item.get("content"), str):
                return item["content"]
        if any(isinstance(item, dict) and item.get("type") == "reasoning" for item in output):
            raise RuntimeError(
                "The model was still reasoning when generation stopped and never produced an answer. "
                "It may need more time (increase `params.timeout`) or a smaller input."
            )

    for key in ("output", "response", "content", "text"):
        value = payload.get(key)
        if isinstance(value, str):
            return value

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]

    return None


class SimpleChatModel(Model):
    """Model provider for a `{model, system_prompt, input} -> text` local endpoint."""

    def __init__(
        self,
        endpoint: str,
        *,
        model_id: str,
        temperature: float = 0.2,
        max_output_tokens: int = 4096,
        response_field: str = "output",
        timeout: float | None = 120,
    ) -> None:
        self.endpoint = endpoint
        self.config: dict[str, Any] = {
            "model_id": model_id,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "response_field": response_field,
            "timeout": timeout,
        }

    def update_config(self, **model_config: Any) -> None:
        self.config.update(model_config)

    def get_config(self) -> dict[str, Any]:
        return self.config

    def _flatten_prompt(self, messages: Messages, system_prompt: str | None) -> tuple[str, str]:
        """Flattens a Strands message list into (system_prompt, input) for this single-turn
        endpoint — prior turns are joined into the input text."""
        lines: list[str] = []
        for message in messages:
            role = message.get("role", "user")
            for content in message.get("content", []):
                if "text" in content:
                    lines.append(f"{role}: {content['text']}")
        return system_prompt or "", "\n".join(lines)

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[Any] | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[dict[str, Any]]:
        system, user_input = self._flatten_prompt(messages, system_prompt)
        body = {
            "model": self.config["model_id"],
            "system_prompt": system,
            "input": user_input,
            "temperature": self.config["temperature"],
            "max_output_tokens": self.config["max_output_tokens"],
        }

        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"start": {}}}

        async with httpx.AsyncClient(timeout=self.config["timeout"]) as client:
            response = await client.post(self.endpoint, json=body)
            response.raise_for_status()
            payload = response.json()

        text = _extract_text(payload, self.config["response_field"])
        if text is None:
            raise RuntimeError(f"Could not find generated text in response: {payload!r}")

        yield {"contentBlockDelta": {"delta": {"text": text.strip()}}}
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "end_turn"}}

    async def structured_output(
        self, output_model: type[T], prompt: Messages, system_prompt: str | None = None, **kwargs: Any
    ) -> AsyncGenerator[dict[str, T | Any], None]:
        raise NotImplementedError(
            "SimpleChatModel does not support structured output (the underlying endpoint has no "
            "native JSON-schema mode)."
        )
        yield  # pragma: no cover - makes this an async generator per the Model interface
