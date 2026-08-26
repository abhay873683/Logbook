from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.file_version import FileVersion


def get_file_or_error(
    db: Session,
    file_id: int,
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
        raise ValueError("File not found")

    return file


def get_next_version_number(
    db: Session,
    file_id: int,
):
    current_version = (
        db.query(
            func.max(FileVersion.version_number)
        )
        .filter(
            FileVersion.file_id == file_id
        )
        .scalar()
    )

    return (current_version or 0) + 1


def create_file_version(
    db: Session,
    file_id: int,
    uploaded_by: int,
    file_path: str,
    file_size: int,
):
    get_file_or_error(
        db,
        file_id,
    )

    version_number = get_next_version_number(
        db,
        file_id,
    )

    version = FileVersion(
        file_id=file_id,
        version_number=version_number,
        file_path=file_path,
        file_size=file_size,
        uploaded_by=uploaded_by,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


def get_file_versions(
    db: Session,
    file_id: int,
):
    get_file_or_error(
        db,
        file_id,
    )

    return (
        db.query(FileVersion)
        .filter(
            FileVersion.file_id == file_id
        )
        .order_by(
            FileVersion.version_number.desc()
        )
        .all()
    )


def get_file_version_by_id(
    db: Session,
    file_id: int,
    version_id: int,
):
    version = (
        db.query(FileVersion)
        .filter(
            FileVersion.id == version_id,
            FileVersion.file_id == file_id,
        )
        .first()
    )

    if not version:
        raise ValueError(
            "File version not found"
        )

    return version


def delete_file_version(
    db: Session,
    file_id: int,
    version_id: int,
):
    version = get_file_version_by_id(
        db,
        file_id,
        version_id,
    )

    db.delete(version)
    db.commit()

    return {
        "message": "File version deleted successfully"
    }