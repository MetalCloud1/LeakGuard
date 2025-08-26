import os
from fastapi.testclient import TestClient
from unittest.mock import patch

from password_checker_service.src_pcs.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("password_checker_service.src_pcs.app.decode_token_return_username")
@patch("password_checker_service.src_pcs.app.check_password_hibp")
def test_check_password_with_hibp(mock_hibp, mock_decode):
    mock_decode.return_value = "testuser"
    mock_hibp.return_value = 1000000

    data = {"password": "123456"}
    response = client.post(
        "/check-password",
        json=data,
        headers={"Authorization": "Bearer dummy"}
    )

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["leaked"] is True
    assert json_resp["times"] == 1000000


@patch("password_checker_service.src_pcs.app.decode_token_return_username")
def test_check_password_invalid_token(mock_decode):
    mock_decode.return_value = None

    data = {"password": "123456"}
    response = client.post(
        "/check-password",
        json=data,
        headers={"Authorization": "Bearer dummy"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


from unittest.mock import patch

@patch("password_checker_service.src_pcs.app.decode_token_return_username")
@patch("password_checker_service.src_pcs.app.USE_HIBP", new=False)
def test_check_password_fallback_local(mock_decode):
    mock_decode.return_value = "testuser"

    data = {"password": "123456"}
    response = client.post(
        "/check-password",
        json=data,
        headers={"Authorization": "Bearer dummy"}
    )

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["leaked"] is False
    assert json_resp["times"] == 0
