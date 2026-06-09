from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.core.settings import settings


def make_bgr_frame(h: int = 480, w: int = 640) -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.integers(0, 255, (h, w, 3), dtype=np.uint8)


def make_l2_embedding(dim: int = 512) -> np.ndarray:
    v = np.random.rand(dim).astype(np.float32)
    return v / np.linalg.norm(v)


def make_face_location(size: int = 120) -> tuple:
    """(top, right, bottom, left)"""
    return (0, size, size, 0)


def make_mock_face(
    bbox: list | None = None,
    det_score: float = 0.95,
    embedding: np.ndarray | None = None,
):
    face = MagicMock()
    face.bbox = np.array(bbox or [0, 0, 120, 120], dtype=np.float32)
    face.det_score = det_score
    face.embedding = embedding if embedding is not None else make_l2_embedding()
    return face


# ── is_good_quality_frame ─────────────────────────────────────────────────────

def test_is_good_quality_frame_rejects_small_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    small_location = make_face_location(size=30)

    assert is_good_quality_frame(small_location, frame, min_face_size=60) is False


def test_is_good_quality_frame_rejects_blurred_face():
    from app.services.face_service import is_good_quality_frame

    blurred_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, blurred_frame, blur_threshold=100.0) is False


def test_is_good_quality_frame_accepts_sharp_large_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, min_face_size=60, blur_threshold=10.0) is True


def test_is_good_quality_frame_rejects_low_det_score():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, det_score=0.5, det_score_threshold=0.7) is False


def test_is_good_quality_frame_accepts_high_det_score():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(
        location, frame, det_score=0.9, det_score_threshold=0.7, blur_threshold=10.0
    ) is True


# ── Task 4: filtro de pose ────────────────────────────────────────────────────

def test_is_good_quality_frame_rejeita_yaw_extremo():
    from app.services.face_service import is_good_quality_frame
    frame = make_bgr_frame()
    location = make_face_location(size=120)
    pose = np.array([0.0, 50.0, 0.0])  # yaw 50° > threshold padrão 40°
    assert is_good_quality_frame(
        location, frame, det_score=0.9, blur_threshold=10.0, pose=pose
    ) is False


def test_is_good_quality_frame_rejeita_pitch_extremo():
    from app.services.face_service import is_good_quality_frame
    frame = make_bgr_frame()
    location = make_face_location(size=120)
    pose = np.array([40.0, 0.0, 0.0])  # pitch 40° > threshold padrão 30°
    assert is_good_quality_frame(
        location, frame, det_score=0.9, blur_threshold=10.0, pose=pose
    ) is False


def test_is_good_quality_frame_aceita_pose_frontal():
    from app.services.face_service import is_good_quality_frame
    frame = make_bgr_frame()
    location = make_face_location(size=120)
    pose = np.array([5.0, 10.0, 3.0])  # yaw e pitch dentro dos limites
    assert is_good_quality_frame(
        location, frame, det_score=0.9, blur_threshold=10.0, pose=pose
    ) is True


def test_is_good_quality_frame_sem_pose_nao_filtra():
    """Sem pose fornecida, filtro de ângulo é ignorado."""
    from app.services.face_service import is_good_quality_frame
    frame = make_bgr_frame()
    location = make_face_location(size=120)
    assert is_good_quality_frame(
        location, frame, det_score=0.9, blur_threshold=10.0, pose=None
    ) is True


def test_extract_embeddings_descarta_face_de_perfil():
    from app.services.face_service import extract_embeddings
    face = make_mock_face(bbox=[10, 10, 130, 130], det_score=0.95)
    face.pose = np.array([0.0, 50.0, 0.0])  # yaw 50° > 40°
    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_get.return_value.get.return_value = [face]
        result = extract_embeddings(make_bgr_frame())
    assert result == []


def test_extract_embeddings_aceita_face_frontal():
    from app.services.face_service import extract_embeddings
    face = make_mock_face(bbox=[10, 10, 130, 130], det_score=0.95)
    face.pose = np.array([5.0, 10.0, 0.0])
    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_get.return_value.get.return_value = [face]
        result = extract_embeddings(make_bgr_frame())
    assert len(result) == 1


# ── extract_embeddings ────────────────────────────────────────────────────────

def test_extract_embeddings_no_face_returns_empty():
    from app.services.face_service import extract_embeddings

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = []
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_one_face_returns_one_tuple():
    from app.services.face_service import extract_embeddings

    face = make_mock_face(bbox=[10, 10, 130, 130], det_score=0.95)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 1
    embedding, location, det_score, bbox = result[0]
    assert embedding.shape == (512,)
    assert len(location) == 4  # (top, right, bottom, left)
    assert isinstance(det_score, float)
    assert bbox.shape == (4,)


