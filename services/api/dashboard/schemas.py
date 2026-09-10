from __future__ import annotations

from pydantic import BaseModel, Field


class TopItemOut(BaseModel):
    sku: str
    name: str
    qty: int
    amount_xof: int


class LateOrderOut(BaseModel):
    id: str
    amount_xof: int
    created_at: str
    age_seconds: int


class DashboardOut(BaseModel):
    tenant_slug: str
    timezone: str
    day: str
    currency: str = "XOF"
    activity_count: int
    activity_xof: int
    average_basket_xof: int
    collected_xof: int
    top_items: list[TopItemOut] = Field(default_factory=list)
    late_orders: list[LateOrderOut] = Field(default_factory=list)
