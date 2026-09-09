"""Catalog API (tenant-isolated)."""

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
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/catalog", tags=["catalog"])


class CatalogItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price_xof: Decimal = Field(gt=0)


class CatalogItemPublic(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None
    price_xof: Decimal


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    body: CatalogItemCreate,
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER, Role.CASHIER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CatalogItemPublic:
    item = CatalogItem(
        id=f"item-{uuid4().hex[:12]}",
        tenant_id=user.tenant_id,
        name=body.name,
        description=body.description,
        price_xof=body.price_xof,
    )
    session.add(item)
    await session.commit()
    return CatalogItemPublic(
        id=item.id,
        tenant_id=item.tenant_id,
        name=item.name,
        description=item.description,
        price_xof=item.price_xof,
    )


@router.get("/items")
async def list_items(
    user: Annotated[UserPublic, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[CatalogItemPublic]:
    result = await session.execute(
        select(CatalogItem).where(CatalogItem.tenant_id == user.tenant_id)
    )
    return [
        CatalogItemPublic(
            id=i.id,
            tenant_id=i.tenant_id,
            name=i.name,
            description=i.description,
            price_xof=i.price_xof,
        )
        for i in result.scalars().all()
    ]


@router.get("/items/{item_id}")
async def get_item(
    item_id: str,
    user: Annotated[UserPublic, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CatalogItemPublic:
    item = await session.get(CatalogItem, item_id)
    if item is None or item.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return CatalogItemPublic(
        id=item.id,
        tenant_id=item.tenant_id,
        name=item.name,
        description=item.description,
        price_xof=item.price_xof,
    )
