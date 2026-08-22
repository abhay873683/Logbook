from pydantic import BaseModel
from datetime import datetime


class FileRestore(BaseModel):
    file_id: int


class FileRestoreResponse(BaseModel):
    id: int
    original_name: str
    restored: bool
    restored_at: datetime

    class Config:
        from_attributes = True