from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.person import Person
from app.models.video import Video
from app.services.auth_service import get_current_user
from app.services.export_service import generate_timeline_csv

router = APIRouter()

_TS = lambda: datetime.now().strftime("%Y%m%d_%H%M%S")


@router.get("/export/timeline")
def export_timeline(
    person_id: int | None = Query(default=None),
    video_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    if person_id is not None and video_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Forneça person_id OU video_id, não ambos simultaneamente.",
        )

    if person_id is not None and db.get(Person, person_id) is None:
        raise HTTPException(status_code=404, detail=f"Pessoa {person_id} não encontrada")

    if video_id is not None and db.get(Video, video_id) is None:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")

    csv_content = generate_timeline_csv(db, person_id=person_id, video_id=video_id)
    filename = f"gossipy_timeline_{_TS()}.csv"

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/timeline/person/{person_id}")
def export_timeline_person(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    if db.get(Person, person_id) is None:
        raise HTTPException(status_code=404, detail=f"Pessoa {person_id} não encontrada")

    csv_content = generate_timeline_csv(db, person_id=person_id)
    filename = f"gossipy_pessoa_{person_id}_{_TS()}.csv"

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/timeline/video/{video_id}")
def export_timeline_video(
    video_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    if db.get(Video, video_id) is None:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")

    csv_content = generate_timeline_csv(db, video_id=video_id)
    filename = f"gossipy_video_{video_id}_{_TS()}.csv"

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
