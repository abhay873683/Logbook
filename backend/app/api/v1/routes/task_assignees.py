from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.task_assignee import (
    TaskAssigneeCreate,
    TaskAssigneeResponse,
)

from app.services.task_assignee_service import (
    get_all_task_assignees,
    get_task_assignees,
    get_task_assignee_by_id,
    add_task_assignee,
    remove_task_assignee,
)


router = APIRouter(
    tags=["Task Assignees"]
)


# ----------------------------------------
# Get All Task Assignees
# ----------------------------------------
@router.get(
    "/",
    response_model=list[TaskAssigneeResponse],
)
def read_all_task_assignees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_task_assignees(db)


# ----------------------------------------
# Get Assignees For One Task
# ----------------------------------------
@router.get(
    "/task/{task_id}",
    response_model=list[TaskAssigneeResponse],
)
def read_task_assignees(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_task_assignees(
            db,
            task_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Get Assignment By ID
# ----------------------------------------
@router.get(
    "/{assignment_id}",
    response_model=TaskAssigneeResponse,
)
def read_task_assignee(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_task_assignee_by_id(
            db,
            assignment_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Add User To Task
# ----------------------------------------
@router.post(
    "/",
    response_model=TaskAssigneeResponse,
    status_code=201,
)
def create_task_assignee(
    assignment: TaskAssigneeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return add_task_assignee(
            db,
            assignment,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ----------------------------------------
# Remove Task Assignee
# ----------------------------------------
@router.delete("/{assignment_id}")
def delete_task_assignee(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return remove_task_assignee(
            db,
            assignment_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )