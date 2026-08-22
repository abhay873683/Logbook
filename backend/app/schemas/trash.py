from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TrashItem(BaseModel):
    file_id: int
    file_name: str
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    file_type: Optional[str] = None
    size: Optional[int] = None

    class Config:
        from_attributes = True