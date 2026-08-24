from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.subtask import SubtaskResponse


# -----------------------------------
# Base Task Schema
# -----------------------------------
class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None

    project_id: int
    team_id: Optional[int] = None
    assigned_to: Optional[int] = None

    # Service validation lowercase enum keys expect karti hai
    status: str = "todo"
    priority: str = "medium"

    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

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
    team_id: Optional[int] = None
    assigned_to: Optional[int] = None

    status: Optional[str] = None
    priority: Optional[str] = None

    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    progress: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )

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
    subtasks: List[SubtaskResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )