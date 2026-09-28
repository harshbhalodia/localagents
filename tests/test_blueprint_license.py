from __future__ import annotations

from dataclasses import dataclass

import pytest

from localagents.blueprints.license import EntitlementError, check_entitlement, sign, verify


@dataclass
class _FakeManifest:
    id: str
    version: str
    tier: str
    price_usd: float | None = None


def test_sign_and_verify_round_trip():
    token = sign("demo.blueprint", "0.1.0", "user-123", secret="s3cret")
    license_ = verify(token, secret="s3cret")
    assert license_.blueprint_id == "demo.blueprint"
    assert license_.version == "0.1.0"
    assert license_.licensee == "user-123"


def test_verify_rejects_tampered_token():
    token = sign("demo.blueprint", "0.1.0", "user-123", secret="s3cret")
    tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
    with pytest.raises(EntitlementError, match="does not match"):
        verify(tampered, secret="s3cret")


def test_verify_rejects_wrong_secret():
    token = sign("demo.blueprint", "0.1.0", "user-123", secret="s3cret")
    with pytest.raises(EntitlementError):
        verify(token, secret="wrong-secret")


def test_verify_rejects_malformed_token():
    with pytest.raises(EntitlementError, match="Malformed"):
        verify("not-a-valid-token", secret="s3cret")


def test_free_tier_always_permitted():
    manifest = _FakeManifest(id="demo", version="0.1.0", tier="free")
    assert check_entitlement(manifest, license_token=None) is True


def test_paid_tier_without_token_raises():
    manifest = _FakeManifest(id="demo", version="0.1.0", tier="paid", price_usd=4.99)
    with pytest.raises(EntitlementError, match="paid blueprint"):
        check_entitlement(manifest, license_token=None)


def test_paid_tier_with_valid_token_passes():
    manifest = _FakeManifest(id="demo", version="0.1.0", tier="paid", price_usd=4.99)
    token = sign("demo", "0.1.0", "user-123", secret="s3cret")
    assert check_entitlement(manifest, license_token=token, secret="s3cret") is True


def test_paid_tier_token_for_different_blueprint_rejected():
    manifest = _FakeManifest(id="demo", version="0.1.0", tier="paid", price_usd=4.99)
    token = sign("other.blueprint", "0.1.0", "user-123", secret="s3cret")
    with pytest.raises(EntitlementError, match="License token is for"):
        check_entitlement(manifest, license_token=token, secret="s3cret")
