from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profile_image_path: str | None
    created_at: datetime


class PersonUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name não pode ser vazio")
        return v
