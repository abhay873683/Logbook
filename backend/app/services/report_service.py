from datetime import datetime, timezone

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum
from app.models.file import File


def _status_value(value):
    return value.value if hasattr(value, "value") else str(value)


# =========================================================
# SUMMARY
# =========================================================

def get_summary_report(db: Session):
    now = datetime.now(timezone.utc)

    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "total_projects": db.query(func.count(Project.id)).scalar() or 0,
        "total_tasks": db.query(func.count(Task.id)).scalar() or 0,

        "completed_tasks": (
            db.query(func.count(Task.id))
            .filter(Task.status == TaskStatusEnum.done)
            .scalar()
            or 0
        ),

        "overdue_tasks": (
            db.query(func.count(Task.id))
            .filter(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status != TaskStatusEnum.done,
                Task.is_active == True,
            )
            .scalar()
            or 0
        ),

        "active_files": (
            db.query(func.count(File.id))
            .filter(File.is_active == True)
            .scalar()
            or 0
        ),
    }


# =========================================================
# DEPARTMENT SUMMARY
# =========================================================

def get_department_summary(
    db: Session,
    department_id: int,
):
    total_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.department_id == department_id
        )
        .scalar()
        or 0
    )

    project_ids = (
        db.query(Project.id)
        .filter(
            Project.department_id == department_id
        )
        .subquery()
    )

    total_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id.in_(
                db.query(project_ids.c.id)
            )
        )
        .scalar()
        or 0
    )

    return {
        "department_id": department_id,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
    }


# =========================================================
# PROJECT REPORTS
# =========================================================

def get_all_project_reports(db: Session):
    projects = db.query(Project).all()

    result = []

    for project in projects:
        total_tasks = (
            db.query(func.count(Task.id))
            .filter(Task.project_id == project.id)
            .scalar()
            or 0
        )

        completed_tasks = (
            db.query(func.count(Task.id))
            .filter(
                Task.project_id == project.id,
                Task.status == TaskStatusEnum.done,
            )
            .scalar()
            or 0
        )

        result.append({
            "id": project.id,
            "name": project.name,
            "status": _status_value(project.status),
            "progress": project.progress or 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
        })

    return result


def get_project_report(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    total_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project.id)
        .scalar()
        or 0
    )

    completed_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id == project.id,
            Task.status == TaskStatusEnum.done,
        )
        .scalar()
        or 0
    )

    return {
        "id": project.id,
        "name": project.name,
        "status": _status_value(project.status),
        "progress": project.progress or 0,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
    }


def get_project_tasks_report(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .all()
    )

    return [
        {
            "id": task.id,
            "name": task.name,
            "status": _status_value(task.status),
            "priority": _status_value(task.priority),
            "progress": task.progress or 0,
            "assigned_to": task.assigned_to,
            "due_date": task.due_date,
        }
        for task in tasks
    ]


# =========================================================
# TASK REPORTS
# =========================================================

def get_all_task_reports(db: Session):
    tasks = db.query(Task).all()

    return [
        {
            "id": task.id,
            "name": task.name,
            "project_id": task.project_id,
            "status": _status_value(task.status),
            "priority": _status_value(task.priority),
            "progress": task.progress or 0,
            "assigned_to": task.assigned_to,
            "due_date": task.due_date,
        }
        for task in tasks
    ]


def get_task_status_distribution(db: Session):
    rows = (
        db.query(
            Task.status,
            func.count(Task.id),
        )
        .group_by(Task.status)
        .all()
    )

    return [
        {
            "status": _status_value(status),
            "count": count,
        }
        for status, count in rows
    ]


def get_overdue_tasks(db: Session):
    now = datetime.now(timezone.utc)

    tasks = (
        db.query(Task)
        .filter(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != TaskStatusEnum.done,
            Task.is_active == True,
        )
        .all()
    )

    return [
        {
            "id": task.id,
            "name": task.name,
            "project_id": task.project_id,
            "status": _status_value(task.status),
            "due_date": task.due_date,
        }
        for task in tasks
    ]


# =========================================================
# USER PRODUCTIVITY
# =========================================================

def get_user_productivity(db: Session):
    users = db.query(User).all()

    result = []

    for user in users:
        assigned_tasks = (
            db.query(func.count(Task.id))
            .filter(Task.assigned_to == user.id)
            .scalar()
            or 0
        )

        completed_tasks = (
            db.query(func.count(Task.id))
            .filter(
                Task.assigned_to == user.id,
                Task.status == TaskStatusEnum.done,
            )
            .scalar()
            or 0
        )

        result.append({
            "user_id": user.id,
            "email": user.email,
            "assigned_tasks": assigned_tasks,
            "completed_tasks": completed_tasks,
        })

    return result


def get_user_report(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    assigned_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.assigned_to == user.id)
        .scalar()
        or 0
    )

    completed_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.assigned_to == user.id,
            Task.status == TaskStatusEnum.done,
        )
        .scalar()
        or 0
    )

    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "assigned_tasks": assigned_tasks,
        "completed_tasks": completed_tasks,
    }


# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

def get_reports_dashboard(db: Session):
    return {
        "summary": get_summary_report(db),
        "task_status": get_task_status_distribution(db),
        "projects": get_all_project_reports(db),
        "user_productivity": get_user_productivity(db),
    }