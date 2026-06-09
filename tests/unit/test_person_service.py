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

    raw = np.random.rand(512).astype(np.float32)
    embedding = raw / np.linalg.norm(raw)
    npy_path = tmp_path / f"{person.id}_embedding_0.npy"
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

    expected_npy = str(tmp_path / f"{person.id}_embedding_0.npy")
    assert mock_save.call_count == 1
    assert mock_save.call_args[0][0] == expected_npy


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


def test_get_person_stats_ignores_open_appearance_without_timestamp_end(db_session):
    """Aparição "aberta" (timestamp_end=None) não deve quebrar o cálculo de total_seconds."""
    from datetime import datetime, timezone
    from app.models.video import Video, VideoStatus
    from app.models.appearance import Appearance
    from app.services.person_service import get_person_stats

    person = Person(name="Com Aparição Aberta")
    db_session.add(person)
    video = Video(
        file_name="v2.mp4",
        file_path="storage/videos/v2.mp4",
        status=VideoStatus.CONCLUIDO,
        uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db_session.add(video)
    db_session.commit()

    fechada = Appearance(person_id=person.id, video_id=video.id, timestamp_start=0.0, timestamp_end=5.0, confidence=0.3)
    aberta = Appearance(person_id=person.id, video_id=video.id, timestamp_start=10.0, timestamp_end=None, confidence=0.4)
    db_session.add_all([fechada, aberta])
    db_session.commit()

    stats = get_person_stats(db_session, person.id)
    assert stats["video_count"] == 1
    assert stats["total_seconds"] == pytest.approx(5.0)


# ── save_face_sample ──────────────────────────────────────────────────────────

def test_save_face_sample_calls_imwrite_with_correct_path(db_session, tmp_path):
    from app.services.person_service import save_face_sample

    person = Person(name="Alguém")
    db_session.add(person)
    db_session.commit()

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)

    with patch("app.services.person_service.cv2.imwrite") as mock_imwrite, \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_settings.FACE_MAX_SAMPLES_PER_PERSON = 10
        mock_settings.FACE_MAX_EMBEDDINGS_PER_PERSON = 5
        mock_imwrite.return_value = True

        result = save_face_sample(db_session, person.id, appearance_id=42, face_crop=face_crop)

    expected_path = str(tmp_path / f"{person.id}_sample_42.jpg")
    mock_imwrite.assert_called_once_with(expected_path, face_crop)
    assert result == expected_path


def test_save_face_sample_returns_none_when_limit_reached(db_session, tmp_path):
    from app.services.person_service import save_face_sample

    person = Person(name="Alguém")
    db_session.add(person)
    db_session.commit()

    for i in range(10):
        (tmp_path / f"{person.id}_sample_{i}.jpg").write_bytes(b"x")

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)

    with patch("app.services.person_service.cv2.imwrite") as mock_imwrite, \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_settings.FACE_MAX_SAMPLES_PER_PERSON = 10

        result = save_face_sample(db_session, person.id, appearance_id=99, face_crop=face_crop)

    assert result is None
    mock_imwrite.assert_not_called()


def test_save_face_sample_returns_none_and_does_not_raise_on_error(db_session, tmp_path):
    from app.services.person_service import save_face_sample

    person = Person(name="Alguém")
    db_session.add(person)
    db_session.commit()

    face_crop = np.zeros((64, 64, 3), dtype=np.uint8)

    with patch("app.services.person_service.cv2.imwrite", side_effect=Exception("disco cheio")), \
         patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_settings.FACE_MAX_SAMPLES_PER_PERSON = 10

        result = save_face_sample(db_session, person.id, appearance_id=7, face_crop=face_crop)

    assert result is None


# ── list_face_samples ─────────────────────────────────────────────────────────

def test_list_face_samples_returns_empty_when_no_files(db_session, tmp_path):
    from app.services.person_service import list_face_samples

    person = Person(name="Sem amostras", profile_image_path=None)
    db_session.add(person)
    db_session.commit()

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        result = list_face_samples(db_session, person.id)

    assert result == []


def test_list_face_samples_includes_primary_and_samples(db_session, tmp_path):
    from app.services.person_service import list_face_samples

    person = Person(name="Com amostras", profile_image_path=None)
    db_session.add(person)
    db_session.commit()
    pid = person.id
    person.profile_image_path = str(tmp_path / f"{pid}.jpg")
    db_session.commit()

    (tmp_path / f"{pid}.jpg").write_bytes(b"x")
    (tmp_path / f"{pid}_sample_10.jpg").write_bytes(b"x")
    (tmp_path / f"{pid}_sample_11.jpg").write_bytes(b"x")
    (tmp_path / f"{pid}_embedding.npy").write_bytes(b"x")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        result = list_face_samples(db_session, pid)

    filenames = {item["filename"] for item in result}
    assert filenames == {f"{pid}.jpg", f"{pid}_sample_10.jpg", f"{pid}_sample_11.jpg"}
    primary = [item for item in result if item["is_primary"]]
    assert len(primary) == 1
    assert primary[0]["filename"] == f"{pid}.jpg"


