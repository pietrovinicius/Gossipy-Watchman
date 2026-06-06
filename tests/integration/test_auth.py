import pytest
from jose import jwt


@pytest.mark.asyncio
async def test_login_valid_returns_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "watchman"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "errado"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_videos_without_token_returns_401(client):
    response = await client.get("/api/v1/videos")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_videos_with_valid_token_returns_200(client):
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "watchman"},
    )
    token = login.json()["access_token"]
    response = await client.get(
        "/api/v1/videos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_token_signature_returns_401(client):
    response = await client.get(
        "/api/v1/videos",
        headers={"Authorization": "Bearer token.invalido.assinatura"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_without_token_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
