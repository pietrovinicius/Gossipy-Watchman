from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Person


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


# ── get_all_embeddings ────────────────────────────────────────────────────────

def test_get_all_embeddings_empty_db(db_session):
    from app.services.person_service import get_all_embeddings
    result = get_all_embeddings(db_session)
    assert result == []


def test_get_all_embeddings_ignores_missing_npy(db_session, tmp_path):
    from app.services.person_service import get_all_embeddings

    person = Person(name="Desconhecido #1", profile_image_path=None)
    db_session.add(person)
    db_session.commit()

    # sem arquivo .npy em disco → deve ignorar
    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path  # dir vazio, sem .npy
        result = get_all_embeddings(db_session)

    assert result == []


def test_get_all_embeddings_loads_existing_npy(db_session, tmp_path):
    from app.services.person_service import get_all_embeddings

    person = Person(name="Desconhecido #1", profile_image_path=None)
    db_session.add(person)
    db_session.commit()

    embedding = np.random.rand(128)
    npy_path = tmp_path / f"{person.id}_embedding.npy"
    np.save(str(npy_path), embedding)

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        result = get_all_embeddings(db_session)

    assert len(result) == 1
    assert result[0][0] == person.id
    np.testing.assert_array_almost_equal(result[0][1], embedding)


# ── save_new_person ───────────────────────────────────────────────────────────

def test_save_new_person_name_format(db_session, tmp_path):
    from app.services.person_service import save_new_person

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    embedding = np.random.rand(128)

    with patch("app.services.person_service.cv2.imwrite") as mock_imwrite, \
         patch("app.services.person_service.np.save") as mock_save, \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_imwrite.return_value = True

        person = save_new_person(db_session, embedding, face_crop, person_index=3)

    assert person.name == "Desconhecido #3"


def test_save_new_person_calls_imwrite_with_correct_path(db_session, tmp_path):
    from app.services.person_service import save_new_person

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    embedding = np.random.rand(128)

    with patch("app.services.person_service.cv2.imwrite") as mock_imwrite, \
         patch("app.services.person_service.np.save") as mock_save, \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_imwrite.return_value = True

        person = save_new_person(db_session, embedding, face_crop, person_index=1)

    expected_jpg = str(tmp_path / f"{person.id}.jpg")
    mock_imwrite.assert_called_once_with(expected_jpg, face_crop)


def test_save_new_person_calls_np_save_with_correct_path(db_session, tmp_path):
    from app.services.person_service import save_new_person

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    embedding = np.random.rand(128)

    with patch("app.services.person_service.cv2.imwrite") as mock_imwrite, \
         patch("app.services.person_service.np.save") as mock_save, \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_imwrite.return_value = True

        person = save_new_person(db_session, embedding, face_crop, person_index=1)

    expected_npy = str(tmp_path / f"{person.id}_embedding.npy")
    mock_save.assert_called_once_with(expected_npy, embedding)


# ── update_person_details ─────────────────────────────────────────────────────

def test_update_person_details_updates_name(db_session):
    from app.services.person_service import update_person_details

    person = Person(name="Antigo Nome")
    db_session.add(person)
    db_session.commit()

    updated = update_person_details(db_session, person.id, name="Novo Nome", notes=None, category=None)
    assert updated is not None
    assert updated.name == "Novo Nome"


def test_update_person_details_updates_notes(db_session):
    from app.services.person_service import update_person_details

    person = Person(name="João")
    db_session.add(person)
    db_session.commit()

    updated = update_person_details(db_session, person.id, name=None, notes="Observação", category=None)
    assert updated.notes == "Observação"


def test_update_person_details_updates_category(db_session):
    from app.services.person_service import update_person_details

    person = Person(name="Maria")
    db_session.add(person)
    db_session.commit()

    updated = update_person_details(db_session, person.id, name=None, notes=None, category="Funcionário")
    assert updated.category == "Funcionário"


