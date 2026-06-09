from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.appearance import Appearance
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
    timestamp: float,
    confidence: float,
) -> Appearance:
    gap = settings.FACE_TRACK_GAP_TOLERANCE
    # Aparição "open" (timestamp_end=None) só corresponde se o start estiver dentro da tolerância.
    # Aparição "fechada" corresponde se o end estiver dentro da tolerância.
    existing = (
        db.query(Appearance)
        .filter(
            Appearance.person_id == person_id,
            Appearance.video_id == video_id,
            (
                (Appearance.timestamp_end == None)  # noqa: E711
                & (Appearance.timestamp_start >= timestamp - gap)
            )
            | (
                (Appearance.timestamp_end != None)  # noqa: E711
                & (Appearance.timestamp_end >= timestamp - gap)
            ),
        )
        .order_by(Appearance.timestamp_start.desc())
        .first()
    )

    if existing is not None:
        existing.timestamp_end = timestamp
        if confidence < existing.confidence:
            existing.confidence = confidence
        db.commit()
        return existing

    new_appearance = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=timestamp,
        timestamp_end=None,
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
