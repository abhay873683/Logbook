from pydantic import BaseModel


class SummaryReport(BaseModel):
    total_users: int
    total_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    active_files: int


class ProjectReport(BaseModel):
    id: int
    name: str
    status: str
    progress: int
    total_tasks: int
    completed_tasks: int


class TaskStatusReport(BaseModel):
    status: str
    count: int


class UserProductivityReport(BaseModel):
    user_id: int
    email: str
    assigned_tasks: int
    completed_tasks: int