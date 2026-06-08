import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

YUNET_URL = "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://huggingface.co/opencv/face_recognition_sface/resolve/main/face_recognition_sface_2021dec.onnx"

MODELS_DIR = Path("storage/models")
YUNET_PATH = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = MODELS_DIR / "face_recognition_sface_2021dec.onnx"


def download_file(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.stat().st_size > 10000:
        logger.info(f"Model already exists: {dest_path.name}")
        return

    logger.info(f"Downloading model from {url} to {dest_path}...")
    try:
        # Baixar o arquivo usando urllib.request
        urllib.request.urlretrieve(url, str(dest_path))
        # Validar tamanho mínimo
        if dest_path.stat().st_size < 10000:
            raise ValueError("Downloaded file is too small, possibly a pointer or corrupted")
        logger.info(f"Successfully downloaded: {dest_path.name}")
    except Exception as e:
        logger.error(f"Failed to download model {dest_path.name}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        raise e


def ensure_models_downloaded() -> None:
    download_file(YUNET_URL, YUNET_PATH)
    download_file(SFACE_URL, SFACE_PATH)
