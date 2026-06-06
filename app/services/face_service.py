import cv2
import face_recognition
import numpy as np

from app.core.settings import settings


def extract_embeddings(frame: np.ndarray) -> list[np.ndarray]:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)
    return list(encodings)


def find_matching_person(
    embedding: np.ndarray,
    known_embeddings: list[tuple[int, np.ndarray]],
    tolerance: float = settings.FACE_RECOGNITION_TOLERANCE,
) -> tuple[int | None, float | None]:
    if not known_embeddings:
        return None, None

    known_vecs = [emb for _, emb in known_embeddings]
    distances: np.ndarray = face_recognition.face_distance(known_vecs, embedding)

    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])

    if best_dist > tolerance:
        return None, None

    person_id = known_embeddings[best_idx][0]
    return person_id, best_dist
