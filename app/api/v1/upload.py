from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import get_db
from app.schemas.video import VideoStatusResponse
from app.services import video_service
from app.workers.video_worker import process_video

router = APIRouter()

_ALLOWED_EXTENSIONS = {".mp4", ".avi"}
_CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/videos/upload", response_model=VideoStatusResponse, status_code=202)
async def upload_video(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> VideoStatusResponse:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{suffix}' não suportado. Use .mp4 ou .avi.",
        )

    video_record = video_service.create_video_record(db, file.filename, "")
    dest_name = f"{video_record.id}_{file.filename}"
    dest_path = settings.STORAGE_VIDEOS / dest_name

    with dest_path.open("wb") as f:
        while chunk := await file.read(_CHUNK_SIZE):
            f.write(chunk)

    video_service.update_file_path(db, video_record.id, str(dest_path))
    db.refresh(video_record)

    background_tasks.add_task(process_video, video_record.id, dest_path)

    return VideoStatusResponse.model_validate(video_record)
