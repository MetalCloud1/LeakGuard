import os
import asyncio
import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, get_db

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://testuser:testpass@postgres:5432/testdb"  
)

engine = None
TestingSessionLocal = None

async def wait_for_postgres(host, port, user, password, db, retries=10, delay=3):
    import asyncpg
    for i in range(retries):
        try:
            conn = await asyncpg.connect(
                host=host, port=port, user=user, password=password, database=db
            )
            await conn.close()
            print("Postgres is ready!")
            return
        except Exception as e:
            print(f"Waiting for Postgres... attempt {i+1}/{retries}: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("Postgres did not become ready in time")

@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_setup_db():
    global engine, TestingSessionLocal

    await wait_for_postgres("postgres", 5432, "testuser", "testpass", "testdb")

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def test_db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
def test_block_network_requests(monkeypatch):
    async def _blocked_request(*args, **kwargs):
        raise RuntimeError(
            "External HTTP requests are blocked in tests. Mock them with monkeypatch or respx."
        )
    monkeypatch.setattr("httpx.AsyncClient.request", _blocked_request)
    yield

@pytest_asyncio.fixture
async def test_async_client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