def test_extract_embeddings_discards_low_det_score():
    from app.services.face_service import extract_embeddings

    face = make_mock_face(det_score=0.3)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_discards_small_face():
    from app.services.face_service import extract_embeddings

    face = make_mock_face(bbox=[0, 0, 20, 20], det_score=0.95)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_two_faces_returns_two():
    from app.services.face_service import extract_embeddings

    faces = [
        make_mock_face(bbox=[0, 0, 120, 120], det_score=0.95),
        make_mock_face(bbox=[200, 200, 320, 320], det_score=0.90),
    ]

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = faces
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 2


# ── bbox_to_location ──────────────────────────────────────────────────────────

def test_bbox_to_location_converts_correctly():
    from app.services.face_service import bbox_to_location

    # InsightFace bbox: [x1, y1, x2, y2] → (top=y1, right=x2, bottom=y2, left=x1)
    location = bbox_to_location(np.array([10.0, 20.0, 110.0, 120.0]))
    assert location == (20, 110, 120, 10)


# ── find_matching_person (coseno) ─────────────────────────────────────────────

def test_find_matching_empty_list_returns_none():
    from app.services.face_service import find_matching_person

    result_id, result_dist = find_matching_person(make_l2_embedding(), [])
    assert result_id is None
    assert result_dist is None


def test_find_matching_below_tolerance_returns_match():
    from app.services.face_service import find_matching_person

    query = make_l2_embedding()
    known = [(1, query.copy())]

    match_id, dist = find_matching_person(query, known, tolerance=0.4)

    assert match_id == 1
    assert dist is not None
    assert dist < 0.01


def test_find_matching_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    opposite = np.zeros(512, dtype=np.float32)
    opposite[1] = 1.0  # distância coseno = 1.0

    match_id, dist = find_matching_person(query, [(1, opposite)], tolerance=0.4)

    assert match_id is None


def test_find_matching_picks_closest():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    close = np.zeros(512, dtype=np.float32)
    close[0] = 0.99
    close[1] = 0.01
    close = close / np.linalg.norm(close)

    far = np.zeros(512, dtype=np.float32)
    far[0] = 0.7
    far[1] = 0.3
    far = far / np.linalg.norm(far)

    match_id, dist = find_matching_person(query, [(1, close), (2, far)], tolerance=0.4)
    assert match_id == 1


def test_find_matching_knn_majority_vote():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    emb_p1 = query.copy()

    emb_p2a = np.zeros(512, dtype=np.float32)
    emb_p2a[0] = 0.98
    emb_p2a[1] = 0.02
    emb_p2a = emb_p2a / np.linalg.norm(emb_p2a)

    emb_p2b = np.zeros(512, dtype=np.float32)
    emb_p2b[0] = 0.97
    emb_p2b[1] = 0.03
    emb_p2b = emb_p2b / np.linalg.norm(emb_p2b)

    known = [(1, emb_p1), (2, emb_p2a), (2, emb_p2b)]
    match_id, _ = find_matching_person(query, known, tolerance=0.4, k=3)
    assert match_id == 2


def test_find_matching_knn_ignores_neighbors_above_tolerance():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    close = np.zeros(512, dtype=np.float32)
    close[0] = 0.99
    close[1] = 0.01
    close = close / np.linalg.norm(close)

    far = np.zeros(512, dtype=np.float32)
    far[1] = 1.0  # dist coseno = 1.0

    match_id, dist = find_matching_person(query, [(1, close), (2, far)], tolerance=0.4, k=3)
    assert match_id == 1


def test_find_matching_uses_settings_knn_k_default():
    from app.services.face_service import find_matching_person
    import inspect

    params = inspect.signature(find_matching_person).parameters
    assert params["k"].default == settings.FACE_KNN_K


# ── get_face_app singleton ────────────────────────────────────────────────────

def test_get_face_app_returns_same_instance():
    from app.services import face_service

    face_service._face_app = None

    with patch("app.services.face_service.FaceAnalysis") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.prepare = MagicMock()
        mock_cls.return_value = mock_instance

        app1 = face_service.get_face_app()
        app2 = face_service.get_face_app()

    assert app1 is app2
    assert mock_cls.call_count == 1


# ── FaceTrack / FaceTracker ───────────────────────────────────────────────────

def test_face_tracker_aggregates_detections():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    emb = make_l2_embedding()
    frame = make_bgr_frame()

    tracker.add_detection(emb, make_face_location(), frame, timestamp=1.0)
    tracker.add_detection(emb, make_face_location(), frame, timestamp=2.0)

    tracks = tracker.flush()
    assert len(tracks) == 1
    assert tracks[0].sample_count == 2


