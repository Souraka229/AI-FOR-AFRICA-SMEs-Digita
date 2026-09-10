"""Socle FastAPI — Gate 1 Blueprint + ledger (mémoire, Postgres si DATABASE_URL)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "contracts" / "python"))

from afrosite_contracts import SCHEMA_VERSION, Blueprint  # noqa: E402

from auth.router import router as auth_router
from db.repo import Channel, get_repo
from catalog.router import router as catalog_router
from crm.router import router as crm_router
from dashboard.router import router as dashboard_router
from orders.router import router as orders_router
from tenants.router import router as tenants_router

app = FastAPI(title="Afrosite API", version="0.1.0")
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(catalog_router)
app.include_router(orders_router)
app.include_router(crm_router)
app.include_router(dashboard_router)

Role = Literal["owner", "cashier", "kitchen", "customer", "staff"]


class CreatePaymentBody(BaseModel):
    tenant_slug: str = Field(min_length=2)
    amount_xof: int = Field(gt=0)
    channel: Channel
    idem_key: str = Field(min_length=4)


class RefundBody(BaseModel):
    amount_xof: int = Field(gt=0)
    reason: str = Field(min_length=3)


def require_owner(role: str | None) -> None:
    if role != "owner":
        raise HTTPException(status_code=403, detail="Remboursement : rôle owner requis.")


@app.get("/health")
def health() -> dict[str, str | bool]:
    repo = get_repo()
    return {
        "ok": True,
        "service": "afrosite-api",
        "blueprint_schema": SCHEMA_VERSION,
        "currency": "XOF",
        "country": "BJ",
        "ledger": repo.backend,
    }


@app.post("/blueprints/validate")
def validate_blueprint(payload: dict) -> JSONResponse:
    try:
        blueprint = Blueprint.model_validate(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=json.loads(error.json()),
        ) from error
    return JSONResponse(
        {
            "ok": True,
            "slug": blueprint.tenant.slug,
            "vertical": blueprint.vertical,
            "schema_version": blueprint.schema_version,
        }
    )


@app.post("/payments")
def create_payment(body: CreatePaymentBody) -> dict:
    try:
        entry = get_repo().create_pending(
            tenant_slug=body.tenant_slug,
            amount_xof=body.amount_xof,
            channel=body.channel,
            idem_key=body.idem_key,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"ok": True, "entry": entry.to_dict()}


@app.post("/payments/{reference}/verify")
def verify_payment(reference: str) -> dict:
    entry = get_repo().verify(reference)
    if not entry:
        raise HTTPException(status_code=404, detail="Référence inconnue.")
    return {"ok": True, "entry": entry.to_dict()}


@app.post("/payments/{reference}/fail")
def fail_payment(reference: str) -> dict:
    entry = get_repo().fail(reference)
    if not entry:
        raise HTTPException(status_code=404, detail="Référence inconnue.")
    return {"ok": True, "entry": entry.to_dict()}


@app.post("/payments/{reference}/expire")
def expire_payment(reference: str) -> dict:
    entry = get_repo().expire(reference)
    if not entry:
        raise HTTPException(status_code=404, detail="Référence inconnue.")
    return {"ok": True, "entry": entry.to_dict()}


@app.post("/payments/{reference}/refund")
def refund_payment(
    reference: str,
    body: RefundBody,
    x_afrosite_role: str | None = Header(default=None),
) -> dict:
    require_owner(x_afrosite_role)
    entry = get_repo().refund(reference, body.amount_xof, body.reason)
    if not entry:
        raise HTTPException(
            status_code=400,
            detail="Remboursement refusé (pas confirmé, ou montant hors reste).",
        )
    return {"ok": True, "entry": entry.to_dict()}


@app.get("/ledger/{tenant_slug}")
def tenant_ledger(tenant_slug: str) -> dict:
    rows = get_repo().list_for_tenant(tenant_slug)
    return {"ok": True, "tenant": tenant_slug, "entries": [row.to_dict() for row in rows]}
