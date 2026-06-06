from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import sessionmaker

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video, VideoStatus


def seed_export_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    person = Person(name="Teste Export", category="Visitante")
    session.add(person)
    video = Video(
        file_name="export.mp4",
        file_path="storage/videos/export.mp4",
        status=VideoStatus.CONCLUIDO,
        uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    session.add(video)
    session.commit()
    session.refresh(person)
    session.refresh(video)
    app = Appearance(
        person_id=person.id,
        video_id=video.id,
        timestamp_start=0.0,
        timestamp_end=5.0,
        confidence=0.35,
    )
    session.add(app)
    session.commit()
    pid = person.id
    vid = video.id
    session.close()
    return pid, vid


@pytest.mark.asyncio
async def test_export_timeline_requires_auth(client):
    response = await client.get("/api/v1/export/timeline")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_timeline_returns_csv_content_type(client, auth_headers):
    response = await client.get("/api/v1/export/timeline", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_timeline_returns_content_disposition(client, auth_headers):
    response = await client.get("/api/v1/export/timeline", headers=auth_headers)
    assert "content-disposition" in response.headers
    assert "attachment" in response.headers["content-disposition"]
    assert ".csv" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_export_timeline_person_not_found(client, auth_headers):
    response = await client.get("/api/v1/export/timeline?person_id=9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_timeline_video_not_found(client, auth_headers):
    response = await client.get("/api/v1/export/timeline?video_id=9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_timeline_both_params_returns_400(client, auth_headers, test_engine):
    pid, vid = seed_export_data(test_engine)
    response = await client.get(
        f"/api/v1/export/timeline?person_id={pid}&video_id={vid}",
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_timeline_person_shortcut(client, auth_headers, test_engine):
    pid, _ = seed_export_data(test_engine)
    response = await client.get(f"/api/v1/export/timeline/person/{pid}", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Teste Export" in response.text


@pytest.mark.asyncio
async def test_export_timeline_video_shortcut(client, auth_headers, test_engine):
    _, vid = seed_export_data(test_engine)
    response = await client.get(f"/api/v1/export/timeline/video/{vid}", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "export.mp4" in response.text
