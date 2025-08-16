import pytest_asyncio
from src.models import User
from src.database import SessionLocal
from sqlalchemy.future import select
import re

@pytest_asyncio.mark.asyncio
async def test_register_validation(async_client):
    response = await async_client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "StrongPass123!"
    })
    assert response.status_code == 201
    assert "msg" in response.json()

    response = await async_client.post("/register", json={
        "username": "testuser",
        "email": "test2@example.com",
        "full_name": "Test User",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400

    response = await async_client.post("/register", json={
        "username": "testuser2",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400

@pytest_asyncio.mark.asyncio
async def test_verify_email_flow(async_client):
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.username=="testuser"))
        user = result.scalars().first()
        token = user.verification_token

    response = await async_client.get(f"/verify-email?token={token}")
    assert response.status_code == 200
    assert "Email verified" in response.json()["msg"]

    response = await async_client.get("/verify-email?token=invalidtoken")
    assert response.status_code == 400

@pytest_asyncio.mark.asyncio
async def test_login_and_userinfo(async_client):
    response = await async_client.post("/token", data={
        "username": "testuser",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert re.match(r"^[A-Za-z0-9\-._~+/]+=*$", token)

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "hashed_password" not in data

@pytest_asyncio.mark.asyncio
async def test_rate_limit(async_client):
    for _ in range(5):
        response = await async_client.post("/token", data={
            "username": "testuser",
            "password": "WrongPass!"
        })
    response = await async_client.post("/token", data={
        "username": "testuser",
        "password": "WrongPass!"
    })
    assert response.status_code == 429

@pytest_asyncio.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
