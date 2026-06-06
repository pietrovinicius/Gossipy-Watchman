from pydantic import BaseModel, ConfigDict


class AppearanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    video_id: int
    timestamp_start: float
    timestamp_end: float | None
    confidence: float
    file_name: str
