from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.file_share import FileShare
from app.schemas.file_share import FileShareCreate


def share_file(
    db: Session,
    data: FileShareCreate,
    user_id: int,
    role: str,
):
    normalized_role = (role or "").strip().lower()

    file = (
        db.query(File)
        .filter(
            File.id == data.file_id,
            File.is_active == True,
        )
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    allowed_roles = {"admin", "super_admin", "manager"}

    if normalized_role not in allowed_roles and file.uploaded_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to share this file",
        )

    existing_share = (
        db.query(FileShare)
        .filter(
            FileShare.file_id == data.file_id,
            FileShare.shared_with == data.shared_with,
            FileShare.is_active == True,
        )
        .first()
    )

    if existing_share:
        raise HTTPException(
            status_code=409,
            detail="File is already shared with this user",
        )

    share = FileShare(
        file_id=data.file_id,
        shared_by=user_id,
        shared_with=data.shared_with,
        permission=data.permission,
        is_active=True,
    )

    try:
        db.add(share)
        db.commit()
        db.refresh(share)
        return share
    except Exception:
        db.rollback()
        raise
