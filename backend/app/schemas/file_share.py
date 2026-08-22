from pydantic import BaseModel
from datetime import datetime


class FileShareCreate(BaseModel):
    file_id: int
    shared_with: int
    permission: str = "read"  # read / update


class FileShareResponse(BaseModel):
    id: int
    file_id: int
    shared_by: int
    shared_with: int
    permission: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True