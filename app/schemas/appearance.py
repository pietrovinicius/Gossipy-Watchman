from pydantic import BaseModel, ConfigDict, Field


class AppearanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    video_id: int
    timestamp_start: float
    timestamp_end: float | None
    confidence: float
    file_name: str


class ManualAppearanceCreate(BaseModel):
    person_id: int
    timestamp_start: float = Field(ge=0.0)
    timestamp_end: float = Field(ge=0.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
