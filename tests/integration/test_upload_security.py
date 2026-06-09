from io import BytesIO
from unittest.mock import patch

import pytest


def make_mp4_bytes(extra: bytes = b"") -> bytes:
    """Mínimo válido: ftyp em bytes 4-7."""
    return b"\x00\x00\x00\x18" + b"ftyp" + b"isom" + b"\x00" * 4 + extra


def make_avi_bytes(extra: bytes = b"") -> bytes:
    """Mínimo válido: RIFF...AVI ."""
    return b"RIFF" + b"\x00\x00\x00\x04" + b"AVI " + extra


def make_txt_as_mp4() -> bytes:
    """Conteúdo de texto com extensão .mp4 — magic bytes inválidos."""
    return b"Isso e texto puro, nao e video"


@pytest.mark.asyncio
async def test_path_traversal_filename_saved_as_uuid(client, auth_headers, tmp_path):
    """../../../etc/passwd.mp4 deve ser salvo com nome UUID, sem path traversal."""
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("../../../etc/passwd.mp4", BytesIO(make_mp4_bytes()), "video/mp4")},
            headers=auth_headers,
        )
    assert response.status_code == 202
    saved = list(tmp_path.iterdir())
    assert len(saved) == 1
    assert ".." not in saved[0].name
    assert "passwd" not in saved[0].name
    assert "etc" not in saved[0].name


@pytest.mark.asyncio
async def test_path_never_contains_original_filename(client, auth_headers, tmp_path):
    """Path em disco nunca deve conter o filename original do cliente."""
    original = "meu_video_especial.mp4"
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        await client.post(
            "/api/v1/videos/upload",
            files={"file": (original, BytesIO(make_mp4_bytes()), "video/mp4")},
            headers=auth_headers,
        )
    saved = list(tmp_path.iterdir())
    assert len(saved) == 1
    assert original not in saved[0].name


@pytest.mark.asyncio
async def test_txt_as_mp4_returns_415(client, auth_headers, tmp_path):
    """Arquivo .txt renomeado para .mp4 deve retornar 415."""
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("malware.mp4", BytesIO(make_txt_as_mp4()), "video/mp4")},
            headers=auth_headers,
        )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_valid_mp4_magic_bytes_returns_202(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("real.mp4", BytesIO(make_mp4_bytes()), "video/mp4")},
            headers=auth_headers,
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_valid_avi_magic_bytes_returns_202(client, auth_headers, tmp_path):
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("real.avi", BytesIO(make_avi_bytes()), "video/x-msvideo")},
            headers=auth_headers,
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_oversized_upload_returns_413(client, auth_headers, tmp_path):
    """Upload acima do MAX_UPLOAD_SIZE deve retornar 413."""
    small_limit = 10  # 10 bytes
    big_data = make_mp4_bytes(b"X" * 50)
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = small_limit
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("big.mp4", BytesIO(big_data), "video/mp4")},
            headers=auth_headers,
        )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_conversion_failure_returns_422_not_500(client, auth_headers, tmp_path):
    """Falha na conversão (disco cheio, ffmpeg erro) deve retornar 422, não 500."""
    import subprocess
    dav_bytes = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b"
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.needs_conversion", return_value=True), \
         patch("app.api.v1.upload.convert_to_mp4",
               side_effect=subprocess.CalledProcessError(
                   228, "ffmpeg", stderr=b"No space left on device")):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("camera.dav", BytesIO(dav_bytes), "application/octet-stream")},
            headers=auth_headers,
        )
    assert response.status_code == 422
    assert "converter" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_valid_dav_returns_202(client, auth_headers, tmp_path):
    """.dav de câmera Dahua deve ser aceito sem validação de magic bytes."""
    dav_bytes = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b"  # bytes arbitrários
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"), \
         patch("app.api.v1.upload.needs_conversion", return_value=False):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("camera.dav", BytesIO(dav_bytes), "application/octet-stream")},
            headers=auth_headers,
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_partial_file_deleted_on_413(client, auth_headers, tmp_path):
    """Arquivo parcial deve ser deletado quando upload excede o limite."""
    small_limit = 10
    big_data = make_mp4_bytes(b"X" * 50)
    with patch("app.api.v1.upload.settings") as ms, \
         patch("app.api.v1.upload.process_video"):
        ms.STORAGE_VIDEOS = tmp_path
        ms.MAX_UPLOAD_SIZE_BYTES = small_limit
        await client.post(
            "/api/v1/videos/upload",
            files={"file": ("big.mp4", BytesIO(big_data), "video/mp4")},
            headers=auth_headers,
        )
    assert list(tmp_path.iterdir()) == []
