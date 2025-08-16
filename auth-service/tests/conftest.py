import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.database import Base, get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://testuser:testpass@postgres:5432/testdb"


engine = None
TestingSessionLocal = None


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    global engine, TestingSessionLocal
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop tablas y cerrar engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
def block_network_requests(monkeypatch):
    async def _blocked_request(*args, **kwargs):
        raise RuntimeError(
            "External HTTP requests are blocked in tests. Mock them with monkeypatch or respx."
        )

    monkeypatch.setattr("httpx.AsyncClient.request", _blocked_request)
    yield


@pytest_asyncio.fixture
async def async_client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
