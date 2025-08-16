import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app, get_db
from src.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
)

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def async_client(engine):
    async def override_get_db():
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(autouse=True)
def block_network_requests(monkeypatch):
    import httpx
    original_request = httpx.AsyncClient.request

    async def _maybe_blocked_request(self, method, url, *args, **kwargs):
        if isinstance(self._transport, ASGITransport):
            return await original_request(self, method, url, *args, **kwargs)
        raise RuntimeError("External HTTP requests are blocked in tests. Mock them.")

    monkeypatch.setattr("httpx.AsyncClient.request", _maybe_blocked_request)
    yield
