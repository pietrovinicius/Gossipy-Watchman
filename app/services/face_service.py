import logging
import cv2
import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Singletons para os modelos do OpenCV
_detector = None
_recognizer = None
_current_input_size = None


def get_face_models(input_size: tuple[int, int]):
    """
    Inicializa e gerencia o cache para FaceDetectorYN e FaceRecognizerSF do OpenCV.
    """
    global _detector, _recognizer, _current_input_size
    
    from app.core.model_downloader import YUNET_PATH, SFACE_PATH, ensure_models_downloaded
    ensure_models_downloaded()
    
    if _detector is None:
        logger.info(f"Carregando FaceDetectorYN a partir de {YUNET_PATH}")
        _detector = cv2.FaceDetectorYN.create(
            model=str(YUNET_PATH),
            config="",
            input_size=input_size,
            score_threshold=0.8,
            nms_threshold=0.3
        )
        _current_input_size = input_size
    elif _current_input_size != input_size:
        _detector.setInputSize(input_size)
        _current_input_size = input_size
        
    if _recognizer is None:
        logger.info(f"Carregando FaceRecognizerSF a partir de {SFACE_PATH}")
        _recognizer = cv2.FaceRecognizerSF.create(
            model=str(SFACE_PATH),
            config=""
        )
        
    return _detector, _recognizer


def is_good_quality_frame(
    location: tuple[int, int, int, int],
    frame: np.ndarray,
    min_face_size: int = settings.FACE_MIN_SIZE_PX,
    blur_threshold: float = settings.FACE_BLUR_THRESHOLD,
) -> bool:
    top, right, bottom, left = location
    width = right - left
    height = bottom - top

    if width < min_face_size or height < min_face_size:
        return False

    face_crop = frame[top:bottom, left:right]
    if face_crop.size == 0:
        return False
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    return bool(variance >= blur_threshold)


def extract_embeddings(frame: np.ndarray) -> list[tuple[np.ndarray, tuple]]:
    height, width = frame.shape[:2]
    try:
        detector, recognizer = get_face_models((width, height))
    except Exception as e:
        logger.error(f"Erro ao carregar modelos de detecção/reconhecimento: {e}")
        return []

    _, faces = detector.detect(frame)
    if faces is None:
        logger.debug("[EXTRACT] faces_detectadas=0")
        return []

    logger.debug(f"[EXTRACT] faces_detectadas={len(faces)}")
    
    results = []
    for face in faces:
        # face contem as coordenadas no formato x, y, w, h em face[0:4]
        x, y, w, h = face[0:4]
        top = int(max(0, y))
        left = int(max(0, x))
        bottom = int(min(height, y + h))
        right = int(min(width, x + w))
        location = (top, right, bottom, left)
        
        if not is_good_quality_frame(location, frame, settings.FACE_MIN_SIZE_PX):
            continue
            
        try:
            # Alinha e recorta a face usando os landmarks retornados pelo YuNet
            aligned = recognizer.alignCrop(frame, face)
            feat = recognizer.feature(aligned)
            embedding = feat.flatten().astype(np.float64)
            results.append((embedding, location))
        except Exception as e:
            logger.error(f"Erro ao extrair embedding de face: {e}")
            
    logger.debug(f"[EXTRACT] embeddings_gerados={len(results)}")
    return results


class FaceTrack:
    """Agrega detecções de uma mesma aparição contínua de rosto no vídeo."""

    def __init__(self, start_time: float):
        self.start_time = start_time
        self.last_seen = start_time
        self.embeddings: list[np.ndarray] = []
        self._frames_data: list[dict] = []

    def add_frame_data(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
    ) -> None:
        self.embeddings.append(embedding)
        self._frames_data.append(
            {"location": location, "frame": frame, "timestamp": timestamp}
        )
        self.last_seen = timestamp

    @property
    def sample_count(self) -> int:
        return len(self.embeddings)

    def mean_embedding(self) -> np.ndarray:
        return np.mean(self.embeddings, axis=0)

    def get_best_crop(self) -> np.ndarray:
        """Recorte do frame com maior área de rosto (proxy de melhor qualidade)."""
        def face_area(data: dict) -> int:
            top, right, bottom, left = data["location"]
            return (right - left) * (bottom - top)

        best = max(self._frames_data, key=face_area)
        top, right, bottom, left = best["location"]
        return best["frame"][top:bottom, left:right]


