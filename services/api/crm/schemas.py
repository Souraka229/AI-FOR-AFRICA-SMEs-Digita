from __future__ import annotations

from pydantic import BaseModel, Field


class CustomerUpsertBody(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)


class VisitCreateBody(BaseModel):
    idem_key: str = Field(min_length=4, max_length=120)
    order_id: str | None = None


class VisitOut(BaseModel):
    id: str
    phone: str
    order_id: str | None
    amount_xof: int | None
    currency: str | None
    created_at: str


class CustomerOut(BaseModel):
    tenant_slug: str
    phone: str
    display_name: str
    loyalty_count: int
    created_at: str
    visits: list[VisitOut] = Field(default_factory=list)
