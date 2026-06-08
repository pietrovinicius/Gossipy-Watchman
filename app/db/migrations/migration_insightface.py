import logging
from pathlib import Path

import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)


def run(storage_dir: Path | None = None) -> None:
    """Remove embeddings dlib (128-dim) de storage_dir.

    Idempotente: arquivos já deletados ou inexistentes são ignorados.
    Preserva arquivos .jpg e embeddings ArcFace (512-dim) intactos.
    """
    dirs = (
        [storage_dir]
        if storage_dir is not None
        else [settings.STORAGE_FACES, settings.STORAGE_EMPLOYEES]
    )

    total_deleted = 0
    for directory in dirs:
        if not directory.exists():
            continue
        for npy_path in directory.glob("*.npy"):
            try:
                arr = np.load(str(npy_path))
                if arr.shape == (128,):
                    npy_path.unlink()
                    total_deleted += 1
                    logger.info(
                        "migration_insightface: removido %s (shape=128)",
                        npy_path.name,
                    )
            except Exception:
                logger.warning(
                    "migration_insightface: falha ao inspecionar %s",
                    npy_path,
                    exc_info=True,
                )

    logger.info("migration_insightface: %d arquivos dlib removidos", total_deleted)
