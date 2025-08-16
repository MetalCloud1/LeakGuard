import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import User 

@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_register_and_verify_email(async_client: AsyncClient, db_session: AsyncSession):
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "Password123!"
    }

    with patch("src.main.send_email") as mock_send:
        mock_send.return_value = None  
        response = await async_client.post("/register", json=user_data)
        assert response.status_code == 201
        assert response.json()["msg"] == "User registered successfully"

    await db_session.commit()

    result = await db_session.execute(
        select(User.verification_token).where(User.username == "testuser")
    )
    token = result.scalar_one()

    response = await async_client.get(f"/verify-email?token={token}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Email verified successfully"

    user = await db_session.get(User, token)  
    await db_session.commit()

@pytest.mark.asyncio
async def test_register_verify_and_login(async_client: AsyncClient):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "Password123!"
    }

    with patch("src.main.send_email") as mock_send:
        mock_send.return_value = None
        # Registro
        response = await async_client.post("/register", json=user_data)
        assert response.status_code == 201
        assert response.json()["msg"] == "User registered successfully"

    from src.models import User
    from src.database import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(User.verification_token).where(User.username == "testuser")
        )
        token = result.scalar_one()
        user = await session.get(User, token)
        user.is_verified = True
        await session.commit()

    data = {"username": "testuser", "password": "Password123!"}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"