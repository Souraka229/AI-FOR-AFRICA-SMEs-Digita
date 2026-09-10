"""Jetons courts signés HS256 et matrice de permissions Afrosite."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from auth.schemas import Principal, Role

ISSUER = "afrosite-api"
AUDIENCE = "afrosite"
ALGORITHM = "HS256"

ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    "owner": frozenset(
        {
            "tenant:read",
            "tenant:manage",
            "catalog:read",
            "catalog:write",
            "orders:read",
            "orders:write",
            "crm:read",
            "crm:write",
            "dashboard:read",
            "exports:read",
        }
    ),
    "cashier": frozenset(
        {
            "tenant:read",
            "catalog:read",
            "orders:read",
            "orders:write",
            "crm:read",
            "crm:write",
            "dashboard:read",
        }
    ),
    "kitchen": frozenset(
        {
            "tenant:read",
            "catalog:read",
            "orders:read",
            "orders:write",
        }
    ),
    "customer": frozenset({"tenant:read", "catalog:read", "orders:create"}),
}


class AuthConfigurationError(RuntimeError):
    pass


def _secret() -> str:
    secret = os.getenv("AFROSITE_AUTH_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise AuthConfigurationError(
            "AFROSITE_AUTH_SECRET doit contenir au moins 32 octets."
        )
    return secret


def permissions_for(role: Role) -> list[str]:
    return sorted(ROLE_PERMISSIONS[role])


def issue_token(
    *,
    subject: str,
    tenant_slug: str,
    role: Role,
    ttl_seconds: int,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "tenant": tenant_slug,
        "role": role,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(seconds=ttl_seconds),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> Principal:
    payload = jwt.decode(
        token,
        _secret(),
        algorithms=[ALGORITHM],
        audience=AUDIENCE,
        issuer=ISSUER,
        leeway=5,
        options={"require": ["sub", "tenant", "role", "iat", "nbf", "exp"]},
    )
    role = payload.get("role")
    if role not in ROLE_PERMISSIONS:
        raise InvalidTokenError("Rôle inconnu.")
    return Principal(
        subject=str(payload["sub"]),
        tenant_slug=str(payload["tenant"]),
        role=role,
        permissions=permissions_for(role),
        expires_at=int(payload["exp"]),
    )
