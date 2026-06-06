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
