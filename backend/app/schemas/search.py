from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    resource_type: str
    resource_id: int
    title: str
    snippet: str | None = None
    relevance: float
    semantic_score: float | None = None
    hybrid_score: float | None = None
    created_at: datetime | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class SearchResponse(BaseModel):
    query: str
    resource_type: str
    total: int
    skip: int
    limit: int
    sort_by: str
    filters: dict[str, Any] = Field(
        default_factory=dict
    )
    results: list[SearchResult]
