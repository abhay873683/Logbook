from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.subtask import SubtaskResponse


# -----------------------------------
# Base Task Schema
# -----------------------------------

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: int
    assigned_to: Optional[int] = None
    status: str = "todo"
    priority: str = "medium"
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_active: bool = True


# -----------------------------------
# Create Task
# -----------------------------------

class TaskCreate(TaskBase):
    pass


# -----------------------------------
# Update Task
# -----------------------------------

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None


# -----------------------------------
# Response Task
# -----------------------------------

class TaskResponse(TaskBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # -----------------------------------
    # Nested Subtasks
    # -----------------------------------

    subtasks: List[SubtaskResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True