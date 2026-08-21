from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.comment import Comment
from app.models.file import File
from app.models.notification import Notification
from app.models.task_progress import TaskProgress


# ---------------------------------
# Dashboard Statistics
# ---------------------------------

def get_dashboard_stats(db: Session):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_projects": db.query(func.count(Project.id)).scalar(),
        "total_tasks": db.query(func.count(Task.id)).scalar(),
        "total_subtasks": db.query(func.count(Subtask.id)).scalar(),
        "total_comments": db.query(func.count(Comment.id)).scalar(),
        "total_files": db.query(func.count(File.id)).scalar(),
        "total_notifications": db.query(func.count(Notification.id)).scalar(),
        "total_progress_updates": db.query(func.count(TaskProgress.id)).scalar(),
    }


# ---------------------------------
# Recent Tasks
# ---------------------------------

def get_recent_tasks(
    db: Session,
    limit: int = 5,
):
    return (
        db.query(Task)
        .order_by(Task.created_at.desc())
        .limit(limit)
        .all()
    )


# ---------------------------------
# Recent Notifications
# ---------------------------------

def get_recent_notifications(
    db: Session,
    limit: int = 5,
):
    return (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )