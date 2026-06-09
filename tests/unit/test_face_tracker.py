from unittest.mock import patch

import numpy as np
import pytest


def make_embedding(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.random(128)


def make_location(size: int = 120) -> tuple:
    return (0, size, size, 0)


def make_frame() -> np.ndarray:
    return np.zeros((480, 640, 3), dtype=np.uint8)


# ── FaceTrack ─────────────────────────────────────────────────────────────────

def test_face_track_aggregates_mean_embedding():
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=1.0)
    emb1, emb2 = make_embedding(1), make_embedding(2)
    track.add_frame_data(emb1, make_location(), make_frame(), timestamp=1.0)
    track.add_frame_data(emb2, make_location(), make_frame(), timestamp=2.0)

    raw_mean = np.mean([emb1, emb2], axis=0).astype(np.float32)
    expected = raw_mean / np.linalg.norm(raw_mean)
    assert np.allclose(track.mean_embedding(), expected)


def test_face_track_sample_count():
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=1.0)
    track.add_frame_data(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    track.add_frame_data(make_embedding(), make_location(), make_frame(), timestamp=2.0)

    assert track.sample_count == 2


def test_face_track_updates_last_seen():
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=1.0)
    track.add_frame_data(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    track.add_frame_data(make_embedding(), make_location(), make_frame(), timestamp=3.5)

    assert track.last_seen == 3.5


def test_face_track_get_best_crop_picks_largest_face():
    from app.services.face_service import FaceTrack

    track = FaceTrack(start_time=1.0)
    small_frame = make_frame()
    big_frame = make_frame()
    track.add_frame_data(make_embedding(1), make_location(60), small_frame, timestamp=1.0)
    track.add_frame_data(make_embedding(2), make_location(150), big_frame, timestamp=2.0)

    crop = track.get_best_crop()

    assert crop.shape[:2] == (150, 150)


# ── FaceTracker ───────────────────────────────────────────────────────────────

def test_face_tracker_creates_track_on_first_detection():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)

    assert tracker.active_track is not None
    assert tracker.active_track.sample_count == 1


def test_face_tracker_continues_track_within_gap_tolerance():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=2.5)

    assert tracker.active_track.sample_count == 2
    assert len(tracker.closed_tracks) == 0


def test_face_tracker_closes_track_when_gap_exceeds_tolerance():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=1)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.5)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=10.0)

    assert len(tracker.closed_tracks) == 1
    assert tracker.closed_tracks[0].sample_count == 2
    assert tracker.active_track.sample_count == 1


def test_face_tracker_discards_tracks_below_min_samples():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=3)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=10.0)

    assert tracker.closed_tracks == []


def test_face_tracker_flush_closes_active_track():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=1)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=2.0)

    closed = tracker.flush()

    assert tracker.active_track is None
    assert len(closed) == 1
    assert closed[0].sample_count == 2


def test_face_tracker_flush_discards_short_track():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=5)
    tracker.add_detection(make_embedding(), make_location(), make_frame(), timestamp=1.0)

    closed = tracker.flush()

    assert tracker.active_track is None
    assert closed == []


def test_face_tracker_uses_settings_defaults():
    from app.services.face_service import FaceTracker
    from app.core.settings import settings

    tracker = FaceTracker()

    assert tracker.gap_tolerance == settings.FACE_TRACK_GAP_TOLERANCE
    assert tracker.min_samples == settings.FACE_TRACK_MIN_SAMPLES


# ── Task 1: multi-face com IoU ────────────────────────────────────────────────

def make_l2_emb(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.random(512).astype(np.float32)
    return v / np.linalg.norm(v)


def test_iou_retorna_zero_para_bboxes_sem_sobreposicao():
    from app.services.face_service import _iou

    a = np.array([0, 0, 100, 100], dtype=np.float32)
    b = np.array([200, 0, 300, 100], dtype=np.float32)
    assert _iou(a, b) == 0.0


def test_iou_retorna_um_para_bboxes_identicas():
    from app.services.face_service import _iou

    a = np.array([10, 20, 110, 120], dtype=np.float32)
    assert abs(_iou(a, a) - 1.0) < 1e-6


def test_iou_parcial():
    from app.services.face_service import _iou

    a = np.array([0, 0, 100, 100], dtype=np.float32)
    b = np.array([50, 0, 150, 100], dtype=np.float32)
    iou = _iou(a, b)
    assert 0.0 < iou < 1.0


def test_tracker_cria_dois_tracks_para_duas_faces_simultaneas():
    """Duas faces sem sobreposição → dois tracks separados."""
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=1)
    bbox1 = np.array([0, 0, 100, 100], dtype=np.float32)
    bbox2 = np.array([200, 0, 300, 100], dtype=np.float32)
    frame = make_frame()
    loc = (0, 100, 100, 0)

    tracker.add_detection(make_l2_emb(1), loc, frame, timestamp=1.0, bbox=bbox1)
    tracker.add_detection(make_l2_emb(2), loc, frame, timestamp=1.0, bbox=bbox2)

    assert len(tracker.active_tracks) == 2


def test_tracker_associa_face_ao_track_com_maior_iou():
    """Segunda detecção na mesma posição deve estender o track existente."""
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=5.0, min_samples=1)
    bbox = np.array([10, 10, 110, 110], dtype=np.float32)
    frame = make_frame()
    loc = (10, 110, 110, 10)

    tracker.add_detection(make_l2_emb(1), loc, frame, timestamp=1.0, bbox=bbox)
    tracker.add_detection(make_l2_emb(2), loc, frame, timestamp=2.0, bbox=bbox)

    assert len(tracker.active_tracks) == 1
    _, track = tracker.active_tracks[0]
    assert track.sample_count == 2


def test_close_stale_tracks_fecha_tracks_expirados():
    """_close_stale_tracks deve mover tracks expirados para closed_tracks."""
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=1)
    bbox = np.array([0, 0, 100, 100], dtype=np.float32)
    frame = make_frame()
    loc = (0, 100, 100, 0)

    tracker.add_detection(make_l2_emb(1), loc, frame, timestamp=0.0, bbox=bbox)
    # detectar t=10.0 — gap 10 > 2.0
    tracker._close_stale_tracks(current_time=10.0)

    assert len(tracker.closed_tracks) == 1
    assert len(tracker.active_tracks) == 0


def test_flush_com_multiple_tracks():
    """flush deve fechar todos os tracks ativos."""
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=5.0, min_samples=1)
    frame = make_frame()
    loc = (0, 100, 100, 0)
    bbox1 = np.array([0, 0, 100, 100], dtype=np.float32)
    bbox2 = np.array([200, 0, 300, 100], dtype=np.float32)

    tracker.add_detection(make_l2_emb(1), loc, frame, timestamp=1.0, bbox=bbox1)
    tracker.add_detection(make_l2_emb(2), loc, frame, timestamp=1.0, bbox=bbox2)

    closed = tracker.flush()
    assert len(closed) == 2
    assert len(tracker.active_tracks) == 0
