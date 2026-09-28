"""Offline license/entitlement checks for paid blueprints.

Local-first design: a paid blueprint still runs entirely on the user's own machine — this
module never phones home to verify a purchase. A license token is a short string signed with
HMAC-SHA256 (`sign()`, called marketplace-side at purchase time); `verify()` only proves the
token was issued by whoever holds the shared secret — it is NOT a copy-protection/DRM scheme
(a token can still be shared), matching this project's local-first, no-lock-in philosophy. See
docs/architecture/blueprint-marketplace.md for the full trust model and its known limitations.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


class EntitlementError(RuntimeError):
    """Raised when a blueprint cannot be run because it is unpaid/unlicensed or the license
    token is malformed, forged, or does not match the blueprint being run."""


@dataclass
class License:
    blueprint_id: str
    version: str
    licensee: str
    signature: str

    @classmethod
    def parse(cls, token: str) -> License:
        try:
            blueprint_id, version, licensee, signature = token.split(":", 3)
        except ValueError as exc:
            raise EntitlementError(f"Malformed license token: {token!r}") from exc
        return cls(blueprint_id, version, licensee, signature)


def sign(blueprint_id: str, version: str, licensee: str, secret: str) -> str:
    """Marketplace-side helper: issues a signed license token at purchase time. `secret` is the
    marketplace's private signing key — never ship it inside the app, only the issued tokens."""
    payload = f"{blueprint_id}:{version}:{licensee}"
    signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify(token: str, secret: str) -> License:
    license_ = License.parse(token)
    payload = f"{license_.blueprint_id}:{license_.version}:{license_.licensee}"
    expected = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, license_.signature):
        raise EntitlementError("License signature does not match — invalid or tampered token.")
    return license_


def check_entitlement(manifest, license_token: str | None, secret: str | None = None) -> bool:
    """Returns True if `manifest`'s tier permits running. Free blueprints always pass. Paid
    blueprints require a `license_token` that verifies against `secret` and names this exact
    blueprint id/version; raises `EntitlementError` otherwise."""
    if manifest.tier == "free":
        return True

    if not license_token or not secret:
        raise EntitlementError(
            f"Blueprint {manifest.id!r} v{manifest.version} is a paid blueprint "
            f"(${manifest.price_usd}) — a valid license token is required to run it."
        )

    license_ = verify(license_token, secret)
    if license_.blueprint_id != manifest.id or license_.version != manifest.version:
        raise EntitlementError(
            f"License token is for {license_.blueprint_id!r} v{license_.version}, not "
            f"{manifest.id!r} v{manifest.version}."
        )
    return True
