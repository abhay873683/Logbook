from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True