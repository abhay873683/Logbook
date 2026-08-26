from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class EventLogCreate(BaseModel):
    event_type: str = Field(
        min_length=1,
        max_length=100,
    )

    description: Optional[str] = None

    metadata: Optional[dict[str, Any]] = None

    ip_address: Optional[str] = None


class EventLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    description: Optional[str] = None
    event_metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )