"""Catalogue API — lecture tous rôles du tenant, écriture owner."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import require_access
from auth.schemas import Principal
from catalog.schemas import CatalogItemOut, CatalogPatchBody, CatalogUpsertBody
from catalog.store import CatalogItem, get_catalog_store

router = APIRouter(tags=["catalog"])


@router.get("/tenants/{tenant_slug}/catalog", response_model=list[CatalogItemOut])
def list_catalog(
    tenant_slug: str,
    _: Principal = Depends(require_access("catalog:read")),
) -> list[CatalogItemOut]:
    return [
        CatalogItemOut.model_validate(item.to_dict())
        for item in get_catalog_store().list(tenant_slug)
    ]


@router.get("/tenants/{tenant_slug}/catalog/{sku}", response_model=CatalogItemOut)
def get_item(
    tenant_slug: str,
    sku: str,
    _: Principal = Depends(require_access("catalog:read")),
) -> CatalogItemOut:
    item = get_catalog_store().get(tenant_slug, sku)
    if not item:
        raise HTTPException(status_code=404, detail="SKU inconnu.")
    return CatalogItemOut.model_validate(item.to_dict())


@router.put("/tenants/{tenant_slug}/catalog/{sku}", response_model=CatalogItemOut)
def upsert_item(
    tenant_slug: str,
    sku: str,
    body: CatalogUpsertBody,
    _: Principal = Depends(require_access("catalog:write")),
) -> CatalogItemOut:
    if body.sku != sku:
        raise HTTPException(status_code=400, detail="SKU du chemin et du corps différents.")
    item = get_catalog_store().upsert(
        tenant_slug,
        CatalogItem(
            sku=body.sku,
            name=body.name,
            price_xof=body.price_xof,
            category=body.category,
            available=body.available,
            unit=body.unit,
        ),
    )
    return CatalogItemOut.model_validate(item.to_dict())


@router.patch("/tenants/{tenant_slug}/catalog/{sku}", response_model=CatalogItemOut)
def patch_item(
    tenant_slug: str,
    sku: str,
    body: CatalogPatchBody,
    _: Principal = Depends(require_access("catalog:write")),
) -> CatalogItemOut:
    item = get_catalog_store().patch(
        tenant_slug, sku, **body.model_dump(exclude_unset=True)
    )
    if not item:
        raise HTTPException(status_code=404, detail="SKU inconnu.")
    return CatalogItemOut.model_validate(item.to_dict())
