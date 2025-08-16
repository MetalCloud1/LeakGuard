# conftest.py
import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app, get_db
from src.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import event
import httpx

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
TestingSessionLocal = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


def _restart_savepoint(session: Session, transaction):
    if transaction.nested and not session.is_active:
        session.begin_nested()

event.listen(Session, "after_transaction_end", _restart_savepoint)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        async_session = AsyncSession(bind=connection, expire_on_commit=False, autoflush=False)

       
        await async_session.begin_nested()

        try:
            yield async_session
        finally:
            await async_session.close()
            await transaction.rollback()


@pytest_asyncio.fixture(autouse=True)
def block_network_requests(monkeypatch):
    original_request = httpx.AsyncClient.request

    async def _maybe_blocked_request(self, method, url, *args, **kwargs):
        # permitir requests internas a la app via ASGITransport
        if isinstance(self._transport, ASGITransport):
            return await original_request(self, method, url, *args, **kwargs)
        raise RuntimeError(
            "External HTTP requests are blocked in tests. Mock them with monkeypatch o respx."
        )

    monkeypatch.setattr("httpx.AsyncClient.request", _maybe_blocked_request)
    yield


@pytest_asyncio.fixture
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
