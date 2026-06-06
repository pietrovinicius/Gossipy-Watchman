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


class VideoStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: VideoStatus
    uploaded_at: datetime
