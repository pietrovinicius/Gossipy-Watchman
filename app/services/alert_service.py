from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(
    db: Session,
    person_id: int,
    video_id: int,
    timestamp_in_video: float,
    message: str,
) -> Alert:
    alert = Alert(
        person_id=person_id,
        video_id=video_id,
        timestamp_in_video=timestamp_in_video,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(
    db: Session,
    unseen_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Alert]:
    query = db.query(Alert)
    if unseen_only:
        query = query.filter(Alert.seen.is_(False))
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def mark_alerts_seen(db: Session, alert_ids: list[int]) -> int:
    updated = (
        db.query(Alert)
        .filter(Alert.id.in_(alert_ids))
        .update({"seen": True}, synchronize_session="fetch")
    )
    db.commit()
    return updated


def get_unseen_count(db: Session) -> int:
    return db.query(Alert).filter(Alert.seen.is_(False)).count()
