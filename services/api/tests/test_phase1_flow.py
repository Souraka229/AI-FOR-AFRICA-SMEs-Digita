"""Phase-1 API smoke: tenant me → catalog → order → ledger."""

from datetime import date
from decimal import Decimal

import pytest
from httpx import AsyncClient

from afrosite_api.common.settings import get_settings


@pytest.mark.asyncio
async def test_catalog_order_ledger_flow(
    client: AsyncClient, owner_auth_header: dict[str, str]
) -> None:
    headers = owner_auth_header

    me_tenant = await client.get("/tenants/me", headers=headers)
    assert me_tenant.status_code == 200
    assert me_tenant.json()["id"] == get_settings().bootstrap_tenant_id

    created = await client.post(
        "/catalog/items",
        headers=headers,
        json={"name": "Attieke poisson", "price_xof": "2500"},
    )
    assert created.status_code == 201
    item_id = created.json()["id"]

    order = await client.post(
        "/orders",
        headers=headers,
        json={"catalog_item_id": item_id, "quantity": 2},
    )
    assert order.status_code == 201
    assert Decimal(order.json()["total_xof"]) == Decimal("5000")
    order_id = order.json()["id"]

    entry = await client.post(
        "/ledger/entries",
        headers=headers,
        json={
            "order_id": order_id,
            "direction": "credit",
            "amount_xof": "5000",
            "channel": "momo",
            "provider_ref": "gp_tx_demo",
        },
    )
    assert entry.status_code == 201

    today = date.today().isoformat()
    reconcile = await client.get(f"/ledger/reconcile/{today}", headers=headers)
    assert reconcile.status_code == 200
    assert Decimal(reconcile.json()["credits_xof"]) == Decimal("5000")
    assert reconcile.json()["entry_count"] == 1
