from sqlalchemy.orm import Session

from app.models.dependency import Dependency
from app.models.task import Task
from app.schemas.dependency import (
    DependencyCreate,
    DependencyUpdate,
)


# -------------------------------
# Get All Dependencies
# -------------------------------
def get_all_dependencies(db: Session):
    return (
        db.query(Dependency)
        .all()
    )


# -------------------------------
# Get Dependency By ID
# -------------------------------
def get_dependency_by_id(
    dependency_id: int,
    db: Session
):
    return (
        db.query(Dependency)
        .filter(Dependency.id == dependency_id)
        .first()
    )


# -------------------------------
# Get Dependencies For Task
# -------------------------------
def get_task_dependencies(
    task_id: int,
    db: Session
):
    return (
        db.query(Dependency)
        .filter(
            (Dependency.predecessor_task_id == task_id)
            |
            (Dependency.successor_task_id == task_id)
        )
        .all()
    )


# -------------------------------
# Create Dependency
# -------------------------------
def create_dependency(
    dependency: DependencyCreate,
    db: Session
):
    # ----------------------------------
    # 1. Prevent Self Dependency
    # ----------------------------------

    if (
        dependency.predecessor_task_id
        == dependency.successor_task_id
    ):
        raise ValueError(
            "A task cannot depend on itself."
        )

    # ----------------------------------
    # 2. Check Predecessor Task
    # ----------------------------------

    predecessor = (
        db.query(Task)
        .filter(
            Task.id
            == dependency.predecessor_task_id
        )
        .first()
    )

    if not predecessor:
        raise ValueError(
            "Predecessor task does not exist."
        )

    # ----------------------------------
    # 3. Check Successor Task
    # ----------------------------------

    successor = (
        db.query(Task)
        .filter(
            Task.id
            == dependency.successor_task_id
        )
        .first()
    )

    if not successor:
        raise ValueError(
            "Successor task does not exist."
        )

    # ----------------------------------
    # 4. Prevent Duplicate Dependency
    # ----------------------------------

    existing_dependency = (
        db.query(Dependency)
        .filter(
            Dependency.predecessor_task_id
            == dependency.predecessor_task_id,
            Dependency.successor_task_id
            == dependency.successor_task_id,
        )
        .first()
    )

    if existing_dependency:
        raise ValueError(
            "This dependency already exists."
        )

    # ----------------------------------
    # 5. Create Dependency
    # ----------------------------------

    new_dependency = Dependency(
        predecessor_task_id=dependency.predecessor_task_id,
        successor_task_id=dependency.successor_task_id,
        dependency_type=dependency.dependency_type,
        lag_days=dependency.lag_days,
    )

    db.add(new_dependency)
    db.commit()
    db.refresh(new_dependency)

    return new_dependency


# -------------------------------
# Update Dependency
# -------------------------------
def update_dependency(
    dependency_id: int,
    dependency: DependencyUpdate,
    db: Session
):
    db_dependency = (
        db.query(Dependency)
        .filter(
            Dependency.id == dependency_id
        )
        .first()
    )

    if not db_dependency:
        return None

    update_data = dependency.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_dependency,
            key,
            value
        )

    db.commit()
    db.refresh(db_dependency)

    return db_dependency


# -------------------------------
# Delete Dependency
# -------------------------------
def delete_dependency(
    dependency_id: int,
    db: Session
):
    db_dependency = (
        db.query(Dependency)
        .filter(
            Dependency.id == dependency_id
        )
        .first()
    )

    if not db_dependency:
        return None

    db.delete(db_dependency)
    db.commit()

    return True