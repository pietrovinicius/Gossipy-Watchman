from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video


@dataclass
class AppearanceWithVideo:
    """Projeção de Appearance com file_name do vídeo associado."""
    id: int
    person_id: int
    video_id: int
    timestamp_start: float
    timestamp_end: float | None
    confidence: float
    file_name: str


def upsert_appearance(
    db: Session,
    person_id: int,
    video_id: int,
    timestamp_start: float,
    timestamp_end: float,
    confidence: float,
) -> Appearance:
    gap = settings.FACE_TRACK_GAP_TOLERANCE
    existing = (
        db.query(Appearance)
        .filter(
            Appearance.person_id == person_id,
            Appearance.video_id == video_id,
            (
                (Appearance.timestamp_end == None)  # noqa: E711
                & (Appearance.timestamp_start >= timestamp_start - gap)
            )
            | (
                (Appearance.timestamp_end != None)  # noqa: E711
                & (Appearance.timestamp_end >= timestamp_start - gap)
            ),
        )
        .order_by(Appearance.timestamp_start.desc())
        .first()
    )

    if existing is not None:
        existing_end = existing.timestamp_end if existing.timestamp_end is not None else existing.timestamp_start
        existing.timestamp_end = max(existing_end, timestamp_end)
        if confidence < existing.confidence:
            existing.confidence = confidence
        db.commit()
        return existing

    new_appearance = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        confidence=confidence,
    )
    db.add(new_appearance)
    db.commit()
    db.refresh(new_appearance)
    return new_appearance


def add_manual_appearance(
    db: Session,
    video_id: int,
    person_id: int,
    timestamp_start: float,
    timestamp_end: float,
    confidence: float = 0.0,
) -> Appearance:
    """Cria uma aparição manualmente para uma pessoa em um vídeo já processado."""
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    new_appearance = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        confidence=confidence,
    )
    db.add(new_appearance)
    db.commit()
    db.refresh(new_appearance)
    return new_appearance


def get_timeline(db: Session, person_id: int) -> list[AppearanceWithVideo]:
    rows = (
        db.query(Appearance, Video.file_name)
        .join(Video, Appearance.video_id == Video.id)
        .filter(Appearance.person_id == person_id)
        .order_by(Appearance.video_id.asc(), Appearance.timestamp_start.asc())
        .all()
    )
    return [
        AppearanceWithVideo(
            id=app.id,
            person_id=app.person_id,
            video_id=app.video_id,
            timestamp_start=app.timestamp_start,
            timestamp_end=app.timestamp_end,
            confidence=app.confidence,
            file_name=file_name,
        )
        for app, file_name in rows
    ]
