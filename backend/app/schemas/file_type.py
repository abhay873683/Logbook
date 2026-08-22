from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileTypeResponse(BaseModel):
    id: int
    name: str
    extension: str
    mime_type: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True