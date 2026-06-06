import logging
from datetime import datetime

import cv2
import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.appearance import Appearance
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


def list_people(db: Session, skip: int = 0, limit: int = 50) -> list[Person]:
    return (
        db.query(Person)
        .order_by(Person.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_person_by_id(db: Session, person_id: int) -> Person | None:
    return db.get(Person, person_id)


def update_person_name(db: Session, person_id: int, name: str) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    person.name = name
    db.commit()
    db.refresh(person)
    return person


def update_person_details(
    db: Session,
    person_id: int,
    name: str | None,
    notes: str | None,
    category: str | None,
) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    if name is not None:
        person.name = name
    if notes is not None:
        person.notes = notes
    if category is not None:
        person.category = category
    db.commit()
    db.refresh(person)
    return person


def get_person_stats(db: Session, person_id: int) -> dict:
    appearances = (
        db.query(Appearance).filter(Appearance.person_id == person_id).all()
    )
    if not appearances:
        return {
            "video_count": 0,
            "total_seconds": 0.0,
            "first_seen": None,
            "last_seen": None,
        }

    video_ids = {a.video_id for a in appearances}
    total_seconds = sum(
        (a.timestamp_end - a.timestamp_start) for a in appearances
    )

    # first_seen / last_seen via video.uploaded_at
    from app.models.video import Video

    videos = (
        db.query(Video)
        .filter(Video.id.in_(video_ids))
        .order_by(Video.uploaded_at)
        .all()
    )
    first_seen: datetime | None = videos[0].uploaded_at if videos else None
    last_seen: datetime | None = videos[-1].uploaded_at if videos else None

    return {
        "video_count": len(video_ids),
        "total_seconds": round(total_seconds, 3),
        "first_seen": first_seen,
        "last_seen": last_seen,
    }


def merge_people(
    db: Session,
    primary_id: int,
    secondary_ids: list[int],
) -> Person:
    if primary_id in secondary_ids:
        raise HTTPException(status_code=400, detail="primary_id não pode estar em secondary_ids")

    primary = db.get(Person, primary_id)
    if primary is None:
        raise HTTPException(status_code=404, detail=f"Pessoa {primary_id} não encontrada")

    for sec_id in secondary_ids:
        secondary = db.get(Person, sec_id)
        if secondary is None:
            raise HTTPException(status_code=404, detail=f"Pessoa {sec_id} não encontrada")

        # reassociate appearances
        db.query(Appearance).filter(Appearance.person_id == sec_id).update(
            {"person_id": primary_id}
        )

        # remove .npy and .jpg files for secondary
        for suffix in (f"{sec_id}_embedding.npy", f"{sec_id}.jpg"):
            path = settings.STORAGE_FACES / suffix
            if path.exists():
                path.unlink()
                logger.info("merge_people: removido %s", path)

        db.delete(secondary)

    db.commit()
    db.refresh(primary)
    return primary
