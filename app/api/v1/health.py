from fastapi import APIRouter

from app.core.settings import settings
from app.core.ffmpeg_check import get_ffmpeg_status

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/health/ffmpeg")
def ffmpeg_check() -> dict:
    return get_ffmpeg_status()
