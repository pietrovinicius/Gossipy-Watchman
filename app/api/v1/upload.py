from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import get_db
from app.schemas.video import VideoStatusResponse
from app.services import video_service
from app.services.auth_service import get_current_user
from app.workers.video_worker import process_video

router = APIRouter()

_ALLOWED_EXTENSIONS = {".mp4", ".avi"}
_CHUNK_SIZE = 1024 * 1024  # 1 MB

_MAGIC: dict[str, list[tuple[int, int, bytes]]] = {
    ".mp4": [(4, 8, b"ftyp")],
    ".avi": [(0, 4, b"RIFF"), (8, 12, b"AVI ")],
}


def _validate_magic(header: bytes, suffix: str) -> bool:
    for start, end, expected in _MAGIC.get(suffix, []):
        if header[start:end] != expected:
            return False
    return True


@router.post("/videos/upload", response_model=VideoStatusResponse, status_code=202)
async def upload_video(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> VideoStatusResponse:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{suffix}' não suportado. Use .mp4 ou .avi.",
        )

    # Correção 2 — Magic Bytes: lê primeiros 12 bytes antes de gravar
    header = await file.read(12)
    if not _validate_magic(header, suffix):
        raise HTTPException(
            status_code=415,
            detail="Conteúdo do arquivo não corresponde à extensão declarada.",
        )

    # Correção 1 — Path Traversal: nome baseado em UUID, não no input do usuário
    safe_filename = f"{uuid4().hex}{suffix}"
    video_record = video_service.create_video_record(db, file.filename, "")
    dest_path: Path = settings.STORAGE_VIDEOS / safe_filename

    # Correção 3 — Limite de tamanho + limpeza de arquivo parcial
    written = len(header)
    try:
        with dest_path.open("wb") as f:
            f.write(header)
            while chunk := await file.read(_CHUNK_SIZE):
                written += len(chunk)
                if written > settings.MAX_UPLOAD_SIZE_BYTES:
                    f.close()
                    dest_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Arquivo excede o limite de "
                            f"{settings.MAX_UPLOAD_SIZE_MB}MB"
                        ),
                    )
                f.write(chunk)
    except HTTPException:
        raise

    video_service.update_file_path(db, video_record.id, str(dest_path))
    db.refresh(video_record)

    background_tasks.add_task(process_video, video_record.id, dest_path)

    return VideoStatusResponse.model_validate(video_record)
