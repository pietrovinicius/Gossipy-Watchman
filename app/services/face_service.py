import logging
import cv2
import face_recognition
import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)


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
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    return bool(variance >= blur_threshold)


def extract_embeddings(frame: np.ndarray) -> list[tuple[np.ndarray, tuple]]:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(
        rgb,
        number_of_times_to_upsample=settings.FACE_UPSAMPLE,
        model=settings.FACE_DETECTION_MODEL,
    )
    logger.debug(
        f"[EXTRACT] faces_detectadas={len(locations)} "
        f"model={settings.FACE_DETECTION_MODEL} "
        f"upsample={settings.FACE_UPSAMPLE}"
    )

    good_locations = [
        loc for loc in locations
        if is_good_quality_frame(loc, frame, settings.FACE_MIN_SIZE_PX)
    ]
    logger.debug(
        f"[EXTRACT] faces_boa_qualidade={len(good_locations)} "
        f"descartadas={len(locations) - len(good_locations)}"
    )
    if not good_locations:
        return []

    encodings = face_recognition.face_encodings(rgb, good_locations)
    logger.debug(f"[EXTRACT] embeddings_gerados={len(encodings)}")
    for i, enc in enumerate(encodings):
        logger.debug(
            f"[EXTRACT] embedding[{i}] shape={enc.shape} dtype={enc.dtype} "
            f"norm={np.linalg.norm(enc):.4f}"
        )
    return list(zip(encodings, good_locations))


def find_matching_person(
    embedding: np.ndarray,
    known_embeddings: list[tuple[int, np.ndarray]],
    tolerance: float = settings.FACE_RECOGNITION_TOLERANCE,
) -> tuple[int | None, float | None]:
    if not known_embeddings:
        return None, None

    known_vecs = [emb for _, emb in known_embeddings]
    distances: np.ndarray = face_recognition.face_distance(known_vecs, embedding)

    logger.debug(
        f"[MATCH] embedding_buscado shape={embedding.shape} dtype={embedding.dtype} "
        f"norm={np.linalg.norm(embedding):.4f}"
    )
    logger.debug(
        f"[MATCH] comparando contra {len(known_vecs)} embeddings conhecidos "
        f"threshold={tolerance:.4f}"
    )

    for i, (person_id, dist) in enumerate(zip([pid for pid, _ in known_embeddings], distances)):
        logger.debug(
            f"[MATCH] person_id={person_id} distancia={dist:.4f} "
            f"aceito={'SIM' if dist < tolerance else 'NAO'}"
        )

    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])

    if best_dist > tolerance:
        logger.info(
            f"[MATCH REJEITADO] melhor_distancia={best_dist:.4f} > "
            f"threshold={tolerance:.4f} → nova_pessoa"
        )
        return None, None

    person_id = known_embeddings[best_idx][0]
    logger.info(
        f"[MATCH ACEITO] person_id={person_id} distancia={best_dist:.4f} < "
        f"threshold={tolerance:.4f}"
    )
    return person_id, best_dist
