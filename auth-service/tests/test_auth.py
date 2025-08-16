import pytest
import re
from sqlalchemy.future import select
from src.models import User

JWT_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


@pytest.mark.asyncio
async def test_register_validation(async_client):
    response = await async_client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 201, f"expected 201, got {response.status_code} - {response.text}"
    assert "msg" in response.json(), f"response body missing 'msg': {response.text}"

    response = await async_client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "full_name": "Test User",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 400, f"expected 400 for duplicate username, got {response.status_code}"

    response = await async_client.post(
        "/register",
        json={
            "username": "testuser2",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 400, f"expected 400 for duplicate email, got {response.status_code}"


@pytest.mark.asyncio
async def test_verify_email_flow(async_client, db_session):
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalars().first()
    assert user is not None, "testuser not found in DB; registration likely failed"
    token = user.verification_token
    assert token, "verification_token missing for testuser"

    response = await async_client.get(f"/verify-email?token={token}")
    assert response.status_code == 200, f"expected 200 on valid token, got {response.status_code}"
    body = response.json()
    assert "msg" in body and "verified" in body["msg"].lower(), f"unexpected verify response: {body}"

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user_after = result.scalars().first()
    assert user_after is not None, "user disappeared after verification"
    assert user_after.is_verified is True, "user.is_verified should be True after verification"
    assert user_after.verification_token in (None, ""), "verification_token should be cleared after verification"

    response = await async_client.get("/verify-email?token=invalidtoken")
    assert response.status_code == 400, f"expected 400 for invalid token, got {response.status_code}"


@pytest.mark.asyncio
async def test_login_and_userinfo(async_client):
    response = await async_client.post(
        "/token", data={"username": "testuser", "password": "StrongPass123!"}
    )
    assert response.status_code == 200, f"login failed: {response.status_code} - {response.text}"
    body = response.json()
    assert "access_token" in body, f"no access_token in login response: {body}"
    token = body["access_token"]
    assert JWT_RE.match(token), f"access_token does not look like a JWT: {token}"

    # Acceder a /users/me con el token obtenido
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200, f"/users/me failed: {response.status_code} - {response.text}"
    data = response.json()
    assert data.get("username") == "testuser", f"expected username testuser, got {data}"
    assert "hashed_password" not in data, "hashed_password must not be returned by /users/me"
