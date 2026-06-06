from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import analytics_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/analytics/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> dict:
    return analytics_service.get_overview(db)


@router.get("/analytics/appearances-per-video")
def appearances_per_video(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[dict]:
    return analytics_service.get_appearances_per_video(db)


@router.get("/analytics/top-people")
def top_people(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[dict]:
    return analytics_service.get_top_people(db, limit=limit)


@router.get("/analytics/activity-timeline")
def activity_timeline(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[dict]:
    return analytics_service.get_activity_timeline(db, days=days)
