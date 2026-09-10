from __future__ import annotations

from pydantic import BaseModel, Field


class OrderLineIn(BaseModel):
    sku: str = Field(min_length=2, max_length=80)
    qty: int = Field(ge=1, le=99)


class CreateOrderBody(BaseModel):
    items: list[OrderLineIn] = Field(min_length=1, max_length=40)
    idem_key: str = Field(min_length=4, max_length=120)


class OrderLineOut(BaseModel):
    sku: str
    name: str
    qty: int
    unit_price_xof: int
    line_total_xof: int


class OrderOut(BaseModel):
    id: str
    tenant_slug: str
    created_by: str
    status: str
    amount_xof: int
    currency: str = "XOF"
    lines: list[OrderLineOut]
    created_at: str
