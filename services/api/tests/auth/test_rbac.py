"""RBAC and auth smoke tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from afrosite_api.common.settings import get_settings
from afrosite_api.main import app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_login_and_me() -> None:
    settings = get_settings()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={"email": settings.bootstrap_owner_email, "password": settings.bootstrap_owner_password},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["role"] == "owner"


@pytest.mark.asyncio
async def test_owner_only_forbidden_for_cashier() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={"email": "cashier@afrosite.example", "password": "change-me-cashier"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        resp = await client.get("/auth/owner-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_owner_only_allowed_for_owner() -> None:
    settings = get_settings()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={"email": settings.bootstrap_owner_email, "password": settings.bootstrap_owner_password},
        )
        token = login.json()["access_token"]
        resp = await client.get("/auth/owner-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
