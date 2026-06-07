from sqlalchemy.orm import Session

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video, VideoStatus


def create_video_record(db: Session, file_name: str, file_path: str) -> Video:
    video = Video(file_name=file_name, file_path=file_path, status=VideoStatus.PENDENTE)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def get_video_by_id(db: Session, video_id: int) -> Video | None:
    return db.get(Video, video_id)


def list_videos(db: Session, skip: int = 0, limit: int = 50) -> list[Video]:
    return (
        db.query(Video)
        .order_by(Video.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_file_path(db: Session, video_id: int, file_path: str) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    video.file_path = file_path
    db.commit()
    db.refresh(video)
    return video


def get_video_detail(db: Session, video_id: int) -> dict | None:
    video = db.get(Video, video_id)
    if video is None:
        return None

    rows = (
        db.query(Appearance, Person)
        .join(Person, Appearance.person_id == Person.id)
        .filter(Appearance.video_id == video_id)
        .all()
    )

    grouped: dict[int, dict] = {}
    for appearance, person in rows:
        entry = grouped.setdefault(
            person.id,
            {
                "person_id": person.id,
                "person_name": person.name,
                "person_category": person.category,
                "profile_image_path": person.profile_image_path,
                "total_seconds": 0.0,
                "appearance_count": 0,
                "first_seen_at": appearance.timestamp_start,
                "last_seen_at": appearance.timestamp_end
                if appearance.timestamp_end is not None
                else appearance.timestamp_start,
                "appearances": [],
            },
        )

        if appearance.timestamp_end is not None:
            entry["total_seconds"] += appearance.timestamp_end - appearance.timestamp_start
            last_candidate = appearance.timestamp_end
        else:
            last_candidate = appearance.timestamp_start

        entry["appearance_count"] += 1
        entry["first_seen_at"] = min(entry["first_seen_at"], appearance.timestamp_start)
        entry["last_seen_at"] = max(entry["last_seen_at"], last_candidate)
        entry["appearances"].append(
            {
                "id": appearance.id,
                "timestamp_start": appearance.timestamp_start,
                "timestamp_end": appearance.timestamp_end,
                "confidence": appearance.confidence,
            }
        )

    people = sorted(grouped.values(), key=lambda p: p["first_seen_at"])

    total_appearances = len(rows)
    duration_covered = sum(
        appearance.timestamp_end - appearance.timestamp_start
        for appearance, _ in rows
        if appearance.timestamp_end is not None
    )

    return {
        "video": {
            "id": video.id,
            "file_name": video.file_name,
            "file_path": video.file_path,
            "status": video.status,
            "uploaded_at": video.uploaded_at,
        },
        "people": people,
        "summary": {
            "total_people": len(grouped),
            "total_appearances": total_appearances,
            "duration_covered": duration_covered,
            "processing_status": video.status.value,
        },
    }


def update_video_status(db: Session, video_id: int, status: VideoStatus) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    video.status = status
    db.commit()
    db.refresh(video)
    return video
