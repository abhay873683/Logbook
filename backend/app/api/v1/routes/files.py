from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse as FastAPIFileResponse

from sqlalchemy.orm import Session
import os
import shutil
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.file import (
    FileCreate,
    FileResponse,
)

from app.services.file_service import (
    list_files,
    get_my_files,
    get_file_by_id,
    download_file,
    create_file,
    delete_file,
)

from app.services.activity_log_service import log_activity

router = APIRouter()

UPLOAD_DIR = "uploads"

MAX_FILE_SIZE = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".csv",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".zip",
}

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------------------------------
# List Files (role-based, optional task_id filter)
# ----------------------------------------
@router.get(
    "/",
    response_model=list[FileResponse],
)
def read_files(
    task_id: int = None,
    folder_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_files(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
        task_id=task_id,
        folder_id=folder_id,
    )


# ----------------------------------------
# Get My Files (Employee)
# ----------------------------------------
@router.get(
    "/my",
    response_model=list[FileResponse],
)
def read_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_files(db, current_user.id)


# ----------------------------------------
# Invalid Access (403 demo endpoint)
# ----------------------------------------
@router.get("/invalid-access")
def invalid_access(
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this resource.",
    )


# ----------------------------------------
# Download File (with permission check)
# ----------------------------------------
@router.get("/download/{file_id}")
def download_file_route(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_record = download_file(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
        role=current_user.role,
    )

    return FastAPIFileResponse(
        path=file_record.file_path,
        filename=file_record.file_name,
        media_type=file_record.file_type or "application/octet-stream",
    )


# ----------------------------------------
# Get File By ID (metadata only)
# ----------------------------------------
@router.get(
    "/{file_id}",
    response_model=FileResponse,
)
def read_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_file_by_id(
            file_id=file_id,
            db=db,
            user_id=current_user.id,
            role=current_user.role,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Upload File
# ----------------------------------------
@router.post(
    "/",
    response_model=FileResponse,
    status_code=201,
)
def upload_file(
    task_id: int = Form(...),
    folder_id: int | None = Form(None),
    uploaded_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    original_name = os.path.basename(uploaded_file.filename or "").strip()

    if not original_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name",
        )

    file_extension = os.path.splitext(original_name)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="File type is not allowed",
        )

    uploaded_file.file.seek(0, os.SEEK_END)
    file_size = uploaded_file.file.tell()
    uploaded_file.file.seek(0)

    if file_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="Empty files are not allowed",
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 25 MB size limit",
        )

    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                uploaded_file.file,
                buffer,
            )

        file_data = FileCreate(
            task_id=task_id,
            folder_id=folder_id,
        )
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    result = create_file(
        db=db,
        file_data=file_data,
        uploaded_by=current_user.id,
        file_name=original_name,
        file_path=file_path,
        file_type=uploaded_file.content_type,
        file_size=file_size,
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Uploaded File",
        entity_type="Task",
        entity_id=task_id,
        description=f"Uploaded file: {uploaded_file.filename}",
    )

    return result


# ----------------------------------------
# Delete File (soft delete)
# ----------------------------------------
@router.delete("/{file_id}")
def remove_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_file(
            file_id=file_id,
            db=db,
            user_id=current_user.id,
            role=current_user.role,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )