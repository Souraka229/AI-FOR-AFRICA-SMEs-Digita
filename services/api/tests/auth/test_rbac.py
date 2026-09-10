"""RBAC and auth smoke tests against an in-memory SQLite database."""

import pytest
from httpx import AsyncClient

from afrosite_api.common.settings import get_settings


@pytest.mark.asyncio
async def test_login_and_me(client: AsyncClient, owner_auth_header: dict[str, str]) -> None:
    settings = get_settings()
    me = await client.get("/auth/me", headers=owner_auth_header)
    assert me.status_code == 200
    assert me.json()["role"] == "owner"
    assert me.json()["tenant_id"] == settings.bootstrap_tenant_id


@pytest.mark.asyncio
async def test_owner_only_forbidden_for_cashier(client: AsyncClient) -> None:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_cashier_email,
            "password": settings.bootstrap_cashier_password,
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    resp = await client.get("/auth/owner-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_owner_only_allowed_for_owner(
    client: AsyncClient, owner_auth_header: dict[str, str]
) -> None:
    resp = await client.get("/auth/owner-only", headers=owner_auth_header)
    assert resp.status_code == 200
