import logging
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video, VideoStatus

logger = logging.getLogger(__name__)


def create_video_record(db: Session, file_name: str, file_path: str) -> Video:
    video = Video(file_name=file_name, file_path=file_path, status=VideoStatus.PENDENTE)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def get_video_by_id(db: Session, video_id: int) -> Video | None:
    return db.get(Video, video_id)


def list_videos(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    status_filter: str | None = None,
) -> list[Video]:
    query = db.query(Video)
    if not include_deleted:
        query = query.filter(Video.deleted_at.is_(None))
    if status_filter is not None:
        query = query.filter(Video.status == status_filter)
    return (
        query
        .order_by(Video.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def _remove_file_if_exists(path_str: str | None) -> None:
    if not path_str:
        return
    p = Path(path_str)
    try:
        if p.exists():
            p.unlink()
    except OSError as e:
        logger.warning(f"[SOFT_DELETE] falha ao remover {path_str}: {e}")


def soft_delete_video(db: Session, video_id: int) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    if video.deleted_at is None:
        video.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(video)
        _remove_file_if_exists(video.file_path)
        _remove_file_if_exists(video.thumbnail_path)
    return video


def restore_video(db: Session, video_id: int) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    video.deleted_at = None
    db.commit()
    db.refresh(video)
    return video


def reprocess_video(db: Session, video_id: int) -> Video | None:
    video = db.get(Video, video_id)
    if video is None:
        return None
    if not Path(video.file_path).exists():
        raise HTTPException(
            status_code=409,
            detail="Arquivo de vídeo não encontrado em disco. Impossível reprocessar.",
        )
    video.status = VideoStatus.PENDENTE
    db.commit()
    db.refresh(video)
    return video


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

    logger.debug(f"[GET_VIDEO_DETAIL] video_id={video_id} total_appearances={len(rows)}")
    for appearance, person in rows:
        logger.debug(f"[GET_VIDEO_DETAIL] appearance_id={appearance.id} video_id={appearance.video_id} person_id={person.id} timestamp={appearance.timestamp_start}-{appearance.timestamp_end}")

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


def search_videos(
    db: Session,
    query: str | None = None,
    status_filter: str | None = None,
    sort_by: str = "uploaded_at_desc",
    page: int = 1,
    page_size: int = 12,
    include_deleted: bool = False,
) -> dict:
    """
    Busca paginada de vídeos com filtros, busca por nome, ordenação e
    contagem de pessoas identificadas.

    Retorna dict com: items, total, page, page_size, total_pages, has_next, has_prev
    """
    q = db.query(Video)

    if not include_deleted:
        q = q.filter(Video.deleted_at.is_(None))

    if status_filter is not None:
        q = q.filter(Video.status == status_filter)

    if query is not None:
        q = q.filter(Video.file_name.ilike(f"%{query}%"))

    if sort_by == "uploaded_at_desc":
        q = q.order_by(Video.uploaded_at.desc())
    elif sort_by == "uploaded_at_asc":
        q = q.order_by(Video.uploaded_at.asc())
    elif sort_by == "name_asc":
        q = q.order_by(Video.file_name.asc())
    elif sort_by == "name_desc":
        q = q.order_by(Video.file_name.desc())
    elif sort_by == "people_desc":
        # Ordena por count de pessoas distintas (desc)
        q = (
            q.outerjoin(Appearance, Video.id == Appearance.video_id)
            .group_by(Video.id)
            .order_by(func.count(func.distinct(Appearance.person_id)).desc())
        )
    else:
        q = q.order_by(Video.uploaded_at.desc())

    total = q.count() if sort_by != "people_desc" else len(q.all())

    offset = (page - 1) * page_size
    items = q.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1

    items_dict = []
    for video in items:
        people_count = (
            db.query(func.count(func.distinct(Appearance.person_id)))
            .filter(Appearance.video_id == video.id)
            .scalar()
        ) or 0

        people_previews = (
            db.query(Person.id, Person.name, Person.profile_image_path)
            .join(Appearance, Person.id == Appearance.person_id)
            .filter(Appearance.video_id == video.id)
            .distinct(Person.id)
            .limit(4)
            .all()
        )

        items_dict.append(
            {
                "id": video.id,
                "file_name": video.file_name,
                "file_path": video.file_path,
                "status": video.status,
                "uploaded_at": video.uploaded_at,
                "thumbnail_path": video.thumbnail_path,
                "deleted_at": video.deleted_at,
                "people_count": people_count,
                "people_previews": [
                    {
                        "person_id": p[0],
                        "person_name": p[1],
                        "profile_image_path": p[2],
                    }
                    for p in people_previews
                ],
            }
        )

    return {
        "items": items_dict,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
    }
