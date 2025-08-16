import pytest
import re
from sqlalchemy.future import select
from src.models import User

@pytest.mark.asyncio
async def test_register_validation(async_client):
    response = await async_client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "StrongPass123!"
    })
    assert response.status_code == 201
    assert "msg" in response.json()

@pytest.mark.asyncio
async def test_verify_email_flow(async_client, db_session):
    result = await db_session.execute(select(User).where(User.username=="testuser"))
    user = result.scalars().first()
    token = user.verification_token

    response = await async_client.get(f"/verify-email?token={token}")
    assert response.status_code == 200
    assert "Email verified" in response.json()["msg"]

@pytest.mark.asyncio
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