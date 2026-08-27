# ============================================================
# TreeFlow AI - Main Application
# ============================================================

from fastapi import FastAPI

from app.core.database import Base, engine


# ============================================================
# Import All Models
# ============================================================

from app.models import *


# ============================================================
# Create Database Tables
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# Import API Routes
# ============================================================

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

from app.api.v1.routes import progress
from app.api.v1.routes import subtask_progress

from app.api.v1.routes import dependency

from app.api.v1.routes import comments
from app.api.v1.routes import comment_reply

from app.api.v1.routes import files
from app.api.v1.routes import file_versions
from app.api.v1.routes import file_type
from app.api.v1.routes import file_share
from app.api.v1.routes import revoke_share
from app.api.v1.routes import restore
from app.api.v1.routes import trash
from app.api.v1.routes import file_report

# Day 39 - Folder Management
from app.api.v1.routes import folders

from app.api.v1.routes import notification
from app.api.v1.routes import activity_log

from app.api.v1.routes import dashboard
from app.api.v1.routes import reports

from app.api.v1.routes import chat
from app.api.v1.routes import chat_ws

from app.api.v1.routes import ai

from app.api.v1.routes import notification_events
from app.api.v1.routes import notification_ws

# Day 41 - Time Tracking
from app.api.v1.routes import time_tracking


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="TreeFlow AI API",
    description="Backend API for TreeFlow AI",
    version="1.0.0",
)


# ============================================================
# Health
# ============================================================

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)


# ============================================================
# Authentication
# ============================================================

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# ============================================================
# Users
# ============================================================

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"],
)


# ============================================================
# Companies
# ============================================================

app.include_router(
    company.router,
    prefix="/api/v1/companies",
    tags=["Companies"],
)


# ============================================================
# Departments
# ============================================================

app.include_router(
    department.router,
    prefix="/api/v1/departments",
    tags=["Departments"],
)


# ============================================================
# Teams
# ============================================================

app.include_router(
    teams.router,
    prefix="/api/v1/teams",
    tags=["Teams"],
)


# ============================================================
# Projects
# ============================================================

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["Projects"],
)


# ============================================================
# Tasks
# ============================================================

app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["Tasks"],
)


# ============================================================
# Task Assignees
# ============================================================

app.include_router(
    task_assignees.router,
    prefix="/api/v1/task-assignees",
    tags=["Task Assignees"],
)


# ============================================================
# Subtasks
# ============================================================

app.include_router(
    subtasks.router,
    prefix="/api/v1/subtasks",
    tags=["Subtasks"],
)


# ============================================================
# Subtask Progress
# ============================================================

app.include_router(
    subtask_progress.router,
    prefix="/api/v1/subtasks",
    tags=["Subtask Progress"],
)


# ============================================================
# Task Progress
# ============================================================

app.include_router(
    progress.router,
    prefix="/api/v1/progress",
    tags=["Task Progress"],
)


# ============================================================
# Task Dependencies
# ============================================================

app.include_router(
    dependency.router,
    prefix="/api/v1/dependencies",
    tags=["Dependencies"],
)


# ============================================================
# Comments
# ============================================================

app.include_router(
    comments.router,
    prefix="/api/v1/comments",
    tags=["Comments"],
)


# ============================================================
# Comment Replies
# ============================================================

app.include_router(
    comment_reply.router,
    prefix="/api/v1/comments",
    tags=["Comment Reply"],
)


# ============================================================
# Files
# ============================================================

app.include_router(
    files.router,
    prefix="/api/v1/files",
    tags=["Files"],
)


# ============================================================
# File Versions
# ============================================================

app.include_router(
    file_versions.router,
    prefix="/api/v1/files",
    tags=["File Versions"],
)


# ============================================================
# Folder Management - Day 39
# ============================================================

app.include_router(
    folders.router,
    prefix="/api/v1/files/folders",
    tags=["Folders"],
)


# ============================================================
# File Types
# ============================================================

app.include_router(
    file_type.router,
    prefix="/api/v1/file-types",
    tags=["File Types"],
)


# ============================================================
# File Share
# ============================================================

app.include_router(
    file_share.router,
    prefix="/api/v1/file-share",
    tags=["File Share"],
)


# ============================================================
# Revoke Share
# ============================================================

app.include_router(
    revoke_share.router,
    prefix="/api/v1/revoke-share",
    tags=["Revoke Share"],
)


# ============================================================
# File Restore
# ============================================================

app.include_router(
    restore.router,
    prefix="/api/v1/restore",
    tags=["File Restore"],
)


# ============================================================
# Trash
# ============================================================

app.include_router(
    trash.router,
    prefix="/api/v1/trash",
    tags=["Trash"],
)


# ============================================================
# File Report
# ============================================================

app.include_router(
    file_report.router,
    prefix="/api/v1/file-report",
    tags=["File Report"],
)


# ============================================================
# Existing Notifications
# ============================================================

app.include_router(
    notification.router,
    prefix="/api/v1/notification",
    tags=["Notification"],
)


# ============================================================
# Notification Preferences & Event Logs
# ============================================================

app.include_router(
    notification_events.router,
    prefix="/api/v1",
    tags=["Notification Events"],
)


# ============================================================
# Real-time Notification WebSocket
# ============================================================

app.include_router(
    notification_ws.router,
    prefix="/api/v1",
    tags=["Real-time Notifications"],
)


# ============================================================
# Activity Logs
# ============================================================

app.include_router(
    activity_log.router,
    prefix="/api/v1/activity",
    tags=["Activity Logs"],
)


# ============================================================
# Dashboard
# ============================================================

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# Reports & Analytics
# ============================================================

app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports & Analytics"],
)


# ============================================================
# Chat & Collaboration
# ============================================================

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat & Collaboration"],
)


# ============================================================
# Real-time WebSocket Chat
# ============================================================

app.include_router(
    chat_ws.router,
    prefix="/api/v1",
    tags=["Real-time Chat"],
)


# ============================================================
# AI Assistant
# ============================================================

app.include_router(
    ai.router,
    prefix="/api/v1/ai",
    tags=["AI Assistant"],
)


# ============================================================
# Time Tracking - Day 41
# ============================================================

app.include_router(
    time_tracking.router,
    prefix="/api/v1/time-tracking",
    tags=["Time Tracking"],
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to TreeFlow AI API"
    }