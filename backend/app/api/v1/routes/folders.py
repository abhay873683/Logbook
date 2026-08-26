from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.folder import (
    FolderCreate,
    FolderUpdate,
    FolderResponse,
)

from app.services.folder_service import (
    create_folder,
    get_folders,
    get_folder_by_id,
    update_folder,
    delete_folder,
)


router = APIRouter()


@router.post(
    "/",
    response_model=FolderResponse,
    status_code=201,
)
def create_new_folder(
    data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_folder(
            db,
            current_user.id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[FolderResponse],
)
def read_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_folders(
        db,
        current_user.id,
    )


@router.get(
    "/{folder_id}",
    response_model=FolderResponse,
)
def read_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_folder_by_id(
            db,
            folder_id,
            current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/{folder_id}",
    response_model=FolderResponse,
)
def edit_folder(
    folder_id: int,
    data: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_folder(
            db,
            folder_id,
            current_user.id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete(
    "/{folder_id}"
)
def remove_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_folder(
            db,
            folder_id,
            current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )