import logging

import cv2
import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)

try:
    from insightface.app import FaceAnalysis
except ImportError:  # pragma: no cover
    FaceAnalysis = None  # type: ignore

_face_app = None


def get_face_app():
    global _face_app
    if _face_app is None:
        if FaceAnalysis is None:
            raise RuntimeError("insightface não está instalado")
        _face_app = FaceAnalysis(
            name=settings.INSIGHTFACE_MODEL,
            providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
        )
        _face_app.prepare(
            ctx_id=0,
            det_size=(settings.INSIGHTFACE_DET_SIZE, settings.INSIGHTFACE_DET_SIZE),
        )
        logger.info(
            "InsightFace inicializado: model=%s det_size=%d",
            settings.INSIGHTFACE_MODEL,
            settings.INSIGHTFACE_DET_SIZE,
        )
    return _face_app


def bbox_to_location(bbox: np.ndarray) -> tuple[int, int, int, int]:
    """Converte bbox InsightFace [x1,y1,x2,y2] → (top, right, bottom, left)."""
    x1, y1, x2, y2 = bbox
    return (int(y1), int(x2), int(y2), int(x1))


def is_good_quality_frame(
    location: tuple[int, int, int, int],
    frame: np.ndarray,
    min_face_size: int = settings.FACE_MIN_SIZE_PX,
    blur_threshold: float = settings.FACE_BLUR_THRESHOLD,
    det_score: float = 1.0,
    det_score_threshold: float = settings.INSIGHTFACE_DET_SCORE,
    pose: np.ndarray | None = None,
    max_yaw_deg: float = settings.FACE_MAX_YAW_DEG,
    max_pitch_deg: float = settings.FACE_MAX_PITCH_DEG,
) -> bool:
    top, right, bottom, left = location
    width = right - left
    height = bottom - top

    if width < min_face_size or height < min_face_size:
        return False

    if det_score < det_score_threshold:
        return False

    if pose is not None:
        pitch, yaw = float(pose[0]), float(pose[1])
        if abs(yaw) > max_yaw_deg or abs(pitch) > max_pitch_deg:
            return False

    face_crop = frame[top:bottom, left:right]
    if face_crop.size == 0:
        return False
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    return bool(variance >= blur_threshold)


def extract_embeddings(
    frame: np.ndarray,
) -> list[tuple[np.ndarray, tuple, float, np.ndarray]]:
    """Retorna lista de (embedding, location, det_score, bbox) por face detectada."""
    app = get_face_app()
    faces = app.get(frame)

    logger.debug("[EXTRACT] faces_detectadas=%d", len(faces))

    result = []
    for face in faces:
        location = bbox_to_location(face.bbox)
        score = float(face.det_score)
        pose = face.pose if hasattr(face, "pose") else None
        if not is_good_quality_frame(location, frame, det_score=score, pose=pose):
            continue
        result.append((face.embedding, location, score, face.bbox.copy()))

    logger.debug(
        "[EXTRACT] faces_boa_qualidade=%d descartadas=%d",
        len(result),
        len(faces) - len(result),
    )
    return result


def _iou(bbox_a: np.ndarray, bbox_b: np.ndarray) -> float:
    """IoU entre dois bboxes [x1, y1, x2, y2]."""
    ax1, ay1, ax2, ay2 = float(bbox_a[0]), float(bbox_a[1]), float(bbox_a[2]), float(bbox_a[3])
    bx1, by1, bx2, by2 = float(bbox_b[0]), float(bbox_b[1]), float(bbox_b[2]), float(bbox_b[3])
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


class FaceTrack:
    """Agrega detecções de uma mesma aparição contínua de rosto no vídeo."""

    def __init__(self, start_time: float):
        self.start_time = start_time
        self.last_seen = start_time
        self.embeddings: list[np.ndarray] = []
        self._det_scores: list[float] = []
        self._frames_data: list[dict] = []

    def add_frame_data(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
        det_score: float = 1.0,
    ) -> None:
        top, right, bottom, left = location
        crop = frame[top:bottom, left:right].copy()
        area = (right - left) * (bottom - top)
        self.embeddings.append(embedding)
        self._det_scores.append(det_score)
        self._frames_data.append({"crop": crop, "area": area, "timestamp": timestamp})
        self.last_seen = timestamp

    @property
    def sample_count(self) -> int:
        return len(self.embeddings)

    def mean_embedding(self) -> np.ndarray:
        weights = np.array(self._det_scores, dtype=np.float32)
        embs = np.array(self.embeddings, dtype=np.float32)
        mean = np.average(embs, axis=0, weights=weights).astype(np.float32)
        norm = np.linalg.norm(mean)
        return mean / norm if norm > 0 else mean

    def get_best_crop(self) -> np.ndarray:
        best = max(self._frames_data, key=lambda d: d["area"])
        return best["crop"]


