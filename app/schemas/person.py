from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class PersonCategory(str, Enum):
    funcionario = "Funcionário"
    visitante = "Visitante"
    desconhecido = "Desconhecido"
    monitorado = "Monitorado"


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profile_image_path: str | None
    created_at: datetime
    notes: str | None = None
    category: str = PersonCategory.desconhecido.value

    @field_validator("category", mode="before")
    @classmethod
    def default_category_if_none(cls, v: Any) -> str:
        if v is None:
            return PersonCategory.desconhecido.value
        return v


class PersonStatsResponse(BaseModel):
    video_count: int
    total_seconds: float
    first_seen: datetime | None
    last_seen: datetime | None


class FaceFrameResponse(BaseModel):
    filename: str
    is_primary: bool
    url: str


class PrimaryPhotoRequest(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def filename_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("filename não pode ser vazio")
        return v


class MergeRequest(BaseModel):
    primary_id: int
    secondary_ids: list[int]

    @model_validator(mode="after")
    def secondary_must_not_include_primary(self) -> "MergeRequest":
        if self.primary_id in self.secondary_ids:
            raise ValueError("primary_id não pode estar em secondary_ids")
        if not self.secondary_ids:
            raise ValueError("secondary_ids não pode ser vazio")
        return self


class PersonUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None
    category: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PersonUpdate":
        if self.name is None and self.notes is None and self.category is None:
            raise ValueError("pelo menos um campo deve ser fornecido")
        return self

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name não pode ser vazio")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        valid = {e.value for e in PersonCategory}
        if v not in valid:
            raise ValueError(f"category deve ser um de: {sorted(valid)}")
        return v
