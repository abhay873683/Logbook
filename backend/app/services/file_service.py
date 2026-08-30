from datetime import datetime, timezone
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.file import File
from app.schemas.file import FileCreate


def can_manage_file(file: File, user_id: int, role: str) -> bool:
    normalized_role = (role or "").strip().lower()

    if normalized_role in {"admin", "super_admin", "manager"}:
        return True

    return file.uploaded_by == user_id


def list_files(
    db: Session,
    user_id: int,
    role: str,
    task_id: int = None,
):
    query = db.query(File).filter(File.is_active == True)

    normalized_role = (role or "").strip().lower()

    if normalized_role in {"employee", "user"}:
        query = query.filter(File.uploaded_by == user_id)

    if task_id is not None:
        query = query.filter(File.task_id == task_id)

    return query.order_by(File.created_at.desc()).all()


def get_my_files(db: Session, user_id: int):
    return (
        db.query(File)
        .filter(
            File.uploaded_by == user_id,
            File.is_active == True,
        )
        .order_by(File.created_at.desc())
        .all()
    )


def get_file_by_id(
    file_id: int,
    db: Session,
    user_id: int | None = None,
    role: str | None = None,
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.is_active == True,
        )
        .first()
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if user_id is not None and role is not None:
        if not can_manage_file(file, user_id, role):
            raise HTTPException(
                status_code=403,
                detail="Not allowed to access this file",
            )

    return file


def download_file(
    db: Session,
    file_id: int,
    user_id: int,
    role: str,
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.is_active == True,
            File.is_downloadable == True,
        )
        .first()
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not can_manage_file(file, user_id, role):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to download this file",
        )

    if not os.path.isfile(file.file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found on server",
        )

    return file


def create_file(
    db: Session,
    file_data: FileCreate,
    uploaded_by: int,
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: int,
):
    new_file = File(
        task_id=file_data.task_id,
        uploaded_by=uploaded_by,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        is_active=True,
        is_downloadable=True,
    )

    try:
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file
    except Exception:
        db.rollback()
        raise


def delete_file(
    file_id: int,
    db: Session,
    user_id: int | None = None,
    role: str | None = None,
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.is_active == True,
        )
        .first()
    )

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if user_id is not None and role is not None:
        if not can_manage_file(file, user_id, role):
            raise HTTPException(
                status_code=403,
                detail="Not allowed to delete this file",
            )

    file.is_active = False
    file.deleted_at = datetime.now(timezone.utc)
    file.deleted_by = user_id

    try:
        db.commit()
        return {"message": "File deleted successfully"}
    except Exception:
        db.rollback()
        raise
