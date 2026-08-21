from sqlalchemy.orm import Session

from app.models.subtask import Subtask
from app.schemas.subtask import (
    SubtaskCreate,
    SubtaskUpdate,
)


# --------------------------------------
# Get All Subtasks
# --------------------------------------
def get_all_subtasks(db: Session):
    return db.query(Subtask).all()


# --------------------------------------
# Get Subtask By ID
# --------------------------------------
def get_subtask_by_id(
    subtask_id: int,
    db: Session,
):
    return (
        db.query(Subtask)
        .filter(Subtask.id == subtask_id)
        .first()
    )


# --------------------------------------
# Create Subtask
# --------------------------------------
def create_subtask(
    subtask: SubtaskCreate,
    created_by: int,
    db: Session,
):
    new_subtask = Subtask(
        title=subtask.title,
        description=subtask.description,
        task_id=subtask.task_id,
        created_by=created_by,
        status=subtask.status,
        is_active=subtask.is_active,
    )

    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)

    return new_subtask


# --------------------------------------
# Update Subtask
# --------------------------------------
def update_subtask(
    subtask_id: int,
    subtask: SubtaskUpdate,
    db: Session,
):
    db_subtask = (
        db.query(Subtask)
        .filter(Subtask.id == subtask_id)
        .first()
    )

    if not db_subtask:
        return None

    update_data = subtask.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_subtask, key, value)

    db.commit()
    db.refresh(db_subtask)

    return db_subtask


# --------------------------------------
# Delete Subtask
# --------------------------------------
def delete_subtask(
    subtask_id: int,
    db: Session,
):
    db_subtask = (
        db.query(Subtask)
        .filter(Subtask.id == subtask_id)
        .first()
    )

    if not db_subtask:
        return False

    db.delete(db_subtask)
    db.commit()

    return True