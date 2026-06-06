from pydantic import BaseModel


class SearchResult(BaseModel):
    person_id: int
    person_name: str
    distance: float
    confidence_pct: int


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query_time_ms: float
