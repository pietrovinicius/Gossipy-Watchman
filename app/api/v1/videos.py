from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video import VideoResponse, VideoStatusResponse
from app.services import video_service

router = APIRouter()


@router.get("/videos", response_model=list[VideoResponse])
def list_videos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[VideoResponse]:
    return video_service.list_videos(db, skip=skip, limit=limit)


@router.get("/videos/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)) -> VideoResponse:
    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoResponse.model_validate(video)


@router.get("/videos/{video_id}/status", response_model=VideoStatusResponse)
def get_video_status(video_id: int, db: Session = Depends(get_db)) -> VideoStatusResponse:
    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return VideoStatusResponse.model_validate(video)
