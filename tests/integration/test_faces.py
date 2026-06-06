import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.mark.asyncio
async def test_faces_without_token_returns_401(client):
    response = await client.get("/api/v1/faces/1.jpg")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_faces_path_traversal_dotdot_returns_400(client, auth_headers):
    response = await client.get("/api/v1/faces/../settings.py", headers=auth_headers)
    assert response.status_code in (400, 404)


@pytest.mark.asyncio
async def test_faces_percent_encoded_traversal_returns_400(client, auth_headers):
    response = await client.get("/api/v1/faces/%2e%2e%2fsettings.py", headers=auth_headers)
    assert response.status_code in (400, 404)


@pytest.mark.asyncio
async def test_faces_nonexistent_returns_404(client, auth_headers, tmp_path):
    with patch("app.api.v1.faces.settings") as ms:
        ms.STORAGE_FACES = tmp_path
        response = await client.get("/api/v1/faces/inexistente.jpg", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_faces_existing_file_returns_200(client, auth_headers, tmp_path):
    img_path = tmp_path / "1.jpg"
    img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 10)  # JPEG magic
    with patch("app.api.v1.faces.settings") as ms:
        ms.STORAGE_FACES = tmp_path
        response = await client.get("/api/v1/faces/1.jpg", headers=auth_headers)
    assert response.status_code == 200
