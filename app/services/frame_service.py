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
