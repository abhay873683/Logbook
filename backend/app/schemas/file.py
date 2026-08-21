from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ----------------------------------------
# Create File
# ----------------------------------------
class FileCreate(BaseModel):
    task_id: int


# ----------------------------------------
# Update File
# ----------------------------------------
class FileUpdate(BaseModel):
    file_name: Optional[str] = None
    is_downloadable: Optional[bool] = None


# ----------------------------------------
# Response File
# ----------------------------------------
class FileResponse(BaseModel):
    id: int
    task_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    is_active: bool
    is_downloadable: bool
    created_at: datetime

    class Config:
        from_attributes = True