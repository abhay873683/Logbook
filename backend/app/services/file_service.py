from sqlalchemy.orm import Session
from fastapi import HTTPException
import os

from app.models.file import File
from app.schemas.file import FileCreate


# ----------------------------------------
# List Files (role-based, optional task_id filter)
# ----------------------------------------
def list_files(
    db: Session,
    user_id: int,
    role: str,
    task_id: int = None,
):
    query = db.query(File).filter(File.is_active == True)

    # Employee can only see their own uploaded files
    if role == "employee":
        query = query.filter(File.uploaded_by == user_id)

    if task_id:
        query = query.filter(File.task_id == task_id)

    return query.order_by(File.created_at.desc()).all()


# ----------------------------------------
# Get Files Uploaded By a Specific User (for "My Files")
# ----------------------------------------
def get_my_files(db: Session, user_id: int):
    return db.query(File).filter(
        File.uploaded_by == user_id,
        File.is_active == True,
    ).all()


# ----------------------------------------
# Get File By ID
# ----------------------------------------
def get_file_by_id(file_id: int, db: Session):
    file = db.query(File).filter(
        File.id == file_id,
        File.is_active == True,
    ).first()

    if not file:
        raise ValueError("File not found")

    return file


# ----------------------------------------
# Download File (with permission + existence check)
# ----------------------------------------
def download_file(db: Session, file_id: int, user_id: int, role: str):
    file = db.query(File).filter(
        File.id == file_id,
        File.is_active == True,
        File.is_downloadable == True,
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Employee can only download their own files
    if role == "employee" and file.uploaded_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to download this file",
        )

    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found on server",
        )

    return file


# ----------------------------------------
# Create File
# ----------------------------------------
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

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file


# ----------------------------------------
# Delete File (Soft Delete)
# ----------------------------------------
def delete_file(file_id: int, db: Session):
    file = db.query(File).filter(
        File.id == file_id,
        File.is_active == True,
    ).first()

    if not file:
        raise ValueError("File not found")

    file.is_active = False
    db.commit()

    return {
        "message": "File deleted successfully"
    }