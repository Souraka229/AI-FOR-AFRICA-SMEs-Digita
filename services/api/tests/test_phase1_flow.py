"""Phase-1 API smoke: tenant me → catalog → order → ledger."""

from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import afrosite_api.db.models  # noqa: F401
from afrosite_api.common.settings import get_settings
from afrosite_api.db.base import Base
from afrosite_api.db.session import get_db_session, reset_engine
from afrosite_api.main import app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()
    reset_engine()
    yield
    get_settings.cache_clear()
    reset_engine()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    await engine.dispose()


async def _owner_token(client: AsyncClient) -> str:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_owner_email,
            "password": settings.bootstrap_owner_password,
        },
    )
    assert login.status_code == 200
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_catalog_order_ledger_flow(client: AsyncClient) -> None:
    token = await _owner_token(client)
    headers = {"Authorization": f"Bearer {token}"}

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
