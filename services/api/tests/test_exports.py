"""Export CSV : owner only, isolation tenant, jamais de hash mot de passe."""

import csv
from io import StringIO

import pytest
from httpx import AsyncClient

from afrosite_api.common.settings import get_settings


def _rows(body: bytes) -> list[list[str]]:
    text = body.decode("utf-8-sig")
    return list(csv.reader(StringIO(text)))


@pytest.mark.asyncio
async def test_owner_exports_ventes_and_transactions(
    client: AsyncClient, owner_auth_header: dict[str, str]
) -> None:
    headers = owner_auth_header
    created = await client.post(
        "/catalog/items",
        headers=headers,
        json={"name": "Pagne wax", "price_xof": "12500"},
    )
    assert created.status_code == 201
    item_id = created.json()["id"]
    order = await client.post(
        "/orders",
        headers=headers,
        json={"catalog_item_id": item_id, "quantity": 1},
    )
    assert order.status_code == 201
    await client.post(
        "/ledger/entries",
        headers=headers,
        json={
            "order_id": order.json()["id"],
            "direction": "credit",
            "amount_xof": "12500",
            "channel": "momo",
            "provider_ref": "gp_tx_csv",
        },
    )

    ventes = await client.get("/exports/ventes.csv", headers=headers)
    assert ventes.status_code == 200
    assert "text/csv" in ventes.headers["content-type"]
    vente_rows = _rows(ventes.content)
    assert vente_rows[0][4] == "total_xof"
    assert any(row[4] == "12500.00" or row[4] == "12500" for row in vente_rows[1:])

    tx = await client.get("/exports/transactions.csv", headers=headers)
    assert tx.status_code == 200
    tx_rows = _rows(tx.content)
    assert any("gp_tx_csv" in row for row in tx_rows[1:])

    people = await client.get("/exports/clients.csv", headers=headers)
    assert people.status_code == 200
    people_rows = _rows(people.content)
    assert people_rows[0] == ["id", "email", "role", "created_at"]
    blob = people.content.decode("utf-8-sig").lower()
    assert "password" not in blob
    assert "hash" not in blob
    assert get_settings().bootstrap_owner_email in blob


@pytest.mark.asyncio
async def test_cashier_cannot_export(client: AsyncClient) -> None:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_cashier_email,
            "password": settings.bootstrap_cashier_password,
        },
    )
    token = login.json()["access_token"]
    resp = await client.get(
        "/exports/ventes.csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unknown_export_is_404(
    client: AsyncClient, owner_auth_header: dict[str, str]
) -> None:
    resp = await client.get("/exports/secrets.csv", headers=owner_auth_header)
    assert resp.status_code == 404
