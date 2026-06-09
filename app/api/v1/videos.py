from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.appearance import AppearanceResponse, ManualAppearanceCreate
from app.schemas.video import (
    CatalogResponse,
    VideoDetailResponse,
    VideoResponse,
    VideoStatusResponse,
)
from app.services import video_service
from app.services.appearance_service import add_manual_appearance
from app.services.auth_service import get_current_user, verify_token
from app.workers.video_worker import process_video

router = APIRouter()


def iterfile(path: Path, start: int, length: int, chunk: int = 65536):
    with open(path, "rb") as f:
        f.seek(start)
        remaining = length
        while remaining > 0:
            data = f.read(min(chunk, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data


@router.get("/videos/{video_id}/stream", response_model=None)
async def stream_video(
    video_id: int,
    token: str | None = Query(default=None),
    request: Request = None,
    db: Session = Depends(get_db),
):
    if not token:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    verify_token(token)

    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    if video.deleted_at is not None:
        raise HTTPException(status_code=410, detail="Vídeo foi excluído")

    file_path = Path(video.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado em disco")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("Range")

    if range_header:
        range_str = range_header.replace("bytes=", "")
        parts = range_str.split("-")
        start = int(parts[0])
        end = int(parts[1]) if parts[1] else file_size - 1
        end = min(end, file_size - 1)
        content_length = end - start + 1

        return StreamingResponse(
            iterfile(file_path, start, content_length),
            status_code=206,
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": "video/mp4",
            },
        )
    else:
        return FileResponse(
            file_path,
            media_type="video/mp4",
            headers={"Accept-Ranges": "bytes"},
        )


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


@router.post("/videos/{video_id}/appearances", response_model=AppearanceResponse, status_code=201)
def add_appearance_to_video(
    video_id: int,
    body: ManualAppearanceCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> AppearanceResponse:
    app_obj = add_manual_appearance(
        db,
        video_id=video_id,
        person_id=body.person_id,
        timestamp_start=body.timestamp_start,
        timestamp_end=body.timestamp_end,
        confidence=body.confidence,
    )
    video = video_service.get_video_by_id(db, video_id)
    return AppearanceResponse(
        id=app_obj.id,
        person_id=app_obj.person_id,
        video_id=app_obj.video_id,
        timestamp_start=app_obj.timestamp_start,
        timestamp_end=app_obj.timestamp_end,
        confidence=app_obj.confidence,
        file_name=video.file_name if video else "",
    )


@router.get("/videos/{video_id}/thumbnail", response_model=None)
def get_video_thumbnail(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    video = video_service.get_video_by_id(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    if not video.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail não disponível")

    thumbnail_file = Path(video.thumbnail_path)
    if not thumbnail_file.exists():
        raise HTTPException(status_code=404, detail="Arquivo de thumbnail não encontrado")

    return FileResponse(thumbnail_file, media_type="image/jpeg")