def test_update_person_details_none_does_not_alter_existing(db_session):
    from app.services.person_service import update_person_details

    person = Person(name="Original", notes="Nota original", category="Visitante")
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)

    updated = update_person_details(db_session, person.id, name=None, notes=None, category=None)
    assert updated.name == "Original"
    assert updated.notes == "Nota original"
    assert updated.category == "Visitante"


def test_update_person_details_returns_none_for_missing(db_session):
    from app.services.person_service import update_person_details

    result = update_person_details(db_session, 9999, name="X", notes=None, category=None)
    assert result is None


# ── get_person_stats ──────────────────────────────────────────────────────────

def test_get_person_stats_zeros_for_no_appearances(db_session):
    from app.services.person_service import get_person_stats

    person = Person(name="Sem Aparições")
    db_session.add(person)
    db_session.commit()

    stats = get_person_stats(db_session, person.id)
    assert stats["video_count"] == 0
    assert stats["total_seconds"] == 0.0
    assert stats["first_seen"] is None
    assert stats["last_seen"] is None


def test_get_person_stats_calculates_total_seconds(db_session):
    from datetime import datetime, timezone
    from app.models.video import Video, VideoStatus
    from app.models.appearance import Appearance
    from app.services.person_service import get_person_stats

    person = Person(name="Com Aparições")
    db_session.add(person)
    video = Video(
        file_name="v.mp4",
        file_path="storage/videos/v.mp4",
        status=VideoStatus.CONCLUIDO,
        uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db_session.add(video)
    db_session.commit()

    app1 = Appearance(person_id=person.id, video_id=video.id, timestamp_start=0.0, timestamp_end=5.0, confidence=0.3)
    app2 = Appearance(person_id=person.id, video_id=video.id, timestamp_start=10.0, timestamp_end=13.0, confidence=0.4)
    db_session.add_all([app1, app2])
    db_session.commit()

    stats = get_person_stats(db_session, person.id)
    assert stats["video_count"] == 1
    assert stats["total_seconds"] == pytest.approx(8.0)
    assert stats["first_seen"] is not None


# ── merge_people ──────────────────────────────────────────────────────────────

def test_merge_people_reassociates_appearances(db_session):
    from app.models.appearance import Appearance
    from app.models.video import Video, VideoStatus
    from app.services.person_service import merge_people
    from datetime import datetime, timezone

    p1 = Person(name="Principal")
    p2 = Person(name="Secundário")
    db_session.add_all([p1, p2])
    video = Video(file_name="v.mp4", file_path="s/v.mp4", status=VideoStatus.CONCLUIDO,
                  uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc))
    db_session.add(video)
    db_session.commit()

    app = Appearance(person_id=p2.id, video_id=video.id, timestamp_start=0.0, timestamp_end=2.0, confidence=0.3)
    db_session.add(app)
    db_session.commit()

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = Path("/tmp/nonexistent_faces")
        result = merge_people(db_session, p1.id, [p2.id])

    reassociated = db_session.query(Appearance).filter_by(person_id=p1.id).all()
    assert len(reassociated) == 1
    assert result.id == p1.id


def test_merge_people_deletes_secondary(db_session):
    from app.services.person_service import merge_people

    p1 = Person(name="Principal")
    p2 = Person(name="Secundário")
    db_session.add_all([p1, p2])
    db_session.commit()

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = Path("/tmp/nonexistent_faces")
        merge_people(db_session, p1.id, [p2.id])

    deleted = db_session.get(Person, p2.id)
    assert deleted is None


def test_merge_people_raises_404_for_unknown_primary(db_session):
    from fastapi import HTTPException
    from app.services.person_service import merge_people

    p2 = Person(name="Secundário")
    db_session.add(p2)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        merge_people(db_session, 9999, [p2.id])
    assert exc.value.status_code == 404


def test_merge_people_raises_400_for_self_merge(db_session):
    from fastapi import HTTPException
    from app.services.person_service import merge_people

    p1 = Person(name="Principal")
    db_session.add(p1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        merge_people(db_session, p1.id, [p1.id])
    assert exc.value.status_code == 400
