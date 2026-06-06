from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profile_image_path: str | None
    created_at: datetime
