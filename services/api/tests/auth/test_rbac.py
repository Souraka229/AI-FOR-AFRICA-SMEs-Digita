"""RBAC and auth smoke tests against an in-memory SQLite database."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import models so metadata is populated
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


@pytest.mark.asyncio
async def test_login_and_me(client: AsyncClient) -> None:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_owner_email,
            "password": settings.bootstrap_owner_password,
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
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
async def test_owner_only_allowed_for_owner(client: AsyncClient) -> None:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_owner_email,
            "password": settings.bootstrap_owner_password,
        },
    )
    token = login.json()["access_token"]
    resp = await client.get("/auth/owner-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
