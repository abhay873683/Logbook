import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File as UploadField,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.file_version import (
    FileVersionResponse,
)

from app.services.file_version_service import (
    create_file_version,
    delete_file_version,
    get_file_version_by_id,
    get_file_versions,
)

from app.services.file_service import get_file_by_id


router = APIRouter()

VERSION_UPLOAD_DIR = "uploads/versions"

os.makedirs(
    VERSION_UPLOAD_DIR,
    exist_ok=True,
)


@router.post(
    "/{file_id}/versions/",
    response_model=FileVersionResponse,
    status_code=201,
)
def upload_new_file_version(
    file_id: int,
    uploaded_file: UploadFile = UploadField(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    extension = os.path.splitext(
        uploaded_file.filename or ""
    )[1]

    unique_name = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        VERSION_UPLOAD_DIR,
        unique_name,
    )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                uploaded_file.file,
                buffer,
            )

        return create_file_version(
            db=db,
            file_id=file_id,
            uploaded_by=current_user.id,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
        )

    except ValueError as exc:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{file_id}/versions/",
    response_model=list[FileVersionResponse],
)
def read_file_versions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    try:
        return get_file_versions(
            db,
            file_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{file_id}/versions/{version_id}",
    response_model=FileVersionResponse,
)
def read_file_version(
    file_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    try:
        return get_file_version_by_id(
            db,
            file_id,
            version_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete(
    "/{file_id}/versions/{version_id}"
)
def remove_file_version(
    file_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    try:
        return delete_file_version(
            db,
            file_id,
            version_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )