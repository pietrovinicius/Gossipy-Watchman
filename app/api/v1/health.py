from pathlib import Path

import numpy as np
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


@router.get("/health/embeddings")
def embeddings_check() -> dict:
    """Diagnóstico de embeddings em armazenamento.

    Valida:
    - shape: deve ser (128,)
    - dtype: deve ser float64
    - norm: deve estar entre 0.9 e 1.1 (vetores aproximadamente unitários)
    """
    embeddings_dir = settings.STORAGE_FACES
    if not embeddings_dir.exists():
        return {"status": "error", "message": f"Diretório não existe: {embeddings_dir}"}

    files = list(embeddings_dir.glob("*_embedding.npy"))
    total = len(files)
    valid = []
    suspicious = []

    for npy_file in files:
        try:
            embedding = np.load(str(npy_file))
            person_id = int(npy_file.stem.replace("_embedding", ""))
            shape = tuple(embedding.shape)
            dtype = str(embedding.dtype)
            norm = float(np.linalg.norm(embedding))

            is_valid = (
                shape == (128,) and
                dtype == "float64" and
                0.85 < norm < 1.15
            )

            record = {
                "person_id": person_id,
                "filename": npy_file.name,
                "shape": shape,
                "dtype": dtype,
                "norm": round(norm, 4),
            }

            if is_valid:
                valid.append(record)
            else:
                suspicious.append(record)
        except Exception as e:
            suspicious.append({
                "filename": npy_file.name,
                "error": str(e),
            })

    return {
        "status": "ok",
        "total": total,
        "valid": len(valid),
        "suspicious": len(suspicious),
        "embeddings_valid": valid,
        "embeddings_suspicious": suspicious,
    }
