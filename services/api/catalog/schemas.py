from __future__ import annotations

from pydantic import BaseModel, Field


class CatalogItemOut(BaseModel):
    sku: str
    name: str
    price_xof: int
    category: str
    available: bool
    unit: str | None = None
    currency: str = "XOF"


class CatalogUpsertBody(BaseModel):
    sku: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=160)
    price_xof: int = Field(ge=0, le=10_000_000)
    category: str = Field(min_length=2, max_length=80)
    available: bool = True
    unit: str | None = Field(default=None, max_length=40)


class CatalogPatchBody(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    price_xof: int | None = Field(default=None, ge=0, le=10_000_000)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    available: bool | None = None
    unit: str | None = Field(default=None, max_length=40)