# ── set_primary_photo ─────────────────────────────────────────────────────────

def test_set_primary_photo_raises_400_for_path_traversal(db_session, tmp_path):
    from fastapi import HTTPException
    from app.services.person_service import set_primary_photo

    person = Person(name="Alguém", profile_image_path=None)
    db_session.add(person)
    db_session.commit()

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        with pytest.raises(HTTPException) as exc:
            set_primary_photo(db_session, person.id, "../../etc/passwd")

    assert exc.value.status_code == 400


def test_set_primary_photo_raises_404_for_missing_file(db_session, tmp_path):
    from fastapi import HTTPException
    from app.services.person_service import set_primary_photo

    person = Person(name="Alguém", profile_image_path=None)
    db_session.add(person)
    db_session.commit()

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        with pytest.raises(HTTPException) as exc:
            set_primary_photo(db_session, person.id, f"{person.id}_sample_999.jpg")

    assert exc.value.status_code == 404


def test_set_primary_photo_raises_403_for_other_persons_file(db_session, tmp_path):
    from fastapi import HTTPException
    from app.services.person_service import set_primary_photo

    p1 = Person(name="Dono", profile_image_path=None)
    p2 = Person(name="Outro", profile_image_path=None)
    db_session.add_all([p1, p2])
    db_session.commit()

    (tmp_path / f"{p2.id}_sample_1.jpg").write_bytes(b"x")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        with pytest.raises(HTTPException) as exc:
            set_primary_photo(db_session, p1.id, f"{p2.id}_sample_1.jpg")

    assert exc.value.status_code == 403


def test_set_primary_photo_copies_and_updates_profile_image_path(db_session, tmp_path):
    from app.services.person_service import set_primary_photo

    person = Person(name="Alguém", profile_image_path=str(tmp_path / "old.jpg"))
    db_session.add(person)
    db_session.commit()
    pid = person.id

    sample = tmp_path / f"{pid}_sample_3.jpg"
    sample.write_bytes(b"conteudo-da-amostra")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        result = set_primary_photo(db_session, pid, f"{pid}_sample_3.jpg")

    primary_path = tmp_path / f"{pid}.jpg"
    assert primary_path.exists()
    assert primary_path.read_bytes() == b"conteudo-da-amostra"
    assert sample.exists()  # shutil.copy2 preserva o original
    assert result.profile_image_path == str(primary_path)


# ── get_profile_quality ───────────────────────────────────────────────────────

def _seed_appearances_with_confidences(db_session, confidences):
    from datetime import datetime, timezone
    from app.models.video import Video, VideoStatus
    from app.models.appearance import Appearance

    person = Person(name="Avaliada")
    db_session.add(person)
    video = Video(file_name="q.mp4", file_path="storage/videos/q.mp4",
                  status=VideoStatus.CONCLUIDO, uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc))
    db_session.add(video)
    db_session.commit()

    for i, conf in enumerate(confidences):
        db_session.add(Appearance(person_id=person.id, video_id=video.id,
                                  timestamp_start=float(i), timestamp_end=float(i) + 1, confidence=conf))
    db_session.commit()
    return person


def test_profile_quality_excelente_for_low_avg_confidence(db_session):
    from app.services.person_service import get_profile_quality

    # dist=0.05 → score=95% > 90 → "excelente" (match muito próximo para coseno ArcFace)
    person = _seed_appearances_with_confidences(db_session, [0.05, 0.05])
    quality = get_profile_quality(db_session, person.id)

    assert quality["avg_confidence"] == pytest.approx(0.05)
    assert quality["quality_score"] == pytest.approx(95.0)
    assert quality["quality_level"] == "excelente"
    assert quality["color"] == "green"


def test_profile_quality_bom_for_mid_avg_confidence(db_session):
    from app.services.person_service import get_profile_quality

    # dist=0.15 → score=85% > 80 → "bom"
    person = _seed_appearances_with_confidences(db_session, [0.15, 0.15])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_score"] == pytest.approx(85.0)
    assert quality["quality_level"] == "bom"
    assert quality["color"] == "green"


