"""Clé d'amorçage locale — jamais en production."""

from __future__ import annotations

import hmac
import os

from fastapi import HTTPException, Header


def require_bootstrap_key(
    x_afrosite_bootstrap_key: str | None = Header(default=None),
) -> None:
    if os.getenv("AFROSITE_ENV", "development").lower() == "production":
        raise HTTPException(status_code=404, detail="Endpoint d'amorçage indisponible.")
    expected = os.getenv("AFROSITE_AUTH_BOOTSTRAP_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Amorçage auth non configuré.")
    if not x_afrosite_bootstrap_key or not hmac.compare_digest(
        x_afrosite_bootstrap_key,
        expected,
    ):
        raise HTTPException(status_code=401, detail="Clé d'amorçage invalide.")
