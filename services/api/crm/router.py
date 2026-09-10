"""CRM — téléphone Bénin, historique, fidélité. Pas de montant client."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import require_access
from auth.schemas import Principal
from crm.phone import normalize_bj_phone
from crm.schemas import CustomerOut, CustomerUpsertBody, VisitCreateBody
from crm.store import get_crm_store

router = APIRouter(tags=["crm"])


def _phone_or_400(raw: str) -> str:
    try:
        return normalize_bj_phone(raw)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/tenants/{tenant_slug}/crm/customers", response_model=list[CustomerOut])
def list_customers(
    tenant_slug: str,
    _: Principal = Depends(require_access("crm:read")),
) -> list[CustomerOut]:
    return [
        CustomerOut.model_validate(row.to_dict())
        for row in get_crm_store().list(tenant_slug)
    ]


@router.put("/tenants/{tenant_slug}/crm/customers/{phone}", response_model=CustomerOut)
def upsert_customer(
    tenant_slug: str,
    phone: str,
    body: CustomerUpsertBody,
    _: Principal = Depends(require_access("crm:write")),
) -> CustomerOut:
    canonical = _phone_or_400(phone)
    row = get_crm_store().upsert(tenant_slug, canonical, body.display_name)
    return CustomerOut.model_validate(row.to_dict())


@router.get("/tenants/{tenant_slug}/crm/customers/{phone}", response_model=CustomerOut)
def get_customer(
    tenant_slug: str,
    phone: str,
    _: Principal = Depends(require_access("crm:read")),
) -> CustomerOut:
    canonical = _phone_or_400(phone)
    row = get_crm_store().get(tenant_slug, canonical)
    if not row:
        raise HTTPException(status_code=404, detail="Client inconnu.")
    return CustomerOut.model_validate(row.to_dict())


@router.post(
    "/tenants/{tenant_slug}/crm/customers/{phone}/visits",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
)
def add_visit(
    tenant_slug: str,
    phone: str,
    body: VisitCreateBody,
    _: Principal = Depends(require_access("crm:write")),
) -> CustomerOut:
    canonical = _phone_or_400(phone)
    try:
        row = get_crm_store().add_visit(
            tenant_slug,
            canonical,
            body.idem_key,
            body.order_id,
        )
    except ValueError as error:
        code = str(error)
        if code == "client_inconnu":
            raise HTTPException(status_code=404, detail="Client inconnu.") from error
        if code == "commande_inconnue":
            raise HTTPException(status_code=400, detail="Commande inconnue.") from error
        if code == "idempotence_conflit":
            raise HTTPException(status_code=409, detail="Clé d'idempotence déjà utilisée.") from error
        raise HTTPException(status_code=400, detail=code) from error
    return CustomerOut.model_validate(row.to_dict())
