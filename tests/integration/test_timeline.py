import pytest
from sqlalchemy.orm import sessionmaker

from app.models.person import Person
from app.models.video import Video, VideoStatus
from app.models.appearance import Appearance


def seed_timeline_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    person = Person(name="Desconhecido #1")
    video = Video(file_name="clip.mp4", file_path="storage/videos/clip.mp4", status=VideoStatus.CONCLUIDO)
    session.add_all([person, video])
    session.commit()
    session.refresh(person)
    session.refresh(video)

    app1 = Appearance(person_id=person.id, video_id=video.id, timestamp_start=0.0, timestamp_end=5.0, confidence=0.3)
    app2 = Appearance(person_id=person.id, video_id=video.id, timestamp_start=10.0, timestamp_end=15.0, confidence=0.25)
    session.add_all([app1, app2])
    session.commit()

    pid = person.id
    fname = video.file_name
    session.close()
    return pid, fname


def seed_person_only(engine) -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    person = Person(name="Sem aparições")
    session.add(person)
    session.commit()
    pid = person.id
    session.close()
    return pid


@pytest.mark.asyncio
async def test_timeline_person_not_found(client, auth_headers):
    response = await client.get("/api/v1/people/9999/timeline", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_timeline_empty_for_person_without_appearances(client, auth_headers, test_engine):
    pid = seed_person_only(test_engine)
    response = await client.get(f"/api/v1/people/{pid}/timeline", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_timeline_returns_appearances_sorted(client, auth_headers, test_engine):
    pid, _ = seed_timeline_data(test_engine)
    response = await client.get(f"/api/v1/people/{pid}/timeline", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["timestamp_start"] == 0.0
    assert data[1]["timestamp_start"] == 10.0


@pytest.mark.asyncio
async def test_timeline_includes_file_name(client, auth_headers, test_engine):
    pid, file_name = seed_timeline_data(test_engine)
    response = await client.get(f"/api/v1/people/{pid}/timeline", headers=auth_headers)
    data = response.json()
    assert data[0]["file_name"] == file_name
