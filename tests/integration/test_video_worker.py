from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.video import Video, VideoStatus


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # uma conexão única compartilhada entre sessions
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def video_in_db(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    video = Video(
        file_name="test.mp4",
        file_path="storage/videos/test.mp4",
        status=VideoStatus.PENDENTE,
    )
    session.add(video)
    session.commit()
    session.refresh(video)
    video_id = video.id
    session.close()
    return db_engine, video_id


def get_video_status(engine, video_id: int) -> VideoStatus:
    Session = sessionmaker(bind=engine)
    session = Session()
    video = session.get(Video, video_id)
    status = video.status
    session.close()
    return status


# ── status transitions ────────────────────────────────────────────────────────

def test_status_changes_to_processando_then_concluido(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db

    with patch("app.workers.video_worker.frame_service.extract_frames", return_value=iter([])), \
         patch("app.workers.video_worker.person_service.get_all_embeddings", return_value=[]):
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert get_video_status(engine, video_id) == VideoStatus.CONCLUIDO


def test_status_changes_to_erro_on_exception(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db

    with patch("app.workers.video_worker.frame_service.extract_frames",
               side_effect=RuntimeError("boom")):
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert get_video_status(engine, video_id) == VideoStatus.ERRO


# ── face new → save_new_person ────────────────────────────────────────────────

def test_new_face_calls_save_new_person(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=iter([(0, fake_frame)])), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[embedding]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person") as mock_save:
        mock_save.return_value = MagicMock(id=99)
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_save.assert_called_once()


# ── face known → upsert_appearance ───────────────────────────────────────────

def test_known_face_calls_upsert_appearance(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=iter([(2, fake_frame)])), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[embedding]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(7, embedding)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(7, 0.3)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance") as mock_upsert:
        mock_upsert.return_value = MagicMock()
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_upsert.assert_called_once()
    args, kwargs = mock_upsert.call_args
    person_id_arg = kwargs.get("person_id") or args[1]
    assert person_id_arg == 7
