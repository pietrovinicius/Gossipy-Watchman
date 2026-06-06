from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.appearance import AppearanceResponse
from app.services import appearance_service, person_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/people/{person_id}/timeline", response_model=list[AppearanceResponse])
def get_person_timeline(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> list[AppearanceResponse]:
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    timeline = appearance_service.get_timeline(db, person_id)
    return [AppearanceResponse.model_validate(item.__dict__) for item in timeline]
