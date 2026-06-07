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
