from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import get_db
from app.schemas.person import (
    FaceFrameResponse,
    MergeRequest,
    PersonResponse,
    PersonStatsResponse,
    PersonUpdate,
    PrimaryPhotoRequest,
    ProfileQualityResponse,
)
from app.services import person_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/people", response_model=list[PersonResponse])
def list_people(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> list[PersonResponse]:
    return person_service.list_people(db, skip=skip, limit=limit)


# CRITICAL: /people/merge MUST precede /people/{person_id}
# FastAPI treats literal path segments as int params if order is reversed
@router.post("/people/merge", response_model=PersonResponse)
def merge_people(
    body: MergeRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> PersonResponse:
    primary = person_service.merge_people(db, body.primary_id, body.secondary_ids)
    return PersonResponse.model_validate(primary)


@router.get("/people/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> PersonResponse:
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return PersonResponse.model_validate(person)


@router.get("/people/{person_id}/stats", response_model=PersonStatsResponse)
def get_person_stats(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> PersonStatsResponse:
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    stats = person_service.get_person_stats(db, person_id)
    return PersonStatsResponse(**stats)


@router.get("/people/{person_id}/frames", response_model=list[FaceFrameResponse])
def get_person_frames(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> list[FaceFrameResponse]:
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    samples = person_service.list_face_samples(db, person_id)
    return [
        FaceFrameResponse(
            filename=item["filename"],
            is_primary=item["is_primary"],
            url=f"{settings.API_V1_PREFIX}/faces/{item['filename']}",
        )
        for item in samples
    ]


@router.get("/people/{person_id}/quality", response_model=ProfileQualityResponse)
def get_person_quality(
    person_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> ProfileQualityResponse:
    quality = person_service.get_profile_quality(db, person_id)
    return ProfileQualityResponse(**quality)


@router.patch("/people/{person_id}/primary-photo", response_model=PersonResponse)
def set_primary_photo(
    person_id: int,
    body: PrimaryPhotoRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> PersonResponse:
    person = person_service.set_primary_photo(db, person_id, body.filename)
    return PersonResponse.model_validate(person)


@router.patch("/people/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    body: PersonUpdate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
) -> PersonResponse:
    person = person_service.update_person_details(
        db, person_id, name=body.name, notes=body.notes, category=body.category
    )
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return PersonResponse.model_validate(person)
