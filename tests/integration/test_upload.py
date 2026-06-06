from io import BytesIO
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_upload_mp4_returns_202(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
            headers=auth_headers,
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_avi_returns_202(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("video.avi", BytesIO(b"fake"), "video/x-msvideo")},
            headers=auth_headers,
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_pdf_returns_400(client, auth_headers):
    response = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("doc.pdf", BytesIO(b"fake"), "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_exe_returns_400(client, auth_headers):
    response = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("evil.exe", BytesIO(b"fake"), "application/octet-stream")},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_saves_file_to_disk(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"video-content"), "video/mp4")},
            headers=auth_headers,
        )
    saved_files = list(tmp_path.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"video-content"


@pytest.mark.asyncio
async def test_upload_dispatches_process_video(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video") as mock_pv:
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
            headers=auth_headers,
        )
    mock_pv.assert_called_once()


@pytest.mark.asyncio
async def test_upload_returns_status_pendente(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
            headers=auth_headers,
        )
    data = response.json()
    assert data["status"] == "Pendente"
    assert "id" in data
    assert "uploaded_at" in data
