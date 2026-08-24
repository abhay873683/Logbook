from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.models.task_assignee import TaskAssignee

from app.schemas.task_assignee import TaskAssigneeCreate


# =========================================================
# Get All Task Assignees
# =========================================================

def get_all_task_assignees(db: Session):
    return db.query(TaskAssignee).all()


# =========================================================
# Get Assignees For One Task
# =========================================================

def get_task_assignees(
    db: Session,
    task_id: int,
):
    # Validate Task
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise ValueError("Task not found")

    return (
        db.query(TaskAssignee)
        .filter(TaskAssignee.task_id == task_id)
        .all()
    )


# =========================================================
# Get Task Assignee By ID
# =========================================================

def get_task_assignee_by_id(
    db: Session,
    assignment_id: int,
):
    assignment = (
        db.query(TaskAssignee)
        .filter(TaskAssignee.id == assignment_id)
        .first()
    )

    if not assignment:
        raise ValueError("Task assignment not found")

    return assignment


# =========================================================
# Add User To Task
# =========================================================

def add_task_assignee(
    db: Session,
    assignment: TaskAssigneeCreate,
):
    # -----------------------------------------------------
    # Validate Task
    # -----------------------------------------------------
    task = (
        db.query(Task)
        .filter(Task.id == assignment.task_id)
        .first()
    )

    if not task:
        raise ValueError("Task not found")

    # -----------------------------------------------------
    # Validate User
    # -----------------------------------------------------
    user = (
        db.query(User)
        .filter(User.id == assignment.user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User is not active")

    # -----------------------------------------------------
    # Prevent Duplicate Assignment
    # -----------------------------------------------------
    existing = (
        db.query(TaskAssignee)
        .filter(
            TaskAssignee.task_id == assignment.task_id,
            TaskAssignee.user_id == assignment.user_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "User is already assigned to this task"
        )

    # -----------------------------------------------------
    # Create Assignment
    # -----------------------------------------------------
    new_assignment = TaskAssignee(
        task_id=assignment.task_id,
        user_id=assignment.user_id,
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment


# =========================================================
# Remove Task Assignee
# =========================================================

def remove_task_assignee(
    db: Session,
    assignment_id: int,
):
    assignment = get_task_assignee_by_id(
        db,
        assignment_id,
    )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Task assignee removed successfully"
    }