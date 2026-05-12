import os

from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test-super-long-secret-key-for-jwt-signing-123456"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"

from app.main import ACCESS_TOKEN_EXPIRE_SECONDS, app

client = TestClient(app)


def test_create_token_success() -> None:
    response = client.post("/token", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == ACCESS_TOKEN_EXPIRE_SECONDS
    assert "access_token" in body
    assert "refresh_token" in body


def test_create_token_rejects_invalid_credentials() -> None:
    response = client.post("/token", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_token_success() -> None:
    token_response = client.post("/token", json={"username": "admin", "password": "admin123"})
    original_body = token_response.json()
    refresh_token = original_body["refresh_token"]

    refresh_response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == ACCESS_TOKEN_EXPIRE_SECONDS
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["refresh_token"] != refresh_token
