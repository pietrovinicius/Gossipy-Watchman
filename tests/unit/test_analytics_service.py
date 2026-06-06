from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Person, Video
from app.models.appearance import Appearance
from app.models.video import VideoStatus


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _add_video(db, name="v.mp4", days_ago=0) -> Video:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    v = Video(file_name=name, file_path=f"storage/videos/{name}",
              status=VideoStatus.CONCLUIDO, uploaded_at=dt)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _add_person(db, name="P") -> Person:
    p = Person(name=name, profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _add_appearance(db, person_id, video_id, ts=0.0, te=5.0):
    a = Appearance(person_id=person_id, video_id=video_id,
                   timestamp_start=ts, timestamp_end=te, confidence=0.2)
    db.add(a)
    db.commit()


def test_get_overview_retorna_contagens_corretas(db):
    from app.services.analytics_service import get_overview
    _add_video(db, "v1.mp4")
    _add_video(db, "v2.mp4")
    p = _add_person(db)
    result = get_overview(db)
    assert result["total_videos"] == 2
    assert result["total_people"] == 1


def test_get_overview_sem_dados_retorna_zeros(db):
    from app.services.analytics_service import get_overview
    result = get_overview(db)
    assert result["total_videos"] == 0
    assert result["total_people"] == 0
    assert result["total_appearances"] == 0


def test_get_appearances_per_video_retorna_lista(db):
    from app.services.analytics_service import get_appearances_per_video
    v = _add_video(db)
    p = _add_person(db)
    _add_appearance(db, p.id, v.id)
    _add_appearance(db, p.id, v.id, ts=10.0, te=15.0)
    result = get_appearances_per_video(db)
    assert len(result) >= 1
    entry = next((r for r in result if r["video_id"] == v.id), None)
    assert entry is not None
    assert entry["count"] == 2


def test_get_top_people_retorna_ordenado_por_aparicoes(db):
    from app.services.analytics_service import get_top_people
    v1 = _add_video(db, "v1.mp4")
    v2 = _add_video(db, "v2.mp4")
    p1 = _add_person(db, "Alice")
    p2 = _add_person(db, "Bob")
    _add_appearance(db, p1.id, v1.id)
    _add_appearance(db, p1.id, v2.id)
    _add_appearance(db, p2.id, v1.id)
    result = get_top_people(db, limit=5)
    assert result[0]["person_id"] == p1.id
    assert result[0]["appearance_count"] == 2
    assert result[1]["person_id"] == p2.id


def test_get_activity_timeline_retorna_contagens_por_data(db):
    from app.services.analytics_service import get_activity_timeline
    _add_video(db, "v1.mp4", days_ago=0)
    _add_video(db, "v2.mp4", days_ago=0)
    _add_video(db, "v3.mp4", days_ago=3)
    result = get_activity_timeline(db, days=7)
    assert isinstance(result, list)
    today_entries = [r for r in result if r["count"] == 2]
    assert len(today_entries) >= 1
