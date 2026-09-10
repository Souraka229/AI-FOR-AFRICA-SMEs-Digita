"""Tenant-scoped API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.deps import get_current_user, require_roles
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import UserPublic
from afrosite_api.db.models.tenant import Tenant
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    id: str = Field(min_length=3, max_length=64)
    name: str = Field(min_length=1, max_length=255)


class TenantPublic(BaseModel):
    id: str
    name: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: TenantCreate,
    _owner: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantPublic:
    existing = await session.get(Tenant, body.id)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant already exists")
    tenant = Tenant(id=body.id, name=body.name)
    session.add(tenant)
    await session.commit()
    return TenantPublic(id=tenant.id, name=tenant.name)


@router.get("/me")
async def get_my_tenant(
    user: Annotated[UserPublic, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantPublic:
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantPublic(id=tenant.id, name=tenant.name)


@router.get("")
async def list_tenants(
    _owner: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[TenantPublic]:
    result = await session.execute(select(Tenant).order_by(Tenant.created_at))
    return [TenantPublic(id=t.id, name=t.name) for t in result.scalars().all()]
