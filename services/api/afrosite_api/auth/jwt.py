"""JWT create/decode helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from afrosite_api.auth.roles import Role
from afrosite_api.common.settings import Settings


def create_access_token(
    *,
    subject: str,
    email: str,
    role: Role,
    tenant_id: str,
    settings: Settings,
) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role.value,
        "tenant_id": tenant_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
