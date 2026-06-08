from unittest.mock import ANY, patch, MagicMock
import numpy as np
import pytest

from app.core.settings import settings


def make_bgr_frame() -> np.ndarray:
    return np.zeros((480, 640, 3), dtype=np.uint8)


def make_embedding() -> np.ndarray:
    emb = np.random.rand(128).astype(np.float64)
    return emb / np.linalg.norm(emb)


def make_face_location(size: int = 120) -> tuple:
    """(top, right, bottom, left) representando rosto quadrado de `size` px."""
    return (0, size, size, 0)


@pytest.fixture(autouse=True)
def reset_face_service_singletons():
    import app.services.face_service
    app.services.face_service._detector = None
    app.services.face_service._recognizer = None



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

    with patch("cv2.FaceDetectorYN.create") as mock_det_create, \
         patch("cv2.FaceRecognizerSF.create") as mock_rec_create:
        
        mock_det = MagicMock()
        mock_det.detect.return_value = (0, None)
        mock_det_create.return_value = mock_det
        
        mock_rec = MagicMock()
        mock_rec_create.return_value = mock_rec

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_two_faces_returns_two_tuples():
    from app.services.face_service import extract_embeddings

    emb1, emb2 = make_embedding(), make_embedding()
    # YuNet detect outputs (N, 15), where x,y,w,h is face[0:4]
    # Bounding Box 1: x=0, y=0, w=120, h=120 -> location=(0, 120, 120, 0)
    # Bounding Box 2: x=100, y=100, w=120, h=120 -> location=(100, 220, 220, 100)
    faces_arr = np.zeros((2, 15), dtype=np.float32)
    faces_arr[0, 0:4] = [0, 0, 120, 120]
    faces_arr[1, 0:4] = [100, 100, 120, 120]

    with patch("cv2.FaceDetectorYN.create") as mock_det_create, \
         patch("cv2.FaceRecognizerSF.create") as mock_rec_create, \
         patch("app.services.face_service.is_good_quality_frame", return_value=True):
        
        mock_det = MagicMock()
        mock_det.detect.return_value = (2, faces_arr)
        mock_det_create.return_value = mock_det
        
        mock_rec = MagicMock()
        mock_rec.feature.side_effect = [emb1.reshape(1, 128), emb2.reshape(1, 128)]
        mock_rec_create.return_value = mock_rec

        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 2
    assert np.allclose(result[0][0], emb1)
    assert result[0][1] == (0, 120, 120, 0)
    assert np.allclose(result[1][0], emb2)
    assert result[1][1] == (100, 220, 220, 100)


def test_extract_embeddings_discards_small_faces():
    from app.services.face_service import extract_embeddings

    faces_arr = np.zeros((1, 15), dtype=np.float32)
    faces_arr[0, 0:4] = [0, 0, 30, 30]

    with patch("cv2.FaceDetectorYN.create") as mock_det_create, \
         patch("cv2.FaceRecognizerSF.create") as mock_rec_create, \
         patch("app.services.face_service.is_good_quality_frame", return_value=False) as mock_quality:
        
        mock_det = MagicMock()
        mock_det.detect.return_value = (1, faces_arr)
        mock_det_create.return_value = mock_det
        
        mock_rec = MagicMock()
        mock_rec_create.return_value = mock_rec

        result = extract_embeddings(make_bgr_frame())

    mock_quality.assert_called_once_with((0, 30, 30, 0), ANY, settings.FACE_MIN_SIZE_PX)
    assert result == []


def test_extract_embeddings_all_bad_quality_returns_empty():
    from app.services.face_service import extract_embeddings

    faces_arr = np.zeros((2, 15), dtype=np.float32)
    faces_arr[0, 0:4] = [0, 0, 30, 30]
    faces_arr[1, 0:4] = [0, 0, 40, 40]

    with patch("cv2.FaceDetectorYN.create") as mock_det_create, \
         patch("cv2.FaceRecognizerSF.create") as mock_rec_create, \
         patch("app.services.face_service.is_good_quality_frame", return_value=False):
        
        mock_det = MagicMock()
        mock_det.detect.return_value = (2, faces_arr)
        mock_det_create.return_value = mock_det
        
        mock_rec = MagicMock()
        mock_rec_create.return_value = mock_rec

        result = extract_embeddings(make_bgr_frame())

    mock_rec.feature.assert_not_called()
    assert result == []


