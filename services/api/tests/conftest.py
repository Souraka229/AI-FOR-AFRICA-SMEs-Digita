"""Shared async SQLite test client for API route tests."""

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


@pytest_asyncio.fixture
async def owner_auth_header(client: AsyncClient) -> dict[str, str]:
    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={
            "email": settings.bootstrap_owner_email,
            "password": settings.bootstrap_owner_password,
        },
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}