def test_profile_quality_regular_for_borderline_avg_confidence(db_session):
    from app.services.person_service import get_profile_quality

    # dist=0.25 → score=75% > 70 → "regular"
    person = _seed_appearances_with_confidences(db_session, [0.25, 0.25])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_score"] == pytest.approx(75.0)
    assert quality["quality_level"] == "regular"
    assert quality["color"] == "yellow"


def test_profile_quality_insuficiente_for_high_avg_confidence(db_session):
    from app.services.person_service import get_profile_quality

    # dist=0.35 → score=65% > 60 → "insuficiente"
    person = _seed_appearances_with_confidences(db_session, [0.35, 0.35])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_score"] == pytest.approx(65.0)
    assert quality["quality_level"] == "insuficiente"
    assert quality["color"] == "yellow"


def test_profile_quality_fraco_for_very_high_avg_confidence(db_session):
    from app.services.person_service import get_profile_quality

    person = _seed_appearances_with_confidences(db_session, [0.7, 0.7])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_score"] == pytest.approx(30.0)
    assert quality["quality_level"] == "fraco"
    assert quality["color"] == "red"


def test_profile_quality_sample_count_matches_appearance_count(db_session):
    from app.services.person_service import get_profile_quality

    person = _seed_appearances_with_confidences(db_session, [0.3, 0.4, 0.5])
    quality = get_profile_quality(db_session, person.id)

    assert quality["sample_count"] == 3
    assert quality["avg_confidence"] == pytest.approx(0.4)


def test_profile_quality_handles_person_without_appearances(db_session):
    from app.services.person_service import get_profile_quality

    person = Person(name="Sem Histórico")
    db_session.add(person)
    db_session.commit()

    quality = get_profile_quality(db_session, person.id)

    assert quality["sample_count"] == 0
    assert quality["avg_confidence"] == pytest.approx(0.0)
    assert quality["quality_score"] == pytest.approx(0.0)
    assert quality["quality_level"] == "insuficiente"
    assert quality["color"] == "red"


def test_profile_quality_recommendation_is_non_empty_for_every_level(db_session):
    from app.services.person_service import get_profile_quality

    for confidences in ([0.3, 0.3], [0.5, 0.5], [0.55, 0.55], [0.58, 0.58], [0.7, 0.7]):
        person = _seed_appearances_with_confidences(db_session, confidences)
        quality = get_profile_quality(db_session, person.id)
        assert isinstance(quality["recommendation"], str)
        assert quality["recommendation"].strip() != ""


def test_profile_quality_score_rounded_to_one_decimal(db_session):
    from app.services.person_service import get_profile_quality

    person = _seed_appearances_with_confidences(db_session, [0.333, 0.334, 0.335])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_score"] == round((1 - quality["avg_confidence"]) * 100, 1)


def test_profile_quality_raises_404_for_unknown_person(db_session):
    from fastapi import HTTPException
    from app.services.person_service import get_profile_quality

    with pytest.raises(HTTPException) as exc:
        get_profile_quality(db_session, 9999)
    assert exc.value.status_code == 404


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


# ── soft delete / restore ─────────────────────────────────────────────────────

def test_soft_delete_person_sets_deleted_at(db_session):
    from app.services.person_service import soft_delete_person

    p = Person(name="Alvo")
    db_session.add(p)
    db_session.commit()

    result = soft_delete_person(db_session, p.id)

    assert result is not None
    assert result.deleted_at is not None


def test_soft_delete_person_returns_none_for_unknown_id(db_session):
    from app.services.person_service import soft_delete_person

    assert soft_delete_person(db_session, 9999) is None


def test_soft_delete_person_is_idempotent(db_session):
    from app.services.person_service import soft_delete_person

    p = Person(name="Alvo")
    db_session.add(p)
    db_session.commit()

    first = soft_delete_person(db_session, p.id)
    second = soft_delete_person(db_session, p.id)

    assert first.deleted_at == second.deleted_at


def test_restore_person_clears_deleted_at(db_session):
    from app.services.person_service import soft_delete_person, restore_person

    p = Person(name="Alvo")
    db_session.add(p)
    db_session.commit()

    soft_delete_person(db_session, p.id)
    restored = restore_person(db_session, p.id)

    assert restored is not None
    assert restored.deleted_at is None


def test_list_people_excludes_deleted_by_default(db_session):
    from app.services.person_service import soft_delete_person, list_people

    p1 = Person(name="Ativo")
    p2 = Person(name="Removido")
    db_session.add_all([p1, p2])
    db_session.commit()

    soft_delete_person(db_session, p2.id)

    result = list_people(db_session)

    ids = [p.id for p in result]
    assert p1.id in ids
    assert p2.id not in ids


