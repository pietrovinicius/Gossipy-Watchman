import logging
import time
from io import BytesIO

import cv2
import face_recognition
import numpy as np
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.person import Person
from app.services import person_service

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

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    if not locations:
        return []

    # pick largest face by area
    def _area(loc: tuple) -> int:
        top, right, bottom, left = loc
        return (bottom - top) * (right - left)

    best_idx = max(range(len(locations)), key=lambda i: _area(locations[i]))
    encodings = face_recognition.face_encodings(rgb, known_face_locations=locations)
    query_embedding = encodings[best_idx]

    known = person_service.get_all_embeddings(db)
    if not known:
        return []

    known_ids = [pid for pid, _ in known]
    known_embeddings = np.array([emb for _, emb in known])

    distances = face_recognition.face_distance(known_embeddings, query_embedding)

    results: list[dict] = []
    for pid, dist in zip(known_ids, distances):
        if dist > tolerance:
            continue
        person = db.get(Person, pid)
        if person is None:
            continue
        results.append({
            "person_id": pid,
            "person_name": person.name,
            "distance": float(dist),
            "confidence_pct": int((1.0 - float(dist)) * 100),
        })

    results.sort(key=lambda r: r["distance"])
    return results[:top_k]
