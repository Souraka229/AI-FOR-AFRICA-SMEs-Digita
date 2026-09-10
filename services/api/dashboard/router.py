"""Dashboard gérant — jour civil Bénin, encaissé seulement après verify()."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from auth.dependencies import require_access
from auth.schemas import Principal
from dashboard.schemas import DashboardOut
from dashboard.service import snapshot

router = APIRouter(tags=["dashboard"])


@router.get("/tenants/{tenant_slug}/dashboard", response_model=DashboardOut)
def tenant_dashboard(
    tenant_slug: str,
    _: Principal = Depends(require_access("dashboard:read")),
) -> DashboardOut:
    return DashboardOut.model_validate(snapshot(tenant_slug))