def test_face_tracker_discards_short_tracks():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    emb = make_l2_embedding()
    frame = make_bgr_frame()

    tracker.add_detection(emb, make_face_location(), frame, timestamp=1.0)

    tracks = tracker.flush()
    assert len(tracks) == 0


def test_face_track_mean_embedding_is_l2_normalized():
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=0.0)
    frame = make_bgr_frame()
    for _ in range(3):
        emb = make_l2_embedding()
        track.add_frame_data(emb, make_face_location(), frame, timestamp=1.0)

    mean = track.mean_embedding()
    assert abs(np.linalg.norm(mean) - 1.0) < 1e-5


# ── Task 3: FaceTrack armazena crop, não frame completo ──────────────────────

def test_face_track_armazena_crop_nao_frame_completo():
    """_frames_data deve guardar crop da face, não o frame inteiro."""
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=0.0)
    big_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    location = (100, 200, 160, 140)  # top=100, right=200, bottom=160, left=140 → 60x60
    track.add_frame_data(make_l2_embedding(), location, big_frame, timestamp=1.0)

    stored = track._frames_data[0]
    assert "crop" in stored, "_frames_data deve ter chave 'crop'"
    assert stored["crop"].shape == (60, 60, 3), (
        f"Shape esperado (60,60,3), recebido {stored['crop'].shape}"
    )
    # NÃO deve guardar o frame completo
    assert "frame" not in stored, "_frames_data NÃO deve guardar o frame completo"


def test_face_track_get_best_crop_usa_crop_armazenado():
    """get_best_crop deve retornar o crop do frame com maior área facial."""
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=0.0)
    frame = make_bgr_frame()

    # face pequena 40x40
    track.add_frame_data(make_l2_embedding(), make_face_location(size=40), frame, timestamp=1.0)
    # face grande 120x120
    track.add_frame_data(make_l2_embedding(), make_face_location(size=120), frame, timestamp=2.0)

    crop = track.get_best_crop()
    assert crop.shape[:2] == (120, 120), (
        f"Melhor crop deve ser 120x120, recebido {crop.shape[:2]}"
    )


# ── Task 5: média ponderada por det_score ─────────────────────────────────────

def test_mean_embedding_pondera_por_det_score():
    """Frame com det_score alto deve ter mais peso no embedding médio."""
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=0.0)
    frame = make_bgr_frame()
    location = make_face_location()

    emb_strong = np.zeros(512, dtype=np.float32); emb_strong[0] = 1.0
    emb_weak   = np.zeros(512, dtype=np.float32); emb_weak[1] = 1.0

    # det_score alto → deve dominar o embedding
    track.add_frame_data(emb_strong, location, frame, timestamp=1.0, det_score=0.99)
    track.add_frame_data(emb_weak,   location, frame, timestamp=2.0, det_score=0.50)

    mean = track.mean_embedding()
    dot_strong = float(np.dot(mean, emb_strong))
    dot_weak   = float(np.dot(mean, emb_weak))
    assert dot_strong > dot_weak, (
        f"Embedding médio deve ser mais próximo de emb_strong "
        f"(dot_strong={dot_strong:.4f}, dot_weak={dot_weak:.4f})"
    )


def test_add_frame_data_aceita_det_score_opcional():
    """add_frame_data com det_score=1.0 default deve funcionar."""
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=0.0)
    frame = make_bgr_frame()
    # sem passar det_score — deve usar default 1.0
    track.add_frame_data(make_l2_embedding(), make_face_location(), frame, timestamp=1.0)
    assert track.sample_count == 1


# ── Task 6 V3: normalizar known_vecs em find_matching_person ─────────────────

def test_find_matching_normaliza_known_vecs_com_escala_pequena():
    """known_vecs com escala != 1 devem ser normalizados antes do dot product.
    Sem normalização: known=[0.1,0,0] → dot(query,known)=0.1 → dist=0.9 > threshold → falso neg.
    Com normalização: known=[1,0,0] → dot=1.0 → dist=0.0 → match correto."""
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0  # L2-normalizado

    known_small = np.zeros(512, dtype=np.float32)
    known_small[0] = 0.1  # mesma direção, escala 0.1 — sem normalizar: dist = 0.9 > 0.4

    person_id, dist = find_matching_person(query, [(99, known_small)], tolerance=0.4)

    assert person_id == 99, (
        "Embedding com mesma direção mas escala 0.1 deve ser reconhecido após normalização; "
        "sem normalização de known_vecs, dist coseno = 0.9 (falso negativo)"
    )
    assert dist is not None and dist < 0.05, f"dist coseno esperado ≈ 0, obtido {dist}"