class FaceTracker:
    """Agrupa detecções consecutivas em tracks, descartando aparições muito curtas."""

    def __init__(
        self,
        gap_tolerance: float = settings.FACE_TRACK_GAP_TOLERANCE,
        min_samples: int = settings.FACE_TRACK_MIN_SAMPLES,
    ):
        self.gap_tolerance = gap_tolerance
        self.min_samples = min_samples
        self.active_track: FaceTrack | None = None
        self.closed_tracks: list[FaceTrack] = []

    def add_detection(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
    ) -> None:
        if self.active_track is None:
            self.active_track = FaceTrack(start_time=timestamp)
        elif timestamp - self.active_track.last_seen > self.gap_tolerance:
            self._close_active_track()
            self.active_track = FaceTrack(start_time=timestamp)

        self.active_track.add_frame_data(embedding, location, frame, timestamp)

    def _close_active_track(self) -> None:
        if self.active_track is not None and self.active_track.sample_count >= self.min_samples:
            self.closed_tracks.append(self.active_track)
            logger.debug(
                f"[TRACKER] track fechado start={self.active_track.start_time:.1f}s "
                f"last_seen={self.active_track.last_seen:.1f}s "
                f"samples={self.active_track.sample_count}"
            )
        elif self.active_track is not None:
            logger.debug(
                f"[TRACKER] track descartado (samples={self.active_track.sample_count} "
                f"< min_samples={self.min_samples})"
            )
        self.active_track = None

    def flush(self) -> list[FaceTrack]:
        self._close_active_track()
        return self.closed_tracks


def find_matching_person(
    embedding: np.ndarray,
    known_embeddings: list[tuple[int, np.ndarray]],
    tolerance: float = settings.FACE_RECOGNITION_TOLERANCE,
    k: int = settings.FACE_KNN_K,
) -> tuple[int | None, float | None]:
    """Vota entre os k vizinhos mais próximos (dentro do tolerance) em vez de
    aceitar cegamente o vizinho mais próximo isolado (argmin) — reduz falsos
    positivos causados por pessoas super-representadas no banco de embeddings."""
    if not known_embeddings:
        return None, None

    known_vecs = [emb for _, emb in known_embeddings]
    person_ids = [pid for pid, _ in known_embeddings]
    
    # Cálculo de distância Euclidiana via NumPy
    known_vecs_arr = np.array(known_vecs)
    distances: np.ndarray = np.linalg.norm(known_vecs_arr - embedding, axis=1)

    logger.debug(
        f"[MATCH] embedding_buscado shape={embedding.shape} dtype={embedding.dtype} "
        f"norm={np.linalg.norm(embedding):.4f}"
    )
    logger.debug(
        f"[MATCH] comparando contra {len(known_vecs)} embeddings conhecidos "
        f"k={k} threshold={tolerance:.4f}"
    )

    candidates = sorted(zip(person_ids, distances), key=lambda pair: pair[1])
    within_tolerance = [(pid, float(dist)) for pid, dist in candidates if dist <= tolerance]

    if not within_tolerance:
        logger.info(
            f"[MATCH REJEITADO] melhor_distancia={float(candidates[0][1]):.4f} > "
            f"threshold={tolerance:.4f} → nova_pessoa"
        )
        return None, None

    top_k = within_tolerance[:k]
    votes: dict[int, list[float]] = {}
    for pid, dist in top_k:
        votes.setdefault(pid, []).append(dist)
        logger.debug(f"[MATCH] voto person_id={pid} distancia={dist:.4f}")

    winner_id, winner_votes = max(votes.items(), key=lambda item: (len(item[1]), -min(item[1])))
    winner_dist = min(winner_votes)

    logger.info(
        f"[MATCH ACEITO] person_id={winner_id} distancia={winner_dist:.4f} "
        f"votos={len(winner_votes)}/{len(top_k)} < threshold={tolerance:.4f}"
    )
    return winner_id, winner_dist
