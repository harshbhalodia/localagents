from __future__ import annotations

import httpx
import pytest

from localagents.harness.config import ModelConfig
from localagents.models.lmstudio_simple import SimpleChatModel, _extract_text
from localagents.models.registry import build_model


def test_extract_text_handles_plain_output_field():
    assert _extract_text({"output": "hello"}) == "hello"


def test_extract_text_handles_responses_style_message_segment():
    payload = {"output": [{"type": "reasoning", "content": "thinking..."}, {"type": "message", "content": "hi"}]}
    assert _extract_text(payload) == "hi"


def test_extract_text_raises_when_only_reasoning_present():
    payload = {"output": [{"type": "reasoning", "content": "still thinking"}]}
    with pytest.raises(RuntimeError, match="still reasoning"):
        _extract_text(payload)


def test_build_model_resolves_lmstudio_simple_provider():
    config = ModelConfig(provider="lmstudio_simple", model_id="qwen/qwen3.6-35b-a3b", host="http://localhost:1234/api/v1/chat")
    model = build_model(config)
    assert isinstance(model, SimpleChatModel)
    assert model.get_config()["model_id"] == "qwen/qwen3.6-35b-a3b"


def test_stream_yields_expected_event_sequence():
    import asyncio
    import unittest.mock

    captured: dict = {}

    async def fake_post(self, url, json=None, **kwargs):
        captured["url"] = url
        captured["json"] = json
        return httpx.Response(200, json={"output": "42"}, request=httpx.Request("POST", url))

    model = SimpleChatModel("http://fake-host/chat", model_id="test-model")

    async def collect():
        return [
            event
            async for event in model.stream(
                messages=[{"role": "user", "content": [{"text": "hello"}]}], system_prompt="system prompt text"
            )
        ]

    with unittest.mock.patch("httpx.AsyncClient.post", fake_post):
        events = asyncio.run(collect())

    assert captured["url"] == "http://fake-host/chat"
    assert captured["json"]["model"] == "test-model"
    assert captured["json"]["system_prompt"] == "system prompt text"
    assert "hello" in captured["json"]["input"]

    assert events[0] == {"messageStart": {"role": "assistant"}}
    assert events[-1] == {"messageStop": {"stopReason": "end_turn"}}
    assert {"contentBlockDelta": {"delta": {"text": "42"}}} in events