class FaceTracker:
    """Agrupa detecções consecutivas em tracks por IoU, suportando múltiplas faces simultâneas."""

    def __init__(
        self,
        gap_tolerance: float = settings.FACE_TRACK_GAP_TOLERANCE,
        min_samples: int = settings.FACE_TRACK_MIN_SAMPLES,
        iou_threshold: float = settings.FACE_TRACK_IOU_THRESHOLD,
    ):
        self.gap_tolerance = gap_tolerance
        self.min_samples = min_samples
        self.iou_threshold = iou_threshold
        self.active_tracks: list[tuple[np.ndarray, FaceTrack]] = []
        self.closed_tracks: list[FaceTrack] = []

    @property
    def active_track(self) -> FaceTrack | None:
        """Compatibilidade retroativa: retorna o único track ativo, ou None."""
        non_expired = [t for _, t in self.active_tracks]
        return non_expired[0] if len(non_expired) == 1 else None

    def add_detection(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
        det_score: float = 1.0,
        bbox: np.ndarray | None = None,
    ) -> None:
        best_idx = -1
        best_iou = 0.0

        if bbox is not None:
            for i, (last_bbox, track) in enumerate(self.active_tracks):
                iou = _iou(last_bbox, bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_idx = i
        else:
            # Modo legado (sem bbox): associar ao primeiro track ativo disponível
            if self.active_tracks:
                best_idx = 0
                best_iou = 1.0

        if best_iou >= self.iou_threshold and best_idx >= 0:
            last_bbox, track = self.active_tracks[best_idx]
            track.add_frame_data(embedding, location, frame, timestamp, det_score=det_score)
            if bbox is not None:
                self.active_tracks[best_idx] = (bbox, track)
        else:
            new_track = FaceTrack(start_time=timestamp)
            new_track.add_frame_data(embedding, location, frame, timestamp, det_score=det_score)
            placeholder = bbox if bbox is not None else np.zeros(4, dtype=np.float32)
            self.active_tracks.append((placeholder, new_track))
            logger.debug("[TRACKER] novo track iniciado em t=%.1fs", timestamp)

    def _close_stale_tracks(self, current_time: float) -> None:
        still_active = []
        for last_bbox, track in self.active_tracks:
            if current_time - track.last_seen > self.gap_tolerance:
                if track.sample_count >= self.min_samples:
                    self.closed_tracks.append(track)
                    logger.debug(
                        "[TRACKER] track fechado start=%.1fs last_seen=%.1fs samples=%d",
                        track.start_time, track.last_seen, track.sample_count,
                    )
                else:
                    logger.debug(
                        "[TRACKER] track descartado samples=%d < min_samples=%d",
                        track.sample_count, self.min_samples,
                    )
            else:
                still_active.append((last_bbox, track))
        self.active_tracks = still_active

    def flush(self) -> list[FaceTrack]:
        for _, track in self.active_tracks:
            if track.sample_count >= self.min_samples:
                self.closed_tracks.append(track)
            else:
                logger.debug(
                    "[TRACKER] track descartado no flush samples=%d < min_samples=%d",
                    track.sample_count, self.min_samples,
                )
        self.active_tracks = []
        return self.closed_tracks


def find_matching_person(
    embedding: np.ndarray,
    known_embeddings: list[tuple[int, np.ndarray]],
    tolerance: float = settings.FACE_RECOGNITION_TOLERANCE,
    k: int = settings.FACE_KNN_K,
) -> tuple[int | None, float | None]:
    """Vota entre os k vizinhos mais próximos usando distância coseno.

    ArcFace embeddings são L2-normalizados → coseno = 1 - dot(a, b).
    """
    if not known_embeddings:
        return None, None

    known_vecs = np.array([emb for _, emb in known_embeddings], dtype=np.float32)
    person_ids = [pid for pid, _ in known_embeddings]

    # Normalizar known_vecs por segurança (embeddings médios ou carregados de disco
    # podem ter escala ligeiramente diferente de 1.0)
    norms = np.linalg.norm(known_vecs, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    known_vecs = known_vecs / norms

    q = embedding.astype(np.float32)
    q_norm = np.linalg.norm(q)
    if q_norm > 0:
        q = q / q_norm

    dots = known_vecs @ q
    distances = (1.0 - dots).tolist()

    logger.debug(
        "[MATCH] comparando contra %d embeddings k=%d threshold=%.4f",
        len(known_vecs),
        k,
        tolerance,
    )

    candidates = sorted(zip(person_ids, distances), key=lambda pair: pair[1])
    within_tolerance = [
        (pid, float(dist)) for pid, dist in candidates if dist <= tolerance
    ]

    if not within_tolerance:
        logger.info(
            "[MATCH REJEITADO] melhor_distancia=%.4f > threshold=%.4f → nova_pessoa",
            float(candidates[0][1]),
            tolerance,
        )
        return None, None

    top_k = within_tolerance[:k]
    votes: dict[int, list[float]] = {}
    for pid, dist in top_k:
        votes.setdefault(pid, []).append(dist)

    winner_id, winner_votes = max(
        votes.items(), key=lambda item: (len(item[1]), -min(item[1]))
    )
    winner_dist = min(winner_votes)

    logger.info(
        "[MATCH ACEITO] person_id=%d distancia=%.4f votos=%d/%d threshold=%.4f",
        winner_id,
        winner_dist,
        len(winner_votes),
        len(top_k),
        tolerance,
    )
    return winner_id, winner_dist
