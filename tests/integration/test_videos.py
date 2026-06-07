import pytest
from sqlalchemy.orm import sessionmaker

from app.models.video import Video, VideoStatus


def seed_video(engine, file_name: str = "test.mp4") -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    video = Video(file_name=file_name, file_path=f"storage/videos/{file_name}", status=VideoStatus.PENDENTE)
    session.add(video)
    session.commit()
    session.refresh(video)
    vid_id = video.id
    session.close()
    return vid_id


@pytest.mark.asyncio
async def test_list_videos_empty(client, auth_headers):
    response = await client.get("/api/v1/videos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_videos_returns_existing(client, auth_headers, test_engine):
    seed_video(test_engine, "clip1.mp4")
    seed_video(test_engine, "clip2.mp4")
    response = await client.get("/api/v1/videos", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_video_returns_correct(client, auth_headers, test_engine):
    vid_id = seed_video(test_engine, "solo.mp4")
    response = await client.get(f"/api/v1/videos/{vid_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == vid_id
    assert data["file_name"] == "solo.mp4"


@pytest.mark.asyncio
async def test_get_video_not_found(client, auth_headers):
    response = await client.get("/api/v1/videos/9999", headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_video_status_returns_fields(client, auth_headers, test_engine):
    vid_id = seed_video(test_engine)
    response = await client.get(f"/api/v1/videos/{vid_id}/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"id", "status", "uploaded_at"}
    assert data["status"] == "Pendente"


@pytest.mark.asyncio
async def test_get_video_status_not_found(client, auth_headers):
    response = await client.get("/api/v1/videos/9999/status", headers=auth_headers)
    assert response.status_code == 404


def seed_appearance(engine, person_id: int, video_id: int, start: float, end: float | None, confidence: float = 0.3) -> int:
    from app.models.appearance import Appearance
    Session = sessionmaker(bind=engine)
    session = Session()
    appearance = Appearance(
        person_id=person_id, video_id=video_id,
        timestamp_start=start, timestamp_end=end, confidence=confidence,
    )
    session.add(appearance)
    session.commit()
    session.refresh(appearance)
    app_id = appearance.id
    session.close()
    return app_id


def seed_person(engine, name: str = "Fulano", category: str = "Visitante") -> int:
    from app.models.person import Person
    Session = sessionmaker(bind=engine)
    session = Session()
    person = Person(name=name, category=category, profile_image_path="fulano.jpg")
    session.add(person)
    session.commit()
    session.refresh(person)
    person_id = person.id
    session.close()
    return person_id


@pytest.mark.asyncio
async def test_get_video_detail_requires_auth(client, test_engine):
    vid_id = seed_video(test_engine, "noauth.mp4")
    response = await client.get(f"/api/v1/videos/{vid_id}/detail")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_video_detail_not_found(client, auth_headers):
    response = await client.get("/api/v1/videos/9999/detail", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_video_detail_returns_structure(client, auth_headers, test_engine):
    vid_id = seed_video(test_engine, "detail.mp4")
    person_id = seed_person(test_engine, "Ciclano")
    seed_appearance(test_engine, person_id, vid_id, start=1.0, end=3.0)

    response = await client.get(f"/api/v1/videos/{vid_id}/detail", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"video", "people", "summary"}
    assert data["video"]["id"] == vid_id
    assert data["summary"]["total_people"] == 1


@pytest.mark.asyncio
async def test_get_video_detail_people_have_required_fields(client, auth_headers, test_engine):
    vid_id = seed_video(test_engine, "detail2.mp4")
    person_id = seed_person(test_engine, "Beltrano")
    seed_appearance(test_engine, person_id, vid_id, start=1.0, end=3.0)

    response = await client.get(f"/api/v1/videos/{vid_id}/detail", headers=auth_headers)
    person = response.json()["people"][0]
    assert person["person_id"] == person_id
    assert person["person_name"] == "Beltrano"
    assert "appearances" in person
    assert person["appearances"][0]["confidence"] == pytest.approx(0.3)


# ── soft delete / restore / reprocess / filtros ───────────────────────────────

@pytest.mark.asyncio
async def test_delete_video_without_token_returns_401(client, test_engine):
    vid = seed_video(test_engine, "sem_token.mp4")
    response = await client.delete(f"/api/v1/videos/{vid}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_video_returns_200_with_deleted_at(client, auth_headers, test_engine):
    vid = seed_video(test_engine, "para_excluir.mp4")
    response = await client.delete(f"/api/v1/videos/{vid}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == vid
    assert data["deleted_at"] is not None


@pytest.mark.asyncio
async def test_delete_video_unknown_id_returns_404(client, auth_headers):
    response = await client.delete("/api/v1/videos/9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_restore_video_resets_deleted_at(client, auth_headers, test_engine):
    vid = seed_video(test_engine, "para_restaurar.mp4")
    await client.delete(f"/api/v1/videos/{vid}", headers=auth_headers)

    response = await client.post(f"/api/v1/videos/{vid}/restore", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["deleted_at"] is None


@pytest.mark.asyncio
async def test_list_videos_excludes_deleted_by_default(client, auth_headers, test_engine):
    v1 = seed_video(test_engine, "ativo.mp4")
    v2 = seed_video(test_engine, "removido.mp4")
    await client.delete(f"/api/v1/videos/{v2}", headers=auth_headers)

    response = await client.get("/api/v1/videos", headers=auth_headers)
    ids = [item["id"] for item in response.json()]
    assert v1 in ids
    assert v2 not in ids


@pytest.mark.asyncio
async def test_list_videos_include_deleted_true_returns_all(client, auth_headers, test_engine):
    v1 = seed_video(test_engine, "ativo.mp4")
    v2 = seed_video(test_engine, "removido.mp4")
    await client.delete(f"/api/v1/videos/{v2}", headers=auth_headers)

    response = await client.get("/api/v1/videos?include_deleted=true", headers=auth_headers)
    ids = [item["id"] for item in response.json()]
    assert v1 in ids
    assert v2 in ids


@pytest.mark.asyncio
async def test_list_videos_filters_by_status(client, auth_headers, test_engine):
    from sqlalchemy.orm import sessionmaker

    v1 = seed_video(test_engine, "pendente.mp4")
    v2 = seed_video(test_engine, "concluido.mp4")
    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, v2)
    video.status = VideoStatus.CONCLUIDO
    session.commit()
    session.close()

    response = await client.get("/api/v1/videos?status=Concluído", headers=auth_headers)
    ids = [item["id"] for item in response.json()]
    assert v2 in ids
    assert v1 not in ids


@pytest.mark.asyncio
async def test_reprocess_video_returns_pendente_status(client, auth_headers, test_engine, tmp_path, monkeypatch):
    from sqlalchemy.orm import sessionmaker
    from unittest.mock import MagicMock

    monkeypatch.setattr("app.api.v1.videos.process_video", MagicMock())

    file_path = tmp_path / "reprocessar.mp4"
    file_path.write_bytes(b"x")
    vid = seed_video(test_engine, "reprocessar.mp4")
    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, vid)
    video.file_path = str(file_path)
    video.status = VideoStatus.ERRO
    session.commit()
    session.close()

    response = await client.post(f"/api/v1/videos/{vid}/reprocess", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Pendente"


@pytest.mark.asyncio
async def test_reprocess_video_missing_file_returns_409(client, auth_headers, test_engine):
    vid = seed_video(test_engine, "sem_arquivo.mp4")
    response = await client.post(f"/api/v1/videos/{vid}/reprocess", headers=auth_headers)
    assert response.status_code == 409


# ── GET /videos/catalog ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_catalog_without_token_returns_401(client):
    response = await client.get("/api/v1/videos/catalog")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_catalog_returns_correct_structure(client, auth_headers, test_engine):
    seed_video(test_engine, "clip1.mp4")
    seed_video(test_engine, "clip2.mp4")
    response = await client.get("/api/v1/videos/catalog", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"items", "total", "page", "page_size", "total_pages", "has_next", "has_prev"}
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_catalog_query_filters_by_name(client, auth_headers, test_engine):
    seed_video(test_engine, "aniversario_2024.mp4")
    seed_video(test_engine, "reuniao.mp4")
    response = await client.get("/api/v1/videos/catalog?q=aniversario", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["file_name"] == "aniversario_2024.mp4"


@pytest.mark.asyncio
async def test_catalog_status_filter(client, auth_headers, test_engine):
    from sqlalchemy.orm import sessionmaker

    v1 = seed_video(test_engine, "pendente.mp4")
    v2 = seed_video(test_engine, "concluido.mp4")
    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, v2)
    video.status = VideoStatus.CONCLUIDO
    session.commit()
    session.close()

    response = await client.get("/api/v1/videos/catalog?status=Concluído", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == v2


@pytest.mark.asyncio
async def test_catalog_pagination(client, auth_headers, test_engine):
    for i in range(15):
        seed_video(test_engine, f"video{i}.mp4")

    response = await client.get("/api/v1/videos/catalog?page=1&page_size=5", headers=auth_headers)
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) == 5
    assert data["has_next"] is True
    assert data["has_prev"] is False

    response2 = await client.get("/api/v1/videos/catalog?page=2&page_size=5", headers=auth_headers)
    data2 = response2.json()
    assert data2["page"] == 2
    assert data2["has_prev"] is True


@pytest.mark.asyncio
async def test_catalog_excludes_deleted_by_default(client, auth_headers, test_engine):
    v1 = seed_video(test_engine, "ativo.mp4")
    v2 = seed_video(test_engine, "deletado.mp4")
    await client.delete(f"/api/v1/videos/{v2}", headers=auth_headers)

    response = await client.get("/api/v1/videos/catalog", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    ids = [item["id"] for item in data["items"]]
    assert v1 in ids
    assert v2 not in ids


# ── GET /videos/{id}/stream (streaming com Range requests) ────────────────────

@pytest.mark.asyncio
async def test_stream_without_token_returns_401(client, test_engine):
    vid = seed_video(test_engine, "stream.mp4")
    response = await client.get(f"/api/v1/videos/{vid}/stream")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_invalid_token_returns_401(client, test_engine):
    vid = seed_video(test_engine, "stream.mp4")
    response = await client.get(f"/api/v1/videos/{vid}/stream?token=invalid_token_xyz")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_nonexistent_video_returns_404(client, auth_headers):
    token = auth_headers['Authorization'].replace('Bearer ', '')
    response = await client.get(f"/api/v1/videos/9999/stream?token={token}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stream_with_deleted_video_returns_410(client, auth_headers, test_engine):
    vid = seed_video(test_engine, "deleted_video.mp4")
    await client.delete(f"/api/v1/videos/{vid}", headers=auth_headers)
    token = auth_headers['Authorization'].replace('Bearer ', '')
    response = await client.get(f"/api/v1/videos/{vid}/stream?token={token}")
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_stream_without_range_returns_200_with_accept_ranges(client, auth_headers, test_engine, tmp_path):
    file_path = tmp_path / "stream.mp4"
    file_path.write_bytes(b"x" * 1000)
    vid = seed_video(test_engine, "stream.mp4")

    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, vid)
    video.file_path = str(file_path)
    session.commit()
    session.close()

    token = auth_headers['Authorization'].replace('Bearer ', '')
    response = await client.get(f"/api/v1/videos/{vid}/stream?token={token}")
    assert response.status_code == 200
    assert response.headers.get("Accept-Ranges") == "bytes"


@pytest.mark.asyncio
async def test_stream_with_range_returns_206(client, auth_headers, test_engine, tmp_path):
    file_path = tmp_path / "stream.mp4"
    file_path.write_bytes(b"x" * 1000)
    vid = seed_video(test_engine, "stream.mp4")

    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, vid)
    video.file_path = str(file_path)
    session.commit()
    session.close()

    token = auth_headers['Authorization'].replace('Bearer ', '')
    headers = {"Range": "bytes=0-99"}
    response = await client.get(f"/api/v1/videos/{vid}/stream?token={token}", headers=headers)
    assert response.status_code == 206
    assert "Content-Range" in response.headers
    assert response.headers.get("Content-Range") == "bytes 0-99/1000"


@pytest.mark.asyncio
async def test_stream_range_partial_returns_correct_length(client, auth_headers, test_engine, tmp_path):
    file_path = tmp_path / "stream.mp4"
    file_path.write_bytes(b"x" * 1000)
    vid = seed_video(test_engine, "stream.mp4")

    Session = sessionmaker(bind=test_engine)
    session = Session()
    video = session.get(Video, vid)
    video.file_path = str(file_path)
    session.commit()
    session.close()

    token = auth_headers['Authorization'].replace('Bearer ', '')
    headers = {"Range": "bytes=100-199"}
    response = await client.get(f"/api/v1/videos/{vid}/stream?token={token}", headers=headers)
    assert response.status_code == 206
    assert int(response.headers.get("Content-Length")) == 100
