import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
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


def test_create_video_record_status_pendente(db):
    from app.services.video_service import create_video_record
    video = create_video_record(db, "clip.mp4", "storage/videos/clip.mp4")
    assert video.id is not None
    assert video.status == VideoStatus.PENDENTE
    assert video.file_name == "clip.mp4"


def test_get_video_by_id_returns_none_for_missing(db):
    from app.services.video_service import get_video_by_id
    result = get_video_by_id(db, 9999)
    assert result is None


def test_get_video_by_id_returns_video(db):
    from app.services.video_service import create_video_record, get_video_by_id
    created = create_video_record(db, "a.mp4", "storage/videos/a.mp4")
    found = get_video_by_id(db, created.id)
    assert found is not None
    assert found.id == created.id


def test_list_videos_empty(db):
    from app.services.video_service import list_videos
    result = list_videos(db)
    assert result == []


def test_list_videos_respects_limit(db):
    from app.services.video_service import create_video_record, list_videos
    for i in range(5):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")
    result = list_videos(db, skip=0, limit=3)
    assert len(result) == 3


def test_list_videos_respects_skip(db):
    from app.services.video_service import create_video_record, list_videos
    for i in range(4):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")
    result = list_videos(db, skip=2, limit=10)
    assert len(result) == 2


def test_update_video_status_changes_correctly(db):
    from app.services.video_service import create_video_record, update_video_status
    video = create_video_record(db, "b.mp4", "storage/videos/b.mp4")
    updated = update_video_status(db, video.id, VideoStatus.CONCLUIDO)
    assert updated is not None
    assert updated.status == VideoStatus.CONCLUIDO


def test_update_video_status_returns_none_for_missing(db):
    from app.services.video_service import update_video_status
    result = update_video_status(db, 9999, VideoStatus.ERRO)
    assert result is None


# ── get_video_detail ─────────────────────────────────────────────────────────

def _make_person(db, name="Fulano", category="Visitante", profile_image_path="fulano.jpg"):
    from app.models.person import Person
    person = Person(name=name, category=category, profile_image_path=profile_image_path)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def _make_appearance(db, person_id, video_id, start, end, confidence=0.3):
    from app.models.appearance import Appearance
    appearance = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=start,
        timestamp_end=end,
        confidence=confidence,
    )
    db.add(appearance)
    db.commit()
    db.refresh(appearance)
    return appearance


def test_get_video_detail_returns_none_for_missing_video(db):
    from app.services.video_service import get_video_detail
    assert get_video_detail(db, 9999) is None


def test_get_video_detail_returns_dict_with_expected_keys(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    detail = get_video_detail(db, video.id)
    assert detail is not None
    assert set(detail.keys()) == {"video", "people", "summary"}
    assert detail["video"]["id"] == video.id


def test_get_video_detail_video_without_appearances(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    detail = get_video_detail(db, video.id)
    assert detail["people"] == []
    assert detail["summary"]["total_people"] == 0
    assert detail["summary"]["total_appearances"] == 0
    assert detail["summary"]["duration_covered"] == 0
    assert detail["summary"]["processing_status"] == video.status.value


def test_get_video_detail_orders_people_by_first_seen_at_asc(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person_a = _make_person(db, name="A")
    person_b = _make_person(db, name="B")
    _make_appearance(db, person_b.id, video.id, start=5.0, end=6.0)
    _make_appearance(db, person_a.id, video.id, start=1.0, end=2.0)

    detail = get_video_detail(db, video.id)
    names = [p["person_name"] for p in detail["people"]]
    assert names == ["A", "B"]


def test_get_video_detail_total_seconds_ignores_open_ended_appearances(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person = _make_person(db)
    _make_appearance(db, person.id, video.id, start=1.0, end=3.0)
    _make_appearance(db, person.id, video.id, start=10.0, end=None)

    detail = get_video_detail(db, video.id)
    p = detail["people"][0]
    assert p["total_seconds"] == 2.0
    assert p["appearance_count"] == 2
    assert p["first_seen_at"] == 1.0
    assert p["last_seen_at"] == 10.0


def test_get_video_detail_appearance_count_scoped_to_video(db):
    from app.services.video_service import create_video_record, get_video_detail
    video1 = create_video_record(db, "v1.mp4", "storage/videos/v1.mp4")
    video2 = create_video_record(db, "v2.mp4", "storage/videos/v2.mp4")
    person = _make_person(db)
    _make_appearance(db, person.id, video1.id, start=1.0, end=2.0)
    _make_appearance(db, person.id, video2.id, start=1.0, end=2.0)
    _make_appearance(db, person.id, video2.id, start=3.0, end=4.0)

    detail = get_video_detail(db, video1.id)
    assert len(detail["people"]) == 1
    assert detail["people"][0]["appearance_count"] == 1


def test_get_video_detail_summary_counts_distinct_people(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person_a = _make_person(db, name="A")
    person_b = _make_person(db, name="B")
    _make_appearance(db, person_a.id, video.id, start=1.0, end=2.0)
    _make_appearance(db, person_a.id, video.id, start=3.0, end=4.0)
    _make_appearance(db, person_b.id, video.id, start=5.0, end=6.0)

    detail = get_video_detail(db, video.id)
    assert detail["summary"]["total_people"] == 2
    assert detail["summary"]["total_appearances"] == 3
    assert detail["summary"]["duration_covered"] == 3.0
