from fastapi import FastAPI

from app.core.database import Base, engine


# ==========================
# Import All Models
# ==========================

from app.models.user import User
from app.models.company import Company
from app.models.department import Department
from app.models.project import Project
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.comment import Comment
from app.models.file import File
from app.models.notification import Notification
from app.models.task_progress import TaskProgress
from app.models.subtask_progress import SubtaskProgress
from app.models.comment_reply import CommentReply
from app.models.activity_log import ActivityLog
from app.models.file_type import FileType
from app.models.file_share import FileShare

# TreeFlow Dependency Engine
from app.models.dependency import Dependency


# ==========================
# Create Database Tables
# ==========================

Base.metadata.create_all(bind=engine)


# ==========================
# Import Routes
# ==========================

from app.api.v1.routes import health
from app.api.v1.routes import auth
from app.api.v1.routes import users
from app.api.v1.routes import company
from app.api.v1.routes import department
from app.api.v1.routes import projects
from app.api.v1.routes import tasks
from app.api.v1.routes import subtasks
from app.api.v1.routes import comments
from app.api.v1.routes import files
from app.api.v1.routes import progress
from app.api.v1.routes import notification
from app.api.v1.routes import dashboard
from app.api.v1.routes import subtask_progress
from app.api.v1.routes import comment_reply
from app.api.v1.routes import activity_log
from app.api.v1.routes import file_type
from app.api.v1.routes import restore
from app.api.v1.routes import trash
from app.api.v1.routes import file_share
from app.api.v1.routes import revoke_share
from app.api.v1.routes import file_report

# TreeFlow Dependency Engine
from app.api.v1.routes import dependency


# ==========================
# FastAPI App
# ==========================

app = FastAPI(
    title="TreeFlow AI API",
    description="Backend API for TreeFlow AI",
    version="1.0.0",
)


# ==========================
# Health
# ==========================

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)


# ==========================
# Authentication
# ==========================

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


# ==========================
# Users
# ==========================

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)


# ==========================
# Companies
# ==========================

app.include_router(
    company.router,
    prefix="/api/v1/companies",
    tags=["Companies"]
)


# ==========================
# Departments
# ==========================

app.include_router(
    department.router,
    prefix="/api/v1/departments",
    tags=["Departments"]
)


# ==========================
# Projects
# ==========================

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["Projects"]
)


# ==========================
# Tasks
# ==========================

app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["Tasks"]
)


# ==========================
# Task Dependencies
# ==========================

app.include_router(
    dependency.router,
    prefix="/api/v1/dependencies",
    tags=["Task Dependencies"]
)


# ==========================
# Subtask Progress
# MUST be before Subtasks router
# ==========================

app.include_router(
    subtask_progress.router,
    prefix="/api/v1/subtasks",
    tags=["Subtask Progress"]
)


# ==========================
# Subtasks
# ==========================

app.include_router(
    subtasks.router,
    prefix="/api/v1/subtasks",
    tags=["Subtasks"]
)


# ==========================
# Comment Replies
# MUST be before Comments router
# ==========================

app.include_router(
    comment_reply.router,
    prefix="/api/v1/comments",
    tags=["Comment Reply"]
)


# ==========================
# Comments
# ==========================

app.include_router(
    comments.router,
    prefix="/api/v1/comments",
    tags=["Comments"]
)


# ==========================
# Files
# ==========================

app.include_router(
    files.router,
    prefix="/api/v1/files",
    tags=["Files"]
)


# ==========================
# Task Progress
# ==========================

app.include_router(
    progress.router,
    prefix="/api/v1/progress",
    tags=["Task Progress"]
)


# ==========================
# Notifications
# ==========================

app.include_router(
    notification.router,
    prefix="/api/v1/notification",
    tags=["Notification"]
)


# ==========================
# Dashboard
# ==========================

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


# ==========================
# Activity Logs
# ==========================

app.include_router(
    activity_log.router,
    prefix="/api/v1/activity",
    tags=["Activity Logs"]
)


# ==========================
# File Types
# ==========================

app.include_router(
    file_type.router,
    prefix="/api/v1/file-types",
    tags=["File Types"]
)


# ==========================
# File Restore
# ==========================

app.include_router(
    restore.router,
    prefix="/api/v1/restore",
    tags=["File Restore"]
)


# ==========================
# Trash
# ==========================

app.include_router(
    trash.router,
    prefix="/api/v1/trash",
    tags=["Trash"]
)


# ==========================
# File Share
# ==========================

app.include_router(
    file_share.router,
    prefix="/api/v1/file-share",
    tags=["File Share"]
)


# ==========================
# Revoke Share
# ==========================

app.include_router(
    revoke_share.router,
    prefix="/api/v1/revoke-share",
    tags=["Revoke Share"]
)


# ==========================
# File Report
# ==========================

app.include_router(
    file_report.router,
    prefix="/api/v1/file-report",
    tags=["File Report"]
)


# ==========================
# Root
# ==========================

@app.get("/")
def root():
    return {
        "message": "Welcome to TreeFlow AI API"
    }