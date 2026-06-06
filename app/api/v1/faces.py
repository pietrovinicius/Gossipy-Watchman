from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.settings import settings
from app.services.auth_service import get_current_user

router = APIRouter()

_UNSAFE_CHARS = {"..": True, "/": True, "\\": True}


def _is_safe_filename(filename: str) -> bool:
    if ".." in filename:
        return False
    if "/" in filename or "\\" in filename:
        return False
    return True


@router.get("/faces/{filename}")
def get_face_image(
    filename: str,
    _current_user: dict = Depends(get_current_user),
) -> FileResponse:
    if not _is_safe_filename(filename):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    face_path = settings.STORAGE_FACES / filename

    # Confinamento de caminho: garante que o path resolvido está dentro de STORAGE_FACES
    try:
        resolved = face_path.resolve()
        base_resolved = settings.STORAGE_FACES.resolve()
        resolved.relative_to(base_resolved)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    return FileResponse(str(resolved), media_type="image/jpeg")