def test_list_people_include_deleted_returns_all(db_session):
    from app.services.person_service import soft_delete_person, list_people

    p1 = Person(name="Ativo")
    p2 = Person(name="Removido")
    db_session.add_all([p1, p2])
    db_session.commit()

    soft_delete_person(db_session, p2.id)

    result = list_people(db_session, include_deleted=True)

    ids = [p.id for p in result]
    assert p1.id in ids
    assert p2.id in ids


# ── reset_person_name ─────────────────────────────────────────────────────────

def test_reset_person_name_sets_desconhecido_pattern(db_session):
    from app.services.person_service import reset_person_name

    p = Person(name="Fulano da Silva")
    db_session.add(p)
    db_session.commit()

    result = reset_person_name(db_session, p.id)

    assert result is not None
    assert result.name == f"Desconhecido #{p.id}"


def test_reset_person_name_returns_none_for_unknown_id(db_session):
    from app.services.person_service import reset_person_name

    assert reset_person_name(db_session, 9999) is None


def test_reset_person_name_persists_change(db_session):
    from app.services.person_service import reset_person_name

    p = Person(name="Fulano da Silva")
    db_session.add(p)
    db_session.commit()
    pid = p.id

    reset_person_name(db_session, pid)

    reloaded = db_session.get(Person, pid)
    assert reloaded.name == f"Desconhecido #{pid}"


# ── Multi-embedding (InsightFace) ─────────────────────────────────────────────

def test_get_all_embeddings_loads_multiple_npy_per_person(tmp_path, monkeypatch):
    """get_all_embeddings carrega todos os embedding_*.npy de cada pessoa."""
    import numpy as np
    from unittest.mock import MagicMock
    from app.services.person_service import get_all_embeddings

    np.save(str(tmp_path / "1_embedding_0.npy"), np.ones(512, dtype=np.float32))
    np.save(str(tmp_path / "1_embedding_1.npy"), np.zeros(512, dtype=np.float32))

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    mock_person = MagicMock()
    mock_person.id = 1

    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_person]

    result = get_all_embeddings(mock_db)

    assert len(result) == 2
    assert all(pid == 1 for pid, _ in result)


def test_get_all_embeddings_skips_wrong_shape(tmp_path, monkeypatch):
    """Embedding com shape != (512,) é ignorado."""
    import numpy as np
    from unittest.mock import MagicMock
    from app.services.person_service import get_all_embeddings

    np.save(str(tmp_path / "1_embedding_0.npy"), np.zeros(128, dtype=np.float32))

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    mock_person = MagicMock()
    mock_person.id = 1
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_person]

    result = get_all_embeddings(mock_db)
    assert result == []


def test_save_new_person_creates_embedding_0_npy(tmp_path, monkeypatch):
    """save_new_person grava {id}_embedding_0.npy."""
    import numpy as np
    from unittest.mock import MagicMock, patch
    from app.services.person_service import save_new_person

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    embedding = np.ones(512, dtype=np.float32)
    face_crop = np.zeros((80, 80, 3), dtype=np.uint8)

    mock_person = MagicMock()
    mock_person.id = 7

    mock_db = MagicMock()
    mock_db.refresh.side_effect = lambda p: None

    with patch("app.services.person_service.Person") as MockPerson:
        MockPerson.return_value = mock_person
        save_new_person(mock_db, embedding, face_crop, person_index=7)

    assert (tmp_path / "7_embedding_0.npy").exists()
    assert not (tmp_path / "7_embedding.npy").exists()


def test_save_face_sample_adds_embedding_when_below_limit(tmp_path, monkeypatch):
    """save_face_sample grava embedding adicional quando abaixo do limite."""
    import numpy as np
    from app.services.person_service import save_face_sample

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)
    monkeypatch.setattr("app.services.person_service.settings.FACE_MAX_EMBEDDINGS_PER_PERSON", 5)

    np.save(str(tmp_path / "3_embedding_0.npy"), np.ones(512, dtype=np.float32))

    mock_db = MagicMock()
    face_crop = np.zeros((60, 60, 3), dtype=np.uint8)
    embedding = np.ones(512, dtype=np.float32)

    save_face_sample(mock_db, person_id=3, appearance_id=99, face_crop=face_crop, embedding=embedding)

    assert (tmp_path / "3_embedding_1.npy").exists()


# ── Task 4 V3: merge_people copia embeddings do secundário para primário ──────

