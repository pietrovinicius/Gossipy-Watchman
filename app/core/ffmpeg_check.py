import subprocess
import logging
from app.core.settings import settings

logger = logging.getLogger(__name__)


def check_ffmpeg() -> bool:
    """Verifica se ffmpeg está disponível no PATH."""
    try:
        result = subprocess.run(
            [settings.FFMPEG_PATH, "-version"],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            logger.info(f"ffmpeg disponível: {version_line}")
            return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


FFMPEG_AVAILABLE = check_ffmpeg()


def get_ffmpeg_status() -> dict:
    """Retorna status do ffmpeg."""
    return {
        "available": FFMPEG_AVAILABLE,
        "path": settings.FFMPEG_PATH,
        "message": (
            "ffmpeg disponível — conversão automática ativa"
            if FFMPEG_AVAILABLE
            else "ffmpeg não encontrado — apenas MP4 e AVI suportados"
        )
    }
