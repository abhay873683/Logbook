from sqlalchemy.orm import Session

from app.models.task_progress import TaskProgress
from app.schemas.task_progress import (
    TaskProgressCreate,
    TaskProgressUpdate,
)


# ---------------------------------
# Get All Progress
# ---------------------------------

def get_all_progress(db: Session):
    return db.query(TaskProgress).all()


# ---------------------------------
# Get Progress By ID
# ---------------------------------

def get_progress_by_id(
    db: Session,
    progress_id: int,
):
    progress = (
        db.query(TaskProgress)
        .filter(TaskProgress.id == progress_id)
        .first()
    )

    if not progress:
        raise ValueError("Progress not found")

    return progress


# ---------------------------------
# Create Progress
# ---------------------------------

def create_progress(
    db: Session,
    progress: TaskProgressCreate,
    user_id: int,
):
    new_progress = TaskProgress(
        task_id=progress.task_id,
        user_id=user_id,
        progress=progress.progress,
        status=progress.status,
        note=progress.note,
    )

    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)

    return new_progress


# ---------------------------------
# Update Progress
# ---------------------------------

def update_progress(
    db: Session,
    progress_id: int,
    progress: TaskProgressUpdate,
):
    db_progress = get_progress_by_id(
        db,
        progress_id,
    )

    update_data = progress.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_progress, key, value)

    db.commit()
    db.refresh(db_progress)

    return db_progress


# ---------------------------------
# Delete Progress
# ---------------------------------

def delete_progress(
    db: Session,
    progress_id: int,
):
    progress = get_progress_by_id(
        db,
        progress_id,
    )

    db.delete(progress)
    db.commit()

    return {
        "message": "Progress deleted successfully"
    }