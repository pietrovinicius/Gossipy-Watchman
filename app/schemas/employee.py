from datetime import datetime
from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    registration: str = Field(..., min_length=1)
    department: str | None = None
    role: str | None = None
    notes: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    department: str | None = None
    role: str | None = None
    notes: str | None = None
    active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    registration: str
    department: str | None
    role: str | None
    photo_path: str | None
    embedding_path: str | None
    person_id: int | None
    active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
