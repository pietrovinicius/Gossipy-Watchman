from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    person_id: int
    person_name: str
    video_id: int
    video_file_name: str
    timestamp_in_video: float
    message: str
    seen: bool
    created_at: datetime
