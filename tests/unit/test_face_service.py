from unittest.mock import ANY, patch

import numpy as np
import pytest

from app.core.settings import settings


def make_bgr_frame() -> np.ndarray:
    return np.zeros((480, 640, 3), dtype=np.uint8)


def make_embedding() -> np.ndarray:
    return np.random.rand(128).astype(np.float64)


# ── extract_embeddings ────────────────────────────────────────────────────────

def test_extract_embeddings_no_face_returns_empty():
    from app.services.face_service import extract_embeddings

    with patch("app.services.face_service.face_recognition.face_locations", return_value=[]), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[]):
        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_two_faces_returns_two():
    from app.services.face_service import extract_embeddings

    emb1, emb2 = make_embedding(), make_embedding()
    with patch("app.services.face_service.face_recognition.face_locations", return_value=["loc1", "loc2"]), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[emb1, emb2]):
        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 2


def test_extract_embeddings_converts_bgr_to_rgb():
    """Verifica que face_locations recebe frame RGB (não BGR)."""
    from app.services.face_service import extract_embeddings

    bgr_frame = np.zeros((2, 2, 3), dtype=np.uint8)
    bgr_frame[0, 0] = [10, 20, 30]  # B=10, G=20, R=30

    captured = {}

    def fake_locations(rgb_frame, **kwargs):
        captured["frame"] = rgb_frame.copy()
        return []

    with patch("app.services.face_service.face_recognition.face_locations", side_effect=fake_locations), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[]):
        extract_embeddings(bgr_frame)

    # pixel [0,0] deve ter R=10, G=20, B=30 (invertido)
    assert captured["frame"][0, 0, 0] == 30  # R channel
    assert captured["frame"][0, 0, 2] == 10  # B channel


def test_extract_embeddings_calls_face_locations_with_settings_model_and_upsample():
    from app.services.face_service import extract_embeddings

    with patch("app.services.face_service.face_recognition.face_locations", return_value=[]) as mock_locations, \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[]):
        extract_embeddings(make_bgr_frame())

    mock_locations.assert_called_with(
        ANY,
        number_of_times_to_upsample=settings.FACE_UPSAMPLE,
        model=settings.FACE_DETECTION_MODEL,
    )


# ── find_matching_person ──────────────────────────────────────────────────────

def test_find_matching_empty_list_returns_none():
    from app.services.face_service import find_matching_person

    result = find_matching_person(make_embedding(), [])
    assert result == (None, None)


def test_find_matching_below_tolerance_returns_match():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(42, target)]  # distância ~0

    with patch("app.services.face_service.face_recognition.face_distance", return_value=np.array([0.3])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6)

    assert person_id == 42
    assert dist == pytest.approx(0.3)


def test_find_matching_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(7, make_embedding())]

    with patch("app.services.face_service.face_recognition.face_distance", return_value=np.array([0.8])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6)

    assert person_id is None
    assert dist is None


def test_find_matching_picks_closest():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(1, make_embedding()), (2, make_embedding()), (3, make_embedding())]

    with patch("app.services.face_service.face_recognition.face_distance",
               return_value=np.array([0.5, 0.2, 0.4])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6)

    assert person_id == 2
    assert dist == pytest.approx(0.2)