def test_merge_people_copia_embeddings_do_secundario(tmp_path):
    """merge_people deve copiar .npy do secundário para o primário antes de deletar."""
    from app.services.person_service import merge_people
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    p1 = Person(name="Principal")
    p2 = Person(name="Secundário")
    db.add_all([p1, p2])
    db.commit()

    emb_primary = np.array([1.0, 0.0], dtype=np.float32)
    np.save(tmp_path / f"{p1.id}_embedding_0.npy", emb_primary)

    emb_secondary = np.array([0.0, 1.0], dtype=np.float32)
    np.save(tmp_path / f"{p2.id}_embedding_0.npy", emb_secondary)

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_settings.FACE_MAX_EMBEDDINGS_PER_PERSON = 5
        merge_people(db, p1.id, [p2.id])

    primary_embs = sorted(tmp_path.glob(f"{p1.id}_embedding_*.npy"))
    assert len(primary_embs) == 2, (
        f"Esperado 2 embeddings no primário após merge, obtido {len(primary_embs)} — "
        "embedding do secundário foi deletado sem copiar para o primário"
    )

    secondary_embs = list(tmp_path.glob(f"{p2.id}_embedding_*.npy"))
    assert len(secondary_embs) == 0

    db.close()
    engine.dispose()


def test_merge_people_respeita_limite_max_embeddings(tmp_path):
    """merge_people não deve ultrapassar FACE_MAX_EMBEDDINGS_PER_PERSON no primário."""
    from app.services.person_service import merge_people
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    p1 = Person(name="Principal")
    p2 = Person(name="Secundário")
    db.add_all([p1, p2])
    db.commit()

    # Primário já tem 4 embeddings; limite = 5 → pode absorver apenas 1 do secundário
    for i in range(4):
        np.save(tmp_path / f"{p1.id}_embedding_{i}.npy", np.zeros(2, dtype=np.float32))
    for i in range(3):
        np.save(tmp_path / f"{p2.id}_embedding_{i}.npy", np.ones(2, dtype=np.float32))

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        mock_settings.FACE_MAX_EMBEDDINGS_PER_PERSON = 5
        merge_people(db, p1.id, [p2.id])

    primary_embs = sorted(tmp_path.glob(f"{p1.id}_embedding_*.npy"))
    assert len(primary_embs) <= 5, (
        f"Primário não deve exceder o limite de 5 embeddings, obtido {len(primary_embs)}"
    )

    db.close()
    engine.dispose()


# ── Task 7 V3: bandas de qualidade recalibradas para distância coseno ─────────

def test_quality_excelente_so_para_distancia_coseno_muito_baixa(db_session):
    """Para distância coseno, 'excelente' deve exigir score > 90% (dist < 0.1).
    dist=0.3 (score=70%) está perto do threshold e não deve ser 'excelente'."""
    from app.services.person_service import get_profile_quality

    # confidence=0.3 → score=70% — bom match, mas não "excelente" para coseno
    person = _seed_appearances_with_confidences(db_session, [0.3, 0.3])
    quality = get_profile_quality(db_session, person.id)

    assert quality["quality_level"] != "excelente", (
        f"dist=0.3 (score=70%) não deve ser 'excelente' para distância coseno "
        f"(threshold=0.4); bandas precisam de recalibração. Obtido: {quality['quality_level']}"
    )


# ── Task 8 V3: MAX_FACE_SAMPLES deve vir de settings ─────────────────────────

def test_save_face_sample_respeita_settings_max_samples(tmp_path):
    """save_face_sample deve usar settings.FACE_MAX_SAMPLES_PER_PERSON, não constante hardcoded."""
    from app.services.person_service import save_face_sample
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    face_crop = np.zeros((80, 80, 3), dtype=np.uint8)
    embedding = np.zeros(512, dtype=np.float32)
    embedding[0] = 1.0

    cap = 3  # limite custom menor que MAX_FACE_SAMPLES=10 hardcoded

    with patch("app.services.person_service.settings") as mock_s:
        mock_s.STORAGE_FACES = tmp_path
        mock_s.FACE_MAX_SAMPLES_PER_PERSON = cap
        mock_s.FACE_MAX_EMBEDDINGS_PER_PERSON = 10  # não limitar embeddings neste teste

        for i in range(cap + 2):
            save_face_sample(db, person_id=1, appearance_id=i,
                             face_crop=face_crop, embedding=embedding)

    samples = list(tmp_path.glob("1_sample_*.jpg"))
    assert len(samples) <= cap, (
        f"save_face_sample deve parar em {cap} (settings.FACE_MAX_SAMPLES_PER_PERSON), "
        f"obtido {len(samples)} — provavelmente usando MAX_FACE_SAMPLES=10 hardcoded"
    )

    db.close()
    engine.dispose()
