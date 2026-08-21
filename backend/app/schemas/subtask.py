from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --------------------------------------
# Base Schema
# --------------------------------------
class SubtaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    is_active: bool = True


# --------------------------------------
# Create Schema
# --------------------------------------
class SubtaskCreate(SubtaskBase):
    task_id: int


# --------------------------------------
# Update Schema
# --------------------------------------
class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


# --------------------------------------
# Response Schema
# --------------------------------------
class SubtaskResponse(SubtaskBase):
    id: int
    task_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True