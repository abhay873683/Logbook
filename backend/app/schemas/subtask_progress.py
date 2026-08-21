from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubtaskProgressBase(BaseModel):
    subtask_id: int
    progress: float = Field(..., ge=0, le=100)
    status: Optional[str] = "In Progress"
    note: Optional[str] = None

class SubtaskProgressCreate(SubtaskProgressBase):
    pass

class SubtaskProgressUpdate(BaseModel):
    progress: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    note: Optional[str] = None

class SubtaskProgressResponse(SubtaskProgressBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True