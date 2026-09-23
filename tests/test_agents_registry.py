from __future__ import annotations

import pytest

from localagents.agents import available, get, register


def test_register_and_get_round_trip():
    @register("test-preset")
    def build_test_preset(harness):
        return harness

    assert get("test-preset") is build_test_preset
    assert "test-preset" in available()


def test_get_unknown_preset_raises_key_error():
    with pytest.raises(KeyError):
        get("does-not-exist")
