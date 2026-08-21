from sqlalchemy.orm import Session, joinedload

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


# -------------------------------
# Get All Tasks
# -------------------------------
def get_all_tasks(db: Session):
    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .all()
    )


# -------------------------------
# Get Task By ID
# -------------------------------
def get_task_by_id(task_id: int, db: Session):
    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )


# -------------------------------
# Create Task
# -------------------------------
def create_task(task: TaskCreate, created_by: int, db: Session):
    new_task = Task(
        name=task.name,
        description=task.description,
        project_id=task.project_id,
        assigned_to=task.assigned_to,
        created_by=created_by,
        status=task.status,
        priority=task.priority,
        start_date=task.start_date,
        due_date=task.due_date,
        is_active=task.is_active,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == new_task.id)
        .first()
    )


# -------------------------------
# Update Task
# -------------------------------
def update_task(task_id: int, task: TaskUpdate, db: Session):
    db_task = (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )

    if not db_task:
        return None

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )


# -------------------------------
# Delete Task
# -------------------------------
def delete_task(task_id: int, db: Session):
    db_task = (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )

    if not db_task:
        return None

    db.delete(db_task)
    db.commit()

    return True