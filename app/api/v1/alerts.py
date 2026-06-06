from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.models.person import Person
from app.models.video import Video
from app.schemas.alert import AlertResponse
from app.services import alert_service
from app.services.auth_service import get_current_user

router = APIRouter()


class SeenRequest(BaseModel):
    alert_ids: list[int]


def _enrich(alert: Alert, db: Session) -> AlertResponse:
    person = db.get(Person, alert.person_id)
    video = db.get(Video, alert.video_id)
    return AlertResponse(
        id=alert.id,
        person_id=alert.person_id,
        person_name=person.name if person else "Desconhecido",
        video_id=alert.video_id,
        video_file_name=video.file_name if video else "",
        timestamp_in_video=alert.timestamp_in_video,
        message=alert.message,
        seen=alert.seen,
        created_at=alert.created_at,
    )


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    unseen_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    alerts = alert_service.list_alerts(db, unseen_only=unseen_only, skip=skip, limit=limit)
    return [_enrich(a, db) for a in alerts]


@router.get("/alerts/count")
def get_alerts_count(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return {"unseen": alert_service.get_unseen_count(db)}


@router.patch("/alerts/seen")
def mark_seen(
    body: SeenRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    updated = alert_service.mark_alerts_seen(db, body.alert_ids)
    return {"updated": updated}
