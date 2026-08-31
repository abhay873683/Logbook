from typing import Any

from pydantic import BaseModel


class SearchResult(BaseModel):
    resource_type: str
    resource_id: int
    title: str
    snippet: str | None = None
    relevance: float
    metadata: dict[str, Any] = {}


class SearchResponse(BaseModel):
    query: str
    resource_type: str
    total: int
    skip: int
    limit: int
    results: list[SearchResult]
