from sqlalchemy.orm import Session, joinedload

from app.models.task import Task
from app.models.project import Project
from app.models.team import Team
from app.models.user import User

from app.schemas.task import TaskCreate, TaskUpdate


# =========================================================
# Allowed Values
# =========================================================

ALLOWED_TASK_STATUSES = {
    "todo",
    "in_progress",
    "review",
    "done",
    "cancelled",
}

ALLOWED_TASK_PRIORITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


# =========================================================
# Helper - Validate Status
# =========================================================

def validate_task_status(status: str):

    if status not in ALLOWED_TASK_STATUSES:
        raise ValueError(
            "Invalid task status. Allowed statuses: "
            "todo, in_progress, review, done, cancelled"
        )


# =========================================================
# Helper - Validate Priority
# =========================================================

def validate_task_priority(priority: str):

    if priority not in ALLOWED_TASK_PRIORITIES:
        raise ValueError(
            "Invalid task priority. Allowed priorities: "
            "low, medium, high, critical"
        )


# =========================================================
# Helper - Validate Project
# =========================================================

def validate_project(db: Session, project_id: int):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    return project


# =========================================================
# Helper - Validate Team
# =========================================================

def validate_team(db: Session, team_id: int):

    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise ValueError("Team not found")

    return team


# =========================================================
# Helper - Validate Assigned User
# =========================================================

def validate_assigned_user(
    db: Session,
    assigned_to: int | None
):

    if assigned_to is None:
        return None

    user = (
        db.query(User)
        .filter(User.id == assigned_to)
        .first()
    )

    if not user:
        raise ValueError("Assigned user not found")

    return user


# =========================================================
# Helper - Validate Team / Project
# =========================================================

def validate_team_project(
    project: Project,
    team: Team | None
):

    if team is None:
        return

    if project.team_id is not None:
        if project.team_id != team.id:
            raise ValueError(
                "Team does not belong to this project"
            )


# =========================================================
# Helper - Validate Dates
# =========================================================

def validate_task_dates(
    start_date,
    due_date
):

    if (
        start_date is not None
        and due_date is not None
        and start_date > due_date
    ):
        raise ValueError(
            "Start date cannot be after due date"
        )


# =========================================================
# Get All Tasks
# =========================================================

def get_all_tasks(db: Session):

    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .all()
    )


# =========================================================
# Get Task By ID
# =========================================================

def get_task_by_id(
    task_id: int,
    db: Session
):

    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )


# =========================================================
# Create Task
# =========================================================

def create_task(
    task: TaskCreate,
    created_by: int,
    db: Session
):

    # -----------------------------------------------------
    # Validate Project
    # -----------------------------------------------------

    project = validate_project(
        db,
        task.project_id
    )

    # -----------------------------------------------------
    # Validate Team
    # -----------------------------------------------------

    team = None

    if task.team_id is not None:

        team = validate_team(
            db,
            task.team_id
        )

        validate_team_project(
            project,
            team
        )

    # -----------------------------------------------------
    # Validate Assigned User
    # -----------------------------------------------------

    validate_assigned_user(
        db,
        task.assigned_to
    )

    # -----------------------------------------------------
    # Validate Status
    # -----------------------------------------------------

    validate_task_status(
        task.status
    )

    # -----------------------------------------------------
    # Validate Priority
    # -----------------------------------------------------

    validate_task_priority(
        task.priority
    )

    # -----------------------------------------------------
    # Validate Dates
    # -----------------------------------------------------

    validate_task_dates(
        task.start_date,
        task.due_date
    )

    # -----------------------------------------------------
    # Create Task
    # -----------------------------------------------------

    new_task = Task(
        name=task.name,
        description=task.description,
        project_id=task.project_id,
        team_id=task.team_id,
        assigned_to=task.assigned_to,
        created_by=created_by,
        status=task.status,
        priority=task.priority,
        progress=task.progress,
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


# =========================================================
# Update Task
# =========================================================

def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session
):

    db_task = (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )

    if not db_task:
        return None

    update_data = task.model_dump(
        exclude_unset=True
    )

    # -----------------------------------------------------
    # Final Project ID
    # -----------------------------------------------------

    final_project_id = update_data.get(
        "project_id",
        db_task.project_id
    )

    project = validate_project(
        db,
        final_project_id
    )

    # -----------------------------------------------------
    # Final Team ID
    # -----------------------------------------------------

    final_team_id = update_data.get(
        "team_id",
        db_task.team_id
    )

    if final_team_id is not None:

        team = validate_team(
            db,
            final_team_id
        )

        validate_team_project(
            project,
            team
        )

    # -----------------------------------------------------
    # Assigned User Validation
    # -----------------------------------------------------

    if "assigned_to" in update_data:

        validate_assigned_user(
            db,
            update_data["assigned_to"]
        )

    # -----------------------------------------------------
    # Status Validation
    # -----------------------------------------------------

    if "status" in update_data:

        validate_task_status(
            update_data["status"]
        )

    # -----------------------------------------------------
    # Priority Validation
    # -----------------------------------------------------

    if "priority" in update_data:

        validate_task_priority(
            update_data["priority"]
        )

    # -----------------------------------------------------
    # Final Dates
    # -----------------------------------------------------

    final_start_date = update_data.get(
        "start_date",
        db_task.start_date
    )

    final_due_date = update_data.get(
        "due_date",
        db_task.due_date
    )

    validate_task_dates(
        final_start_date,
        final_due_date
    )

    # -----------------------------------------------------
    # Update Fields
    # -----------------------------------------------------

    for key, value in update_data.items():

        setattr(
            db_task,
            key,
            value
        )

    db.commit()

    db.refresh(db_task)

    return (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )


# =========================================================
# Delete Task
# =========================================================

def delete_task(
    task_id: int,
    db: Session
):

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