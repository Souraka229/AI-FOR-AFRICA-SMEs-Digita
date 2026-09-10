"""DTO d'authentification — aucun secret dans les réponses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["owner", "cashier", "kitchen", "customer"]


class IssueTokenBody(BaseModel):
    subject: str = Field(min_length=2, max_length=120, pattern=r"^[a-zA-Z0-9@._+-]+$")
    tenant_slug: str = Field(
        min_length=2,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    role: Role
    ttl_seconds: int = Field(default=3600, ge=60, le=3600)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class Principal(BaseModel):
    subject: str
    tenant_slug: str
    role: Role
    permissions: list[str]
    expires_at: int
