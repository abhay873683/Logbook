from sqlalchemy.orm import Session

from app.models.dependency import Dependency
from app.models.task import Task

from app.schemas.dependency import (
    DependencyCreate,
    DependencyUpdate,
)


# =========================================================
# Get All Dependencies
# =========================================================
def get_all_dependencies(db: Session):
    return db.query(Dependency).all()


# =========================================================
# Get Dependency By ID
# =========================================================
def get_dependency_by_id(
    dependency_id: int,
    db: Session,
):
    return (
        db.query(Dependency)
        .filter(Dependency.id == dependency_id)
        .first()
    )


# =========================================================
# Get Dependencies For Task
# =========================================================
def get_task_dependencies(
    task_id: int,
    db: Session,
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise ValueError("Task not found")

    return (
        db.query(Dependency)
        .filter(
            (Dependency.predecessor_task_id == task_id)
            |
            (Dependency.successor_task_id == task_id)
        )
        .all()
    )


# =========================================================
# Circular Dependency Detection
# =========================================================
def would_create_cycle(
    predecessor_task_id: int,
    successor_task_id: int,
    db: Session,
    exclude_dependency_id: int | None = None,
):
    dependencies = db.query(Dependency)

    if exclude_dependency_id is not None:
        dependencies = dependencies.filter(
            Dependency.id != exclude_dependency_id
        )

    dependencies = dependencies.all()

    # predecessor -> successors graph
    graph = {}

    for item in dependencies:
        graph.setdefault(
            item.predecessor_task_id,
            [],
        ).append(
            item.successor_task_id
        )

    # If successor can reach predecessor,
    # adding predecessor -> successor creates a cycle.
    stack = [successor_task_id]
    visited = set()

    while stack:
        current_task_id = stack.pop()

        if current_task_id == predecessor_task_id:
            return True

        if current_task_id in visited:
            continue

        visited.add(current_task_id)

        for next_task_id in graph.get(
            current_task_id,
            [],
        ):
            if next_task_id not in visited:
                stack.append(next_task_id)

    return False


# =========================================================
# Validate Dependency
# =========================================================
def validate_dependency(
    predecessor_task_id: int,
    successor_task_id: int,
    db: Session,
    exclude_dependency_id: int | None = None,
):
    # -----------------------------------------------------
    # 1. Prevent Self Dependency
    # -----------------------------------------------------
    if predecessor_task_id == successor_task_id:
        raise ValueError(
            "A task cannot depend on itself."
        )

    # -----------------------------------------------------
    # 2. Validate Predecessor Task
    # -----------------------------------------------------
    predecessor = (
        db.query(Task)
        .filter(
            Task.id == predecessor_task_id
        )
        .first()
    )

    if not predecessor:
        raise ValueError(
            "Predecessor task does not exist."
        )

    # -----------------------------------------------------
    # 3. Validate Successor Task
    # -----------------------------------------------------
    successor = (
        db.query(Task)
        .filter(
            Task.id == successor_task_id
        )
        .first()
    )

    if not successor:
        raise ValueError(
            "Successor task does not exist."
        )

    # -----------------------------------------------------
    # 4. Both Tasks Must Belong To Same Project
    # -----------------------------------------------------
    if predecessor.project_id != successor.project_id:
        raise ValueError(
            "Dependency tasks must belong to the same project."
        )

    # -----------------------------------------------------
    # 5. Prevent Duplicate Dependency
    # -----------------------------------------------------
    duplicate_query = (
        db.query(Dependency)
        .filter(
            Dependency.predecessor_task_id
            == predecessor_task_id,

            Dependency.successor_task_id
            == successor_task_id,
        )
    )

    if exclude_dependency_id is not None:
        duplicate_query = duplicate_query.filter(
            Dependency.id != exclude_dependency_id
        )

    existing_dependency = duplicate_query.first()

    if existing_dependency:
        raise ValueError(
            "This dependency already exists."
        )

    # -----------------------------------------------------
    # 6. Prevent Circular Dependency
    # -----------------------------------------------------
    if would_create_cycle(
        predecessor_task_id=predecessor_task_id,
        successor_task_id=successor_task_id,
        db=db,
        exclude_dependency_id=exclude_dependency_id,
    ):
        raise ValueError(
            "Circular dependency detected."
        )

    return predecessor, successor


# =========================================================
# Create Dependency
# =========================================================
def create_dependency(
    dependency: DependencyCreate,
    db: Session,
):
    validate_dependency(
        predecessor_task_id=dependency.predecessor_task_id,
        successor_task_id=dependency.successor_task_id,
        db=db,
    )

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


# =========================================================
# Update Dependency
# =========================================================
def update_dependency(
    dependency_id: int,
    dependency: DependencyUpdate,
    db: Session,
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

    new_predecessor_task_id = update_data.get(
        "predecessor_task_id",
        db_dependency.predecessor_task_id,
    )

    new_successor_task_id = update_data.get(
        "successor_task_id",
        db_dependency.successor_task_id,
    )

    validate_dependency(
        predecessor_task_id=new_predecessor_task_id,
        successor_task_id=new_successor_task_id,
        db=db,
        exclude_dependency_id=dependency_id,
    )

    for key, value in update_data.items():
        setattr(
            db_dependency,
            key,
            value,
        )

    db.commit()
    db.refresh(db_dependency)

    return db_dependency


# =========================================================
# Delete Dependency
# =========================================================
def delete_dependency(
    dependency_id: int,
    db: Session,
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