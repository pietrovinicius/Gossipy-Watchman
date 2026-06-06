from sqlalchemy.orm import Session

from app.models.appearance import Appearance

_GAP_TOLERANCE_SECONDS = 2.0


def upsert_appearance(
    db: Session,
    person_id: int,
    video_id: int,
    timestamp: float,
    confidence: float,
) -> Appearance:
    # Aparição "open" (timestamp_end=None) só corresponde se o start estiver dentro da tolerância.
    # Aparição "fechada" corresponde se o end estiver dentro da tolerância.
    existing = (
        db.query(Appearance)
        .filter(
            Appearance.person_id == person_id,
            Appearance.video_id == video_id,
            (
                (Appearance.timestamp_end == None)  # noqa: E711
                & (Appearance.timestamp_start >= timestamp - _GAP_TOLERANCE_SECONDS)
            )
            | (
                (Appearance.timestamp_end != None)  # noqa: E711
                & (Appearance.timestamp_end >= timestamp - _GAP_TOLERANCE_SECONDS)
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
