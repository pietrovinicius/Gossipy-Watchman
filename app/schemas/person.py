from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


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


class PersonUpdate(BaseModel):
    name: str
    notes: str | None = None
    category: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
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
