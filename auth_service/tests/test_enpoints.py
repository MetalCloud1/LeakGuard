import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(test_async_client: AsyncClient):
    response = await test_async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_register_and_verify_email(test_async_client: AsyncClient, db_session):
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "Password123!"
    }
    response = await test_async_client.post("/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["msg"] == "User registered successfully"

    
    result = await db_session.execute(
        "SELECT verification_token FROM users WHERE username='testuser'"
    )
    token = result.scalar_one()

    
    response = await test_async_client.get(f"/verify-email?token={token}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Email verified successfully"

@pytest.mark.asyncio
async def test_login_and_get_current_user(test_async_client: AsyncClient):
    
    data = {"username": "testuser", "password": "Password123!"}
    response = await test_async_client.post("/token", data=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    token = json_data["access_token"]

    
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
