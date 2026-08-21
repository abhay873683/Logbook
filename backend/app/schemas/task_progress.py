from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ---------------------------------
# Base Schema
# ---------------------------------

class TaskProgressBase(BaseModel):
    task_id: int
    progress: int = Field(..., ge=0, le=100)
    status: str
    note: Optional[str] = None


# ---------------------------------
# Create Progress
# ---------------------------------

class TaskProgressCreate(TaskProgressBase):
    pass


# ---------------------------------
# Update Progress
# ---------------------------------

class TaskProgressUpdate(BaseModel):
    progress: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    note: Optional[str] = None


# ---------------------------------
# Response Schema
# ---------------------------------

class TaskProgressResponse(TaskProgressBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True