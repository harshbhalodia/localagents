from __future__ import annotations

import pytest

from localagents.harness.config import ModelConfig
from localagents.models.registry import build_model


def test_build_model_raises_for_unknown_provider():
    with pytest.raises(ValueError, match="Unknown model provider"):
        build_model(ModelConfig(provider="not-a-real-provider"))
