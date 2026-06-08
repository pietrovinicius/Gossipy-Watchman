from collections.abc import Generator
from pathlib import Path

import cv2
import numpy as np

from app.core.settings import settings


def extract_frames(
    video_path: Path,
    fps_sample: int = settings.FRAMES_PER_SECOND_SAMPLE,
) -> Generator[tuple[int, np.ndarray], None, None]:
    cap = cv2.VideoCapture(str(video_path))
    try:
        if not cap.isOpened():
            raise FileNotFoundError(f"Não foi possível abrir o vídeo: {video_path}")

        fps_real: float = cap.get(cv2.CAP_PROP_FPS)
        frame_interval: int = max(1, round(fps_real / fps_sample))

        frame_index = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % frame_interval == 0:
                segundo = frame_index // frame_interval
                yield segundo, frame
            frame_index += 1
    finally:
        cap.release()


def has_motion(
    prev_gray: np.ndarray,
    curr_gray: np.ndarray,
    threshold: int = settings.MOTION_GATING_THRESHOLD,
    area_ratio: float = settings.MOTION_GATING_AREA_RATIO,
) -> tuple[bool, float]:
    """
    Detecta movimento significativo entre dois frames em escala de cinza.
    Aplica diferença absoluta, binarização, dilatação e conta pixels de mudança.
    
    Retorna (has_motion: bool, motion_ratio: float).
    """
    # Diferença absoluta
    frame_diff = cv2.absdiff(prev_gray, curr_gray)
    
    # Threshold binário
    _, thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)
    
    # Contagem de pixels brancos
    motion_pixels = cv2.countNonZero(thresh)
    total_pixels = curr_gray.shape[0] * curr_gray.shape[1]
    
    ratio = motion_pixels / total_pixels
    return bool(ratio >= area_ratio), ratio

