from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from app.services.task_service import (
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)


router = APIRouter(
    tags=["Tasks"]
)


# ---------------------------------------
# GET ALL TASKS
# ---------------------------------------
@router.get(
    "/",
    response_model=list[TaskResponse]
)
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_tasks(db)


# ---------------------------------------
# GET TASK BY ID
# ---------------------------------------
@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(
        task_id,
        db
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ---------------------------------------
# CREATE TASK
# ---------------------------------------
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201
)
def create_new_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_task(
            task=task,
            created_by=current_user.id,
            db=db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------
# UPDATE TASK
# ---------------------------------------
@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_existing_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_task = update_task(
            task_id,
            task,
            db
        )

        if not updated_task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return updated_task

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------
# DELETE TASK
# ---------------------------------------
@router.delete("/{task_id}")
def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_task(
        task_id,
        db
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted successfully"
    }