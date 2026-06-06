from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video


def get_overview(db: Session) -> dict:
    total_videos = db.query(func.count(Video.id)).scalar() or 0
    total_people = db.query(func.count(Person.id)).scalar() or 0
    total_appearances = db.query(func.count(Appearance.id)).scalar() or 0
    return {
        "total_videos": total_videos,
        "total_people": total_people,
        "total_appearances": total_appearances,
    }


def get_appearances_per_video(db: Session) -> list[dict]:
    rows = (
        db.query(Video.id, Video.file_name, func.count(Appearance.id))
        .outerjoin(Appearance, Appearance.video_id == Video.id)
        .group_by(Video.id)
        .order_by(func.count(Appearance.id).desc())
        .all()
    )
    return [
        {"video_id": vid, "file_name": fname, "count": cnt}
        for vid, fname, cnt in rows
    ]


def get_top_people(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(Person.id, Person.name, func.count(Appearance.id))
        .outerjoin(Appearance, Appearance.person_id == Person.id)
        .group_by(Person.id)
        .order_by(func.count(Appearance.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"person_id": pid, "person_name": name, "appearance_count": cnt}
        for pid, name, cnt in rows
    ]


def get_activity_timeline(db: Session, days: int = 30) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(Video.uploaded_at).label("date"),
            func.count(Video.id).label("count"),
        )
        .filter(Video.uploaded_at >= cutoff)
        .group_by(func.date(Video.uploaded_at))
        .order_by(func.date(Video.uploaded_at))
        .all()
    )
    return [{"date": str(r.date), "count": r.count} for r in rows]