# ── find_matching_person ──────────────────────────────────────────────────────

def test_find_matching_empty_list_returns_none():
    from app.services.face_service import find_matching_person

    result = find_matching_person(make_embedding(), [])
    assert result == (None, None)


def test_find_matching_below_tolerance_returns_match():
    from app.services.face_service import find_matching_person

    target = make_embedding()
    known = [(42, target)]  # distância ~0

    person_id, dist = find_matching_person(target, known, tolerance=0.6)

    assert person_id == 42
    assert dist == pytest.approx(0.0)


def test_find_matching_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    target = np.ones(128)
    known = [(7, np.zeros(128))]  # dist = sqrt(128) ≈ 11.3

    person_id, dist = find_matching_person(target, known, tolerance=0.6)

    assert person_id is None
    assert dist is None


def test_find_matching_picks_closest():
    from app.services.face_service import find_matching_person

    target = np.zeros(128)
    # dists: 5.0, 2.0, 4.0
    known = [
        (1, np.ones(128) * (5.0 / np.sqrt(128))),
        (2, np.ones(128) * (2.0 / np.sqrt(128))),
        (3, np.ones(128) * (4.0 / np.sqrt(128)))
    ]

    person_id, dist = find_matching_person(target, known, tolerance=6.0)

    assert person_id == 2
    assert dist == pytest.approx(2.0)


# ── find_matching_person — votação k-NN ──────────────────────────────────────

def test_find_matching_majority_vote_overrides_nearest_neighbor():
    """3 vizinhos mais próximos votam: pessoa 1 vence por maioria mesmo
    sem ser o vizinho mais próximo isolado."""
    from app.services.face_service import find_matching_person

    target = np.zeros(128)
    known = [
        (1, np.ones(128) * (0.1 / np.sqrt(128))),
        (2, np.ones(128) * (0.15 / np.sqrt(128))),
        (1, np.ones(128) * (0.2 / np.sqrt(128)))
    ]

    person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id == 1
    assert dist == pytest.approx(0.1)


def test_find_matching_knn_ignores_neighbors_above_tolerance():
    from app.services.face_service import find_matching_person

    target = np.zeros(128)
    known = [
        (1, np.ones(128) * (0.1 / np.sqrt(128))),
        (2, np.ones(128) * (0.9 / np.sqrt(128))),
        (3, np.ones(128) * (0.95 / np.sqrt(128)))
    ]

    person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id == 1
    assert dist == pytest.approx(0.1)


def test_find_matching_knn_all_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    target = np.zeros(128)
    known = [
        (1, np.ones(128) * (0.7 / np.sqrt(128))),
        (2, np.ones(128) * (0.8 / np.sqrt(128)))
    ]

    person_id, dist = find_matching_person(target, known, tolerance=0.6, k=3)

    assert person_id is None
    assert dist is None


def test_find_matching_uses_settings_knn_k_default():
    from app.services.face_service import find_matching_person
    import inspect

    params = inspect.signature(find_matching_person).parameters
    assert params["k"].default == settings.FACE_KNN_K


def test_extract_embeddings_returns_l2_normalized():
    from app.services.face_service import extract_embeddings
    
    # Geramos um embedding não normalizado no mock (todos 5.0, norma = ~56.56)
    raw_emb = np.ones(128).astype(np.float64) * 5.0
    faces_arr = np.zeros((1, 15), dtype=np.float32)
    faces_arr[0, 0:4] = [0, 0, 120, 120]
    
    with patch("cv2.FaceDetectorYN.create") as mock_det_create, \
         patch("cv2.FaceRecognizerSF.create") as mock_rec_create, \
         patch("app.services.face_service.is_good_quality_frame", return_value=True):
        
        mock_det = MagicMock()
        mock_det.detect.return_value = (1, faces_arr)
        mock_det_create.return_value = mock_det
        
        mock_rec = MagicMock()
        mock_rec.feature.return_value = raw_emb.reshape(1, 128)
        mock_rec_create.return_value = mock_rec
        
        result = extract_embeddings(make_bgr_frame())
        
    assert len(result) == 1
    embedding = result[0][0]
    # O embedding retornado pelo face_service deve ser normalizado L2
    assert np.allclose(np.linalg.norm(embedding), 1.0)

