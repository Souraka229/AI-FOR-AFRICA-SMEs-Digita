"""DTO établissement — aligné sur Blueprint.tenant + table SQL."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Vertical = Literal["commerce", "restaurant", "services"]


class TenantRecord(BaseModel):
    slug: str
    name: str
    vertical: Vertical
    city: str = "Cotonou"
    neighborhood: str
    country: Literal["BJ"] = "BJ"


class CreateTenantBody(BaseModel):
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=120)
    vertical: Vertical
    city: str = Field(default="Cotonou", min_length=2, max_length=80)
    neighborhood: str = Field(min_length=2, max_length=80)


class PatchTenantBody(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    neighborhood: str | None = Field(default=None, min_length=2, max_length=80)
    city: str | None = Field(default=None, min_length=2, max_length=80)
