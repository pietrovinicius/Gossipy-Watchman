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
