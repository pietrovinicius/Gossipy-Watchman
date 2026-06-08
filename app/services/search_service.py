import logging
import time

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.person import Person
from app.services import person_service
from app.services.face_service import get_face_app

logger = logging.getLogger(__name__)


def search_by_face(
    db: Session,
    image_bytes: bytes,
    top_k: int = 5,
    tolerance: float | None = None,
) -> list[dict]:
    if tolerance is None:
        tolerance = settings.FACE_RECOGNITION_TOLERANCE

    t0 = time.perf_counter()

    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if frame is None:
        return []

    faces = get_face_app().get(frame)
    if not faces:
        return []

    def _area(face) -> float:
        x1, y1, x2, y2 = face.bbox
        return (x2 - x1) * (y2 - y1)

    best_face = max(faces, key=_area)
    query_embedding = best_face.embedding  # L2-normalized ArcFace 512-dim

    known = person_service.get_all_embeddings(db)
    if not known:
        return []

    results: list[dict] = []
    for pid, emb in known:
        dist = float(1.0 - np.dot(query_embedding, emb))
        if dist > tolerance:
            continue
        person = db.get(Person, pid)
        if person is None:
            continue
        results.append({
            "person_id": pid,
            "person_name": person.name,
            "distance": dist,
            "confidence_pct": int((1.0 - dist) * 100),
        })

    results.sort(key=lambda r: r["distance"])
    elapsed = time.perf_counter() - t0
    logger.info("[SEARCH] %.3fs → %d resultados", elapsed, len(results))
    return results[:top_k]
