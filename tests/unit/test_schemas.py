from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


# ── VideoCreate ──────────────────────────────────────────────────────────────

def test_video_create_valid():
    from app.schemas.video import VideoCreate
    v = VideoCreate(file_name="clip.mp4", file_path="storage/videos/clip.mp4")
    assert v.file_name == "clip.mp4"
    assert v.file_path == "storage/videos/clip.mp4"


def test_video_create_missing_file_name():
    from app.schemas.video import VideoCreate
    with pytest.raises(ValidationError):
        VideoCreate(file_path="storage/videos/clip.mp4")


def test_video_create_missing_file_path():
    from app.schemas.video import VideoCreate
    with pytest.raises(ValidationError):
        VideoCreate(file_name="clip.mp4")


# ── VideoResponse ─────────────────────────────────────────────────────────────

def test_video_response_from_orm():
    from app.schemas.video import VideoResponse
    from app.models.video import Video, VideoStatus

    orm_obj = Video(
        id=1,
        file_name="clip.mp4",
        file_path="storage/videos/clip.mp4",
        status=VideoStatus.PENDENTE,
        uploaded_at=datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc),
    )
    schema = VideoResponse.model_validate(orm_obj)
    assert schema.id == 1
    assert schema.file_name == "clip.mp4"
    assert schema.status == VideoStatus.PENDENTE


def test_video_response_wrong_type():
    from app.schemas.video import VideoResponse
    with pytest.raises(ValidationError):
        VideoResponse(id="nao_inteiro", file_name=1, file_path=2, status="X", uploaded_at="errado")


# ── VideoStatusResponse ───────────────────────────────────────────────────────

def test_video_status_response_fields():
    from app.schemas.video import VideoStatusResponse
    from app.models.video import VideoStatus
    v = VideoStatusResponse(
        id=5,
        status=VideoStatus.PROCESSANDO,
        uploaded_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
    )
    assert v.id == 5
    assert v.status == VideoStatus.PROCESSANDO


# ── PersonResponse ────────────────────────────────────────────────────────────

def test_person_response_from_orm():
    from app.schemas.person import PersonResponse
    from app.models.person import Person

    orm_obj = Person(
        id=2,
        name="Desconhecido #1",
        profile_image_path="storage/faces/2.jpg",
        created_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
    )
    schema = PersonResponse.model_validate(orm_obj)
    assert schema.id == 2
    assert schema.name == "Desconhecido #1"


def test_person_response_optional_profile_image():
    from app.schemas.person import PersonResponse
    from app.models.person import Person

    orm_obj = Person(
        id=3,
        name="Desconhecido #2",
        profile_image_path=None,
        created_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
    )
    schema = PersonResponse.model_validate(orm_obj)
    assert schema.profile_image_path is None


# ── __init__ exports ──────────────────────────────────────────────────────────

def test_schemas_init_exports():
    from app.schemas import VideoCreate, VideoResponse, VideoStatusResponse, PersonResponse
    assert VideoCreate is not None
    assert VideoResponse is not None
    assert VideoStatusResponse is not None
    assert PersonResponse is not None
