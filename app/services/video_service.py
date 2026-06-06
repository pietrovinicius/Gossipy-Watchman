from sqlalchemy.orm import Session

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


def update_video_status(db: Session, video_id: int, status: VideoStatus) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    video.status = status
    db.commit()
    db.refresh(video)
    return video
