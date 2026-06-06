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
    """segundo_aproximado = frame_index // frame_interval."""
    from app.services.frame_service import extract_frames

    frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(90)]
    cap = make_mock_cap(fps=30.0, frames=frames)

    with patch("app.services.frame_service.cv2.VideoCapture", return_value=cap):
        results = list(extract_frames(Path("video.mp4"), fps_sample=1))

    seconds = [r[0] for r in results]
    assert seconds == [0, 1, 2]


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
