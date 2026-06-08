from unittest.mock import ANY, patch

import numpy as np
import pytest

from app.core.settings import settings


def make_bgr_frame() -> np.ndarray:
    return np.zeros((480, 640, 3), dtype=np.uint8)


def make_embedding() -> np.ndarray:
    return np.random.rand(128).astype(np.float64)


def make_face_location(size: int = 120) -> tuple:
    """(top, right, bottom, left) representando rosto quadrado de `size` px."""
    return (0, size, size, 0)


# ── is_good_quality_frame ─────────────────────────────────────────────────────

def test_is_good_quality_frame_rejects_small_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    small_location = make_face_location(size=30)  # < min_face_size=60

    assert is_good_quality_frame(small_location, frame, min_face_size=60) is False


def test_is_good_quality_frame_rejects_blurred_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:120, :120] = 128  # região uniforme → variância do Laplaciano ≈ 0
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, min_face_size=60) is False


def test_is_good_quality_frame_accepts_sharp_large_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    rng = np.random.default_rng(42)
    frame[:120, :120] = rng.integers(0, 255, (120, 120, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, min_face_size=60) is True


# ── extract_embeddings ────────────────────────────────────────────────────────

def test_extract_embeddings_no_face_returns_empty():
    from app.services.face_service import extract_embeddings

    with patch("app.services.face_service.face_recognition.face_locations", return_value=[]), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[]):
        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_two_faces_returns_two_tuples():
    from app.services.face_service import extract_embeddings

    emb1, emb2 = make_embedding(), make_embedding()
    loc1, loc2 = make_face_location(120), make_face_location(120)
    with patch("app.services.face_service.face_recognition.face_locations", return_value=[loc1, loc2]), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[emb1, emb2]), \
         patch("app.services.face_service.is_good_quality_frame", return_value=True):
        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 2
    assert result[0] == (emb1, loc1)
    assert result[1] == (emb2, loc2)


def test_extract_embeddings_discards_small_faces():
    from app.services.face_service import extract_embeddings

    loc_small = make_face_location(30)
    with patch("app.services.face_service.face_recognition.face_locations", return_value=[loc_small]), \
         patch("app.services.face_service.face_recognition.face_encodings", return_value=[make_embedding()]), \
         patch("app.services.face_service.is_good_quality_frame", return_value=False) as mock_quality:
        result = extract_embeddings(make_bgr_frame())

    mock_quality.assert_called_once_with(loc_small, ANY, settings.FACE_MIN_SIZE_PX)
    assert result == []


def test_extract_embeddings_all_bad_quality_returns_empty():
    from app.services.face_service import extract_embeddings

    locations = [make_face_location(30), make_face_location(40)]
    with patch("app.services.face_service.face_recognition.face_locations", return_value=locations), \
         patch("app.services.face_service.face_recognition.face_encodings") as mock_encodings, \
         patch("app.services.face_service.is_good_quality_frame", return_value=False):
        result = extract_embeddings(make_bgr_frame())

    mock_encodings.assert_not_called()
    assert result == []


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


# ── find_matching_person — votação k-NN ──────────────────────────────────────

def test_find_matching_majority_vote_overrides_nearest_neighbor():
    """3 vizinhos mais próximos votam: pessoa 1 vence por maioria mesmo
    sem ser o vizinho mais próximo isolado."""
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(1, make_embedding()), (2, make_embedding()), (1, make_embedding())]

    with patch("app.services.face_service.face_recognition.face_distance",
               return_value=np.array([0.1, 0.15, 0.2])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id == 1
    assert dist == pytest.approx(0.1)


def test_find_matching_knn_ignores_neighbors_above_tolerance():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(1, make_embedding()), (2, make_embedding()), (3, make_embedding())]

    with patch("app.services.face_service.face_recognition.face_distance",
               return_value=np.array([0.1, 0.9, 0.95])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id == 1
    assert dist == pytest.approx(0.1)


def test_find_matching_knn_all_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(1, make_embedding()), (2, make_embedding())]

    with patch("app.services.face_service.face_recognition.face_distance",
               return_value=np.array([0.7, 0.8])):
        person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id is None
    assert dist is None


def test_find_matching_uses_settings_knn_k_default():
    from app.services.face_service import find_matching_person
    import inspect

    params = inspect.signature(find_matching_person).parameters
    assert params["k"].default == settings.FACE_KNN_K
