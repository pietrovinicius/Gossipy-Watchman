import logging

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.person import Person

logger = logging.getLogger(__name__)


def get_all_embeddings(db: Session) -> list[tuple[int, np.ndarray]]:
    people = db.query(Person).all()
    result: list[tuple[int, np.ndarray]] = []
    for person in people:
        npy_path = settings.STORAGE_FACES / f"{person.id}_embedding.npy"
        if not npy_path.exists():
            logger.warning("Embedding não encontrado para pessoa id=%s: %s", person.id, npy_path)
            continue
        embedding = np.load(str(npy_path))
        result.append((person.id, embedding))
    return result


def save_new_person(
    db: Session,
    embedding: np.ndarray,
    face_crop: np.ndarray,
    person_index: int,
) -> Person:
    person = Person(name=f"Desconhecido #{person_index}")
    db.add(person)
    db.commit()
    db.refresh(person)

    jpg_path = settings.STORAGE_FACES / f"{person.id}.jpg"
    npy_path = settings.STORAGE_FACES / f"{person.id}_embedding.npy"

    cv2.imwrite(str(jpg_path), face_crop)
    np.save(str(npy_path), embedding)

    person.profile_image_path = str(jpg_path)
    db.commit()

    return person
