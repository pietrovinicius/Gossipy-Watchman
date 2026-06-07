from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.video import VideoStatus


class VideoCreate(BaseModel):
    file_name: str
    file_path: str


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    file_path: str
    status: VideoStatus
    uploaded_at: datetime
    deleted_at: datetime | None = None


class VideoStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: VideoStatus
    uploaded_at: datetime


class AppearanceDetail(BaseModel):
    id: int
    timestamp_start: float
    timestamp_end: float | None
    confidence: float


class PersonInVideo(BaseModel):
    person_id: int
    person_name: str
    person_category: str
    profile_image_path: str | None
    total_seconds: float
    appearance_count: int
    first_seen_at: float
    last_seen_at: float
    appearances: list[AppearanceDetail]


class VideoSummary(BaseModel):
    total_people: int
    total_appearances: int
    duration_covered: float
    processing_status: str


class VideoDetailResponse(BaseModel):
    video: VideoResponse
    people: list[PersonInVideo]
    summary: VideoSummary


class PersonPreview(BaseModel):
    person_id: int
    person_name: str
    profile_image_path: str | None


class VideoCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    file_path: str
    status: VideoStatus
    uploaded_at: datetime
    deleted_at: datetime | None = None
    people_count: int
    people_previews: list[PersonPreview]


class CatalogResponse(BaseModel):
    items: list[VideoCardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
