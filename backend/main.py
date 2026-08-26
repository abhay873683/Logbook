from fastapi import FastAPI

from app.core.database import Base, engine


# =========================================================
# Import All Models
# =========================================================

from app.models import *


# =========================================================
# Create Database Tables
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# Import API Routes
# =========================================================

from app.api.v1.routes import health
from app.api.v1.routes import auth
from app.api.v1.routes import users
from app.api.v1.routes import company
from app.api.v1.routes import department
from app.api.v1.routes import teams
from app.api.v1.routes import projects
from app.api.v1.routes import tasks
from app.api.v1.routes import task_assignees
from app.api.v1.routes import subtasks
from app.api.v1.routes import comments
from app.api.v1.routes import files
from app.api.v1.routes import file_versions
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
from app.api.v1.routes import dependency

# Day 33 - Reports & Analytics
from app.api.v1.routes import reports


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="TreeFlow AI API",
    description="Backend API for TreeFlow AI",
    version="1.0.0",
)


# =========================================================
# Health
# =========================================================

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)


# =========================================================
# Authentication
# =========================================================

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# =========================================================
# Users
# =========================================================

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"],
)


# =========================================================
# Companies
# =========================================================

app.include_router(
    company.router,
    prefix="/api/v1/companies",
    tags=["Companies"],
)


# =========================================================
# Departments
# =========================================================

app.include_router(
    department.router,
    prefix="/api/v1/departments",
    tags=["Departments"],
)


# =========================================================
# Teams
# =========================================================

app.include_router(
    teams.router,
    prefix="/api/v1/teams",
    tags=["Teams"],
)


# =========================================================
# Projects
# =========================================================

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["Projects"],
)


# =========================================================
# Tasks
# =========================================================

app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["Tasks"],
)


# =========================================================
# Task Assignees
# =========================================================

app.include_router(
    task_assignees.router,
    prefix="/api/v1/task-assignees",
    tags=["Task Assignees"],
)


# =========================================================
# Subtask Progress
# IMPORTANT: Register before generic Subtasks router
# =========================================================

app.include_router(
    subtask_progress.router,
    prefix="/api/v1/subtasks",
    tags=["Subtask Progress"],
)


# =========================================================
# Subtasks
# =========================================================

app.include_router(
    subtasks.router,
    prefix="/api/v1/subtasks",
    tags=["Subtasks"],
)


# =========================================================
# Comment Replies
# IMPORTANT: Register before generic Comments router
# =========================================================

app.include_router(
    comment_reply.router,
    prefix="/api/v1/comments",
    tags=["Comment Reply"],
)


# =========================================================
# Comments
# =========================================================

app.include_router(
    comments.router,
    prefix="/api/v1/comments",
    tags=["Comments"],
)


# =========================================================
# Files
# =========================================================

app.include_router(
    files.router,
    prefix="/api/v1/files",
    tags=["Files"],
)


# =========================================================
# File Versions - Day 32
# =========================================================

app.include_router(
    file_versions.router,
    prefix="/api/v1/files",
    tags=["File Versions"],
)


# =========================================================
# Task Progress
# =========================================================

app.include_router(
    progress.router,
    prefix="/api/v1/progress",
    tags=["Task Progress"],
)


# =========================================================
# Notifications
# =========================================================

app.include_router(
    notification.router,
    prefix="/api/v1/notification",
    tags=["Notification"],
)


# =========================================================
# Dashboard
# =========================================================

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


# =========================================================
# Reports & Analytics - Day 33
# =========================================================

app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports & Analytics"],
)


# =========================================================
# Activity Logs
# =========================================================

app.include_router(
    activity_log.router,
    prefix="/api/v1/activity",
    tags=["Activity Logs"],
)


# =========================================================
# File Types
# =========================================================

app.include_router(
    file_type.router,
    prefix="/api/v1/file-types",
    tags=["File Types"],
)


# =========================================================
# File Restore
# =========================================================

app.include_router(
    restore.router,
    prefix="/api/v1/restore",
    tags=["File Restore"],
)


# =========================================================
# Trash
# =========================================================

app.include_router(
    trash.router,
    prefix="/api/v1/trash",
    tags=["Trash"],
)


# =========================================================
# File Share
# =========================================================

app.include_router(
    file_share.router,
    prefix="/api/v1/file-share",
    tags=["File Share"],
)


# =========================================================
# Revoke Share
# =========================================================

app.include_router(
    revoke_share.router,
    prefix="/api/v1/revoke-share",
    tags=["Revoke Share"],
)


# =========================================================
# File Report
# =========================================================

app.include_router(
    file_report.router,
    prefix="/api/v1/file-report",
    tags=["File Report"],
)


# =========================================================
# Task Dependencies
# =========================================================

app.include_router(
    dependency.router,
    prefix="/api/v1/dependencies",
    tags=["Dependencies"],
)


# =========================================================
# Root Endpoint
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to TreeFlow AI API"
    }