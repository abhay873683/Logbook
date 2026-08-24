from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskAssigneeBase(BaseModel):
    task_id: int
    user_id: int


class TaskAssigneeCreate(TaskAssigneeBase):
    pass


class TaskAssigneeResponse(TaskAssigneeBase):
    id: int
    assigned_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )