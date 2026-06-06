from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.person import PersonResponse, PersonUpdate
from app.services import person_service

router = APIRouter()


@router.get("/people", response_model=list[PersonResponse])
def list_people(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[PersonResponse]:
    return person_service.list_people(db, skip=skip, limit=limit)


@router.get("/people/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)) -> PersonResponse:
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return PersonResponse.model_validate(person)


@router.patch("/people/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    body: PersonUpdate,
    db: Session = Depends(get_db),
) -> PersonResponse:
    person = person_service.update_person_name(db, person_id, body.name)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return PersonResponse.model_validate(person)
