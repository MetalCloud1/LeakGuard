# tests/test_password_checker.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from password_checker_service import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("password_checker_service.main.decode_token_return_username")
def test_check_password_valid_token(mock_decode):
    mock_decode.return_value = "testuser"
    
    data = {"password": "123456"}  
    response = client.post("/check-password", json=data, headers={"Authorization": "Bearer dummy"})
    
    assert response.status_code == 200
    json_resp = response.json()
    assert "leaked" in json_resp
    assert "times" in json_resp
    assert isinstance(json_resp["leaked"], bool)
    assert isinstance(json_resp["times"], int)

@patch("password_checker_service.main.decode_token_return_username")
def test_check_password_invalid_token(mock_decode):
    mock_decode.return_value = None
    
    data = {"password": "123456"}
    response = client.post("/check-password", json=data, headers={"Authorization": "Bearer dummy"})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
