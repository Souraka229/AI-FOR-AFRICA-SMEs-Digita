"""Commandes — SKU + qty seulement ; le serveur calcule le FCFA."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import require_access, require_any
from auth.schemas import Principal
from orders.schemas import CreateOrderBody, OrderOut
from orders.store import get_order_store

router = APIRouter(tags=["orders"])


def _visible(principal: Principal, order) -> bool:
    if principal.role == "customer":
        return order.created_by == principal.subject
    return True


@router.post(
    "/tenants/{tenant_slug}/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    tenant_slug: str,
    body: CreateOrderBody,
    principal: Principal = Depends(require_any("orders:create", "orders:write")),
) -> OrderOut:
    try:
        order = get_order_store().create(
            tenant_slug,
            principal.subject,
            [(line.sku, line.qty) for line in body.items],
            body.idem_key,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return OrderOut.model_validate(order.to_dict())


@router.get("/tenants/{tenant_slug}/orders", response_model=list[OrderOut])
def list_orders(
    tenant_slug: str,
    principal: Principal = Depends(require_any("orders:read", "orders:create")),
) -> list[OrderOut]:
    subject = principal.subject if principal.role == "customer" else None
    rows = get_order_store().list_for(tenant_slug, subject)
    return [OrderOut.model_validate(row.to_dict()) for row in rows]


@router.get("/tenants/{tenant_slug}/orders/{order_id}", response_model=OrderOut)
def get_order(
    tenant_slug: str,
    order_id: str,
    principal: Principal = Depends(require_any("orders:read", "orders:create")),
) -> OrderOut:
    order = get_order_store().get(tenant_slug, order_id)
    if not order or not _visible(principal, order):
        raise HTTPException(status_code=404, detail="Commande inconnue.")
    return OrderOut.model_validate(order.to_dict())


@router.post("/tenants/{tenant_slug}/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    tenant_slug: str,
    order_id: str,
    principal: Principal = Depends(require_access("orders:write")),
) -> OrderOut:
    order = get_order_store().cancel(tenant_slug, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande inconnue.")
    return OrderOut.model_validate(order.to_dict())
