from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.file import File
from app.models.notification import Notification
from app.models.project import Project
from app.models.project_user import ProjectUser
from app.models.subtask import Subtask
from app.models.task import Task
from app.models.task_progress import TaskProgress


def _accessible_project_ids(
    db: Session,
    user_id: int,
):
    created_ids = (
        db.query(
            Project.id.label("project_id")
        )
        .filter(
            Project.created_by == user_id,
            Project.is_active.is_(True),
        )
    )

    member_ids = (
        db.query(
            ProjectUser.project_id.label(
                "project_id"
            )
        )
        .join(
            Project,
            Project.id
            == ProjectUser.project_id,
        )
        .filter(
            ProjectUser.user_id == user_id,
            Project.is_active.is_(True),
        )
    )

    return created_ids.union(
        member_ids
    ).subquery()


def get_dashboard_stats(
    db: Session,
    user_id: int,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
    )

    accessible_ids = db.query(
        project_ids.c.project_id
    )

    total_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.id.in_(accessible_ids)
        )
        .scalar()
        or 0
    )

    total_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id.in_(
                accessible_ids
            )
        )
        .scalar()
        or 0
    )

    total_subtasks = (
        db.query(func.count(Subtask.id))
        .join(
            Task,
            Task.id == Subtask.task_id,
        )
        .filter(
            Task.project_id.in_(
                accessible_ids
            )
        )
        .scalar()
        or 0
    )

    total_comments = (
        db.query(func.count(Comment.id))
        .join(
            Task,
            Task.id == Comment.task_id,
        )
        .filter(
            Task.project_id.in_(
                accessible_ids
            )
        )
        .scalar()
        or 0
    )

    total_files = (
        db.query(func.count(File.id))
        .outerjoin(
            Task,
            Task.id == File.task_id,
        )
        .filter(
            (
                File.uploaded_by == user_id
            )
            | (
                Task.project_id.in_(
                    accessible_ids
                )
            )
        )
        .scalar()
        or 0
    )

    total_notifications = (
        db.query(
            func.count(Notification.id)
        )
        .filter(
            Notification.user_id
            == user_id
        )
        .scalar()
        or 0
    )

    total_progress_updates = (
        db.query(
            func.count(TaskProgress.id)
        )
        .join(
            Task,
            Task.id
            == TaskProgress.task_id,
        )
        .filter(
            Task.project_id.in_(
                accessible_ids
            )
        )
        .scalar()
        or 0
    )

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "total_subtasks": total_subtasks,
        "total_comments": total_comments,
        "total_files": total_files,
        "total_notifications": (
            total_notifications
        ),
        "total_progress_updates": (
            total_progress_updates
        ),
    }


def get_recent_tasks(
    db: Session,
    user_id: int,
    limit: int = 5,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
    )

    accessible_ids = db.query(
        project_ids.c.project_id
    )

    return (
        db.query(Task)
        .filter(
            Task.project_id.in_(
                accessible_ids
            )
        )
        .order_by(
            Task.created_at.desc()
        )
        .limit(limit)
        .all()
    )


def get_recent_notifications(
    db: Session,
    user_id: int,
    limit: int = 5,
):
    return (
        db.query(Notification)
        .filter(
            Notification.user_id
            == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(limit)
        .all()
    )