from pathlib import Path
from unittest.mock import MagicMock, patch, call

import numpy as np
import pytest


def make_mock_cap(fps: float, frames: list[np.ndarray]) -> MagicMock:
    """Helper: simula cv2.VideoCapture com lista de frames."""
    cap = MagicMock()
    cap.isOpened.return_value = True
    cap.get.return_value = fps  # CAP_PROP_FPS

    read_returns = [(True, f) for f in frames] + [(False, None)]
    cap.read.side_effect = read_returns
    return cap


def test_file_not_found_raises():
    from app.services.frame_service import extract_frames
    with patch("app.services.frame_service.cv2.VideoCapture") as mock_cap_cls:
        cap = MagicMock()
        cap.isOpened.return_value = False
        mock_cap_cls.return_value = cap

        with pytest.raises(FileNotFoundError):
            list(extract_frames(Path("nao_existe.mp4")))


def test_30fps_sample1_yields_one_per_second():
    """30 FPS vídeo, sample=1 → frame_interval=30 → 1 frame/s."""
    from app.services.frame_service import extract_frames

    frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(60)]
    cap = make_mock_cap(fps=30.0, frames=frames)

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=1))

    # 60 frames @ interval 30 → frames 0 e 30 → 2 resultados
    assert len(results) == 2


def test_second_approximation_correct():
    """Para 30fps / fps_sample=1: frames 0, 30, 60 → timestamps 0.0s, 1.0s, 2.0s."""
    from app.services.frame_service import extract_frames

    frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(90)]
    cap = make_mock_cap(fps=30.0, frames=frames)

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=1))

    timestamps = [r[0] for r in results]
    assert len(timestamps) == 3
    assert abs(timestamps[0] - 0.0) < 0.01
    assert abs(timestamps[1] - 1.0) < 0.01
    assert abs(timestamps[2] - 2.0) < 0.01


def test_release_called_on_success():
    from app.services.frame_service import extract_frames

    frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(30)]
    cap = make_mock_cap(fps=30.0, frames=frames)

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        list(extract_frames(Path("video.mp4")))

    cap.release.assert_called_once()


def test_release_called_on_error():
    from app.services.frame_service import extract_frames

    with patch("app.services.frame_service.cv2.VideoCapture") as mock_cap_cls:
        cap = MagicMock()
        cap.isOpened.return_value = False
        mock_cap_cls.return_value = cap

        with pytest.raises(FileNotFoundError):
            list(extract_frames(Path("nao_existe.mp4")))

    cap.release.assert_called_once()


def test_yields_ndarray_frames():
    from app.services.frame_service import extract_frames

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cap = make_mock_cap(fps=1.0, frames=[frame])

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=1))

    assert len(results) == 1
    assert isinstance(results[0][1], np.ndarray)


# ── Task 3: timestamps devem ser segundos reais, não índice de amostra ────────

def test_timestamps_sao_segundos_reais_nao_indice():
    """Para 30fps / fps_sample=2: frame_interval=15.
    frame 0 → 0.0s, frame 15 → 0.5s, frame 30 → 1.0s.
    Código antigo retornava índices 0, 1, 2 (2× o valor correto).
    """
    from app.services.frame_service import extract_frames

    frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(45)]
    cap = make_mock_cap(fps=30.0, frames=frames)

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=2))

    timestamps = [r[0] for r in results]
    # 45 frames @ interval 15 → frames 0, 15, 30 → timestamps 0.0, 0.5, 1.0
    assert len(results) == 3
    assert abs(timestamps[0] - 0.0) < 0.01, f"frame 0 deve ser 0.0s, obtido {timestamps[0]}"
    assert abs(timestamps[1] - 0.5) < 0.01, f"frame 15 deve ser 0.5s, obtido {timestamps[1]} (bug: retorna 1.0)"
    assert abs(timestamps[2] - 1.0) < 0.01, f"frame 30 deve ser 1.0s, obtido {timestamps[2]} (bug: retorna 2.0)"


def test_timestamp_tipo_float():
    """extract_frames deve retornar float, não int."""
    from app.services.frame_service import extract_frames

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cap = make_mock_cap(fps=30.0, frames=[frame])

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=1))

    assert isinstance(results[0][0], float), (
        f"timestamp deve ser float, obtido {type(results[0][0])}"
    )


def test_has_motion_no_motion():
    from app.services.frame_service import has_motion
    frame1 = np.zeros((100, 100), dtype=np.uint8)
    frame2 = np.zeros((100, 100), dtype=np.uint8)
    
    motion_detected, ratio = has_motion(frame1, frame2, threshold=25, area_ratio=0.005)
    assert not motion_detected
    assert ratio == 0.0


def test_has_motion_with_motion():
    from app.services.frame_service import has_motion
    frame1 = np.zeros((100, 100), dtype=np.uint8)
    frame2 = np.zeros((100, 100), dtype=np.uint8)
    frame2[45:55, 45:55] = 255
    
    motion_detected, ratio = has_motion(frame1, frame2, threshold=25, area_ratio=0.005)
    assert motion_detected
    assert ratio == 0.01


def test_has_motion_below_area_ratio():
    from app.services.frame_service import has_motion
    frame1 = np.zeros((100, 100), dtype=np.uint8)
    frame2 = np.zeros((100, 100), dtype=np.uint8)
    frame2[47:52, 47:52] = 255
    
    motion_detected, ratio = has_motion(frame1, frame2, threshold=25, area_ratio=0.005)
    assert not motion_detected
    assert ratio == 0.0025

