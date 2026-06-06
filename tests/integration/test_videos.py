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
