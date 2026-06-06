from io import BytesIO
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest


@pytest.mark.asyncio
async def test_upload_mp4_returns_202(client, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_avi_returns_202(client, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("video.avi", BytesIO(b"fake"), "video/x-msvideo")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_pdf_returns_400(client):
    response = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("doc.pdf", BytesIO(b"fake"), "application/pdf")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_exe_returns_400(client):
    response = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("evil.exe", BytesIO(b"fake"), "application/octet-stream")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_saves_file_to_disk(client, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"video-content"), "video/mp4")},
        )
    saved_files = list(tmp_path.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"video-content"


@pytest.mark.asyncio
async def test_upload_dispatches_process_video(client, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video") as mock_pv:
        ms.STORAGE_VIDEOS = tmp_path
        await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
        )
    mock_pv.assert_called_once()


@pytest.mark.asyncio
async def test_upload_returns_status_pendente(client, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("clip.mp4", BytesIO(b"fake"), "video/mp4")},
        )
    data = response.json()
    assert data["status"] == "Pendente"
    assert "id" in data
    assert "uploaded_at" in data
