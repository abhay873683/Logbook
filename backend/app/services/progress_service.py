from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_progress import TaskProgress

from app.schemas.task_progress import (
    TaskProgressCreate,
    TaskProgressUpdate,
)

from app.services.project_service import get_accessible_project_ids


# ==================================================
# Helper: Get Accessible Task
# ==================================================

def get_accessible_task(
    db: Session,
    task_id: int,
    user_id: int,
):
    accessible_project_ids = get_accessible_project_ids(
        db,
        user_id,
    )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.project_id.in_(accessible_project_ids),
            Task.is_active.is_(True),
        )
        .first()
    )

    if not task:
        raise ValueError(
            "Task not found or access denied"
        )

    return task


# ==================================================
# Get All Accessible Progress
# ==================================================

def get_all_progress(
    db: Session,
    user_id: int,
):
    accessible_project_ids = get_accessible_project_ids(
        db,
        user_id,
    )

    return (
        db.query(TaskProgress)
        .join(
            Task,
            Task.id == TaskProgress.task_id,
        )
        .filter(
            Task.project_id.in_(accessible_project_ids),
            Task.is_active.is_(True),
        )
        .order_by(
            TaskProgress.updated_at.desc(),
            TaskProgress.id.desc(),
        )
        .all()
    )


# ==================================================
# Get Progress By ID
# ==================================================

def get_progress_by_id(
    db: Session,
    progress_id: int,
    user_id: int,
):
    accessible_project_ids = get_accessible_project_ids(
        db,
        user_id,
    )

    progress = (
        db.query(TaskProgress)
        .join(
            Task,
            Task.id == TaskProgress.task_id,
        )
        .filter(
            TaskProgress.id == progress_id,
            Task.project_id.in_(accessible_project_ids),
            Task.is_active.is_(True),
        )
        .first()
    )

    if not progress:
        raise ValueError(
            "Progress not found or access denied"
        )

    return progress


# ==================================================
# Get Progress History For Specific Task
# ==================================================

def get_task_progress_history(
    db: Session,
    task_id: int,
    user_id: int,
):
    # First verify that the current user can access
    # the requested task.
    get_accessible_task(
        db,
        task_id,
        user_id,
    )

    return (
        db.query(TaskProgress)
        .filter(
            TaskProgress.task_id == task_id,
        )
        .order_by(
            TaskProgress.updated_at.desc(),
            TaskProgress.id.desc(),
        )
        .all()
    )


# ==================================================
# Create Progress
# ==================================================

def create_progress(
    db: Session,
    progress: TaskProgressCreate,
    user_id: int,
):
    task = get_accessible_task(
        db,
        progress.task_id,
        user_id,
    )

    new_progress = TaskProgress(
        task_id=progress.task_id,
        user_id=user_id,
        progress=progress.progress,
        status=progress.status,
        note=progress.note,
    )

    db.add(new_progress)

    # Keep the current Task state synchronized
    # with the latest progress update.
    task.progress = progress.progress

    db.commit()

    db.refresh(new_progress)
    db.refresh(task)

    return new_progress


# ==================================================
# Update Progress
# ==================================================

def update_progress(
    db: Session,
    progress_id: int,
    progress: TaskProgressUpdate,
    user_id: int,
):
    db_progress = get_progress_by_id(
        db,
        progress_id,
        user_id,
    )

    update_data = progress.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_progress,
            key,
            value,
        )

    # If this is the newest progress record for the
    # task, keep Task.progress synchronized.
    latest_progress = (
        db.query(TaskProgress)
        .filter(
            TaskProgress.task_id == db_progress.task_id,
        )
        .order_by(
            TaskProgress.updated_at.desc(),
            TaskProgress.id.desc(),
        )
        .first()
    )

    if (
        latest_progress
        and latest_progress.id == db_progress.id
        and progress.progress is not None
    ):
        task = get_accessible_task(
            db,
            db_progress.task_id,
            user_id,
        )

        task.progress = progress.progress

    db.commit()
    db.refresh(db_progress)

    return db_progress


# ==================================================
# Delete Progress
# ==================================================

def delete_progress(
    db: Session,
    progress_id: int,
    user_id: int,
):
    progress = get_progress_by_id(
        db,
        progress_id,
        user_id,
    )

    task_id = progress.task_id

    db.delete(progress)
    db.commit()

    # After deletion, synchronize Task.progress with
    # the newest remaining progress record.
    latest_progress = (
        db.query(TaskProgress)
        .filter(
            TaskProgress.task_id == task_id,
        )
        .order_by(
            TaskProgress.updated_at.desc(),
            TaskProgress.id.desc(),
        )
        .first()
    )

    task = get_accessible_task(
        db,
        task_id,
        user_id,
    )

    if latest_progress:
        task.progress = latest_progress.progress
    else:
        task.progress = 0

    db.commit()
    db.refresh(task)

    return {
        "message": "Progress deleted successfully"
    }