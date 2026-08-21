from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.subtask import (
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
)

from app.services.subtask_service import (
    get_all_subtasks,
    get_subtask_by_id,
    create_subtask,
    update_subtask,
    delete_subtask,
)

router = APIRouter(
    tags=["Subtasks"]
)


# --------------------------------------
# GET ALL SUBTASKS
# --------------------------------------
@router.get("/", response_model=list[SubtaskResponse])
def read_subtasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_subtasks(db)


# --------------------------------------
# GET SUBTASK BY ID
# --------------------------------------
@router.get("/{subtask_id}", response_model=SubtaskResponse)
def read_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subtask = get_subtask_by_id(subtask_id, db)

    if not subtask:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    return subtask


# --------------------------------------
# CREATE SUBTASK
# --------------------------------------
@router.post("/", response_model=SubtaskResponse, status_code=201)
def create_new_subtask(
    subtask: SubtaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_subtask(
        subtask=subtask,
        created_by=current_user.id,
        db=db,
    )


# --------------------------------------
# UPDATE SUBTASK
# --------------------------------------
@router.put("/{subtask_id}", response_model=SubtaskResponse)
def update_existing_subtask(
    subtask_id: int,
    subtask: SubtaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_subtask = update_subtask(
        subtask_id,
        subtask,
        db,
    )

    if not updated_subtask:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    return updated_subtask


# --------------------------------------
# DELETE SUBTASK
# --------------------------------------
@router.delete("/{subtask_id}")
def delete_existing_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_subtask(
        subtask_id,
        db,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    return {
        "message": "Subtask deleted successfully"
    }