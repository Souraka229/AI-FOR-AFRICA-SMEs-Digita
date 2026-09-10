"""API établissements — un jeton = un tenant, jamais de liste globale."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from auth.bootstrap import require_bootstrap_key
from auth.dependencies import require_access
from auth.schemas import Principal
from tenants.schemas import CreateTenantBody, PatchTenantBody, TenantRecord
from tenants.store import TenantRow, get_tenant_store

router = APIRouter(tags=["tenants"])


@router.post(
    "/tenants",
    response_model=TenantRecord,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    body: CreateTenantBody,
    _: None = Depends(require_bootstrap_key),
) -> TenantRecord:
    store = get_tenant_store()
    try:
        row = store.create(
            TenantRow(
                slug=body.slug,
                name=body.name,
                vertical=body.vertical,
                city=body.city,
                neighborhood=body.neighborhood,
            )
        )
    except ValueError as error:
        if str(error) == "slug_exists":
            raise HTTPException(status_code=409, detail="Slug déjà pris.") from error
        raise
    return row.to_record()


@router.get("/tenants/{tenant_slug}", response_model=TenantRecord)
def get_tenant(
    tenant_slug: str,
    _: Principal = Depends(require_access("tenant:read")),
) -> TenantRecord:
    row = get_tenant_store().get(tenant_slug)
    if not row:
        raise HTTPException(status_code=404, detail="Établissement inconnu.")
    return row.to_record()


@router.patch("/tenants/{tenant_slug}", response_model=TenantRecord)
def patch_tenant(
    tenant_slug: str,
    body: PatchTenantBody,
    _: Principal = Depends(require_access("tenant:manage")),
) -> TenantRecord:
    updates = body.model_dump(exclude_unset=True)
    row = get_tenant_store().update(tenant_slug, **updates)
    if not row:
        raise HTTPException(status_code=404, detail="Établissement inconnu.")
    return row.to_record()
