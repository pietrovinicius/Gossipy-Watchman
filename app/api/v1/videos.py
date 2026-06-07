from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video import (
    CatalogResponse,
    VideoDetailResponse,
    VideoResponse,
    VideoStatusResponse,
)
from app.services import video_service
from app.services.auth_service import get_current_user
from app.workers.video_worker import process_video

router = APIRouter()


@router.get("/videos/catalog", response_model=CatalogResponse)
def catalog_videos(
    q: str | None = Query(default=None, description="Busca parcial por nome de arquivo"),
    status: str | None = Query(default=None, description="Filtro por status exato"),
    sort_by: str = Query(
        default="uploaded_at_desc",
        description="uploaded_at_desc, uploaded_at_asc, name_asc, name_desc, people_desc",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=48),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> CatalogResponse:
    result = video_service.search_videos(
        db,
        query=q,
        status_filter=status,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
    )
    return CatalogResponse(**result)


@router.get("/videos", response_model=list[VideoResponse])
def list_videos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    include_deleted: bool = Query(default=False),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> list[VideoResponse]:
    return video_service.list_videos(
        db, skip=skip, limit=limit, include_deleted=include_deleted, status_filter=status
    )


@router.post("/videos/{video_id}/restore", response_model=VideoResponse)
def restore_video(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoResponse:
    video = video_service.restore_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoResponse.model_validate(video)


@router.post("/videos/{video_id}/reprocess", response_model=VideoStatusResponse)
def reprocess_video(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoStatusResponse:
    video = video_service.get_video_by_id(db, video_id)
    if video is None or video.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    video = video_service.reprocess_video(db, video_id)
    background_tasks.add_task(process_video, video.id, Path(video.file_path))
    return VideoStatusResponse.model_validate(video)


@router.delete("/videos/{video_id}", response_model=VideoResponse)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoResponse:
    video = video_service.soft_delete_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoResponse.model_validate(video)


@router.get("/videos/{video_id}/detail", response_model=VideoDetailResponse)
def get_video_detail(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoDetailResponse:
    detail = video_service.get_video_detail(db, video_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoDetailResponse.model_validate(detail)


@router.get("/videos/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoResponse:
    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoResponse.model_validate(video)


@router.get("/videos/{video_id}/status", response_model=VideoStatusResponse)
def get_video_status(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoStatusResponse:
    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoStatusResponse.model_validate(video)
