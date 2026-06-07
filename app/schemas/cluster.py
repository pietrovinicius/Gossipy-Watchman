from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ClusterSuggestionResponse(BaseModel):
    id: int
    group_id: int
    person_id: int
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClusterGroupResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    suggestions: list[ClusterSuggestionResponse]

    model_config = ConfigDict(from_attributes=True)
