import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import SearchResponse, SearchResult
from app.services import search_service
from app.services.auth_service import get_current_user

router = APIRouter()

_ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png"}
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/search/by-face", response_model=SearchResponse)
async def search_by_face(
    file: UploadFile = File(...),
    top_k: int = 5,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> SearchResponse:
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Use JPEG ou PNG.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=422,
            detail="Imagem excede o limite de 10 MB.",
        )

    t0 = time.perf_counter()
    results = search_service.search_by_face(db, image_bytes, top_k=top_k)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        query_time_ms=elapsed_ms,
    )
