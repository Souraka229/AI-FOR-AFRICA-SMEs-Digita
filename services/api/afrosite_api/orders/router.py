"""Orders API (tenant-isolated; amount recalculated server-side)."""

from decimal import Decimal
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.deps import get_current_user, require_roles
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import UserPublic
from afrosite_api.db.models.catalog_item import CatalogItem
from afrosite_api.db.models.order import Order
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    catalog_item_id: str
    quantity: int = Field(ge=1, le=100)


class OrderPublic(BaseModel):
    id: str
    tenant_id: str
    catalog_item_id: str
    quantity: int
    unit_price_xof: Decimal
    total_xof: Decimal
    status: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER, Role.CASHIER, Role.CUSTOMER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrderPublic:
    item = await session.get(CatalogItem, body.catalog_item_id)
    if item is None or item.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")
    unit = Decimal(item.price_xof)
    total = unit * body.quantity
    order = Order(
        id=f"ord-{uuid4().hex[:12]}",
        tenant_id=user.tenant_id,
        catalog_item_id=item.id,
        quantity=body.quantity,
        unit_price_xof=unit,
        total_xof=total,
        status="pending",
    )
    session.add(order)
    await session.commit()
    return OrderPublic(
        id=order.id,
        tenant_id=order.tenant_id,
        catalog_item_id=order.catalog_item_id,
        quantity=order.quantity,
        unit_price_xof=order.unit_price_xof,
        total_xof=order.total_xof,
        status=order.status,
    )


@router.get("")
async def list_orders(
    user: Annotated[UserPublic, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[OrderPublic]:
    result = await session.execute(select(Order).where(Order.tenant_id == user.tenant_id))
    return [
        OrderPublic(
            id=o.id,
            tenant_id=o.tenant_id,
            catalog_item_id=o.catalog_item_id,
            quantity=o.quantity,
            unit_price_xof=o.unit_price_xof,
            total_xof=o.total_xof,
            status=o.status,
        )
        for o in result.scalars().all()
    ]
