from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


def normalize_name(name: str) -> str:
    value = (name or "").strip()

    if not value:
        raise HTTPException(
            status_code=400,
            detail="Folder name cannot be empty",
        )

    return value


def get_owned_folder(
    db: Session,
    folder_id: int,
    user_id: int,
):
    folder = (
        db.query(Folder)
        .filter(
            Folder.id == folder_id,
            Folder.owner_id == user_id,
        )
        .first()
    )

    if not folder:
        raise HTTPException(
            status_code=404,
            detail="Folder not found",
        )

    return folder


def ensure_unique_name(
    db: Session,
    user_id: int,
    name: str,
    parent_id: int | None,
    exclude_folder_id: int | None = None,
):
    query = db.query(Folder).filter(
        Folder.owner_id == user_id,
        Folder.parent_id == parent_id,
        Folder.name.ilike(name),
    )

    if exclude_folder_id is not None:
        query = query.filter(
            Folder.id != exclude_folder_id
        )

    if query.first():
        raise HTTPException(
            status_code=409,
            detail=(
                "A folder with this name already "
                "exists in the same location"
            ),
        )


def validate_parent(
    db: Session,
    user_id: int,
    parent_id: int | None,
):
    if parent_id is None:
        return None

    return get_owned_folder(
        db=db,
        folder_id=parent_id,
        user_id=user_id,
    )


def ensure_not_descendant(
    db: Session,
    folder: Folder,
    new_parent_id: int | None,
    user_id: int,
):
    if new_parent_id is None:
        return

    if new_parent_id == folder.id:
        raise HTTPException(
            status_code=400,
            detail="Folder cannot be its own parent",
        )

    current = get_owned_folder(
        db=db,
        folder_id=new_parent_id,
        user_id=user_id,
    )

    visited = set()

    while current is not None:
        if current.id in visited:
            raise HTTPException(
                status_code=409,
                detail="Invalid circular folder hierarchy",
            )

        visited.add(current.id)

        if current.id == folder.id:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Folder cannot be moved inside "
                    "one of its descendants"
                ),
            )

        if current.parent_id is None:
            break

        current = get_owned_folder(
            db=db,
            folder_id=current.parent_id,
            user_id=user_id,
        )


def create_folder(
    db: Session,
    user_id: int,
    data: FolderCreate,
):
    name = normalize_name(data.name)

    validate_parent(
        db=db,
        user_id=user_id,
        parent_id=data.parent_id,
    )

    ensure_unique_name(
        db=db,
        user_id=user_id,
        name=name,
        parent_id=data.parent_id,
    )

    folder = Folder(
        name=name,
        description=data.description,
        parent_id=data.parent_id,
        owner_id=user_id,
    )

    try:
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder

    except Exception:
        db.rollback()
        raise


def get_folders(
    db: Session,
    user_id: int,
):
    return (
        db.query(Folder)
        .filter(
            Folder.owner_id == user_id
        )
        .order_by(Folder.created_at.desc())
        .all()
    )


def get_folder_by_id(
    db: Session,
    folder_id: int,
    user_id: int,
):
    return get_owned_folder(
        db=db,
        folder_id=folder_id,
        user_id=user_id,
    )


def update_folder(
    db: Session,
    folder_id: int,
    user_id: int,
    data: FolderUpdate,
):
    folder = get_owned_folder(
        db=db,
        folder_id=folder_id,
        user_id=user_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    new_name = folder.name
    new_parent_id = folder.parent_id

    if "name" in update_data:
        new_name = normalize_name(
            update_data["name"]
        )

    if "parent_id" in update_data:
        new_parent_id = update_data["parent_id"]

        validate_parent(
            db=db,
            user_id=user_id,
            parent_id=new_parent_id,
        )

        ensure_not_descendant(
            db=db,
            folder=folder,
            new_parent_id=new_parent_id,
            user_id=user_id,
        )

    ensure_unique_name(
        db=db,
        user_id=user_id,
        name=new_name,
        parent_id=new_parent_id,
        exclude_folder_id=folder.id,
    )

    if "name" in update_data:
        folder.name = new_name

    if "description" in update_data:
        folder.description = update_data[
            "description"
        ]

    if "parent_id" in update_data:
        folder.parent_id = new_parent_id

    try:
        db.commit()
        db.refresh(folder)
        return folder

    except Exception:
        db.rollback()
        raise


def delete_folder(
    db: Session,
    folder_id: int,
    user_id: int,
):
    folder = get_owned_folder(
        db=db,
        folder_id=folder_id,
        user_id=user_id,
    )

    try:
        db.delete(folder)
        db.commit()

        return {
            "message": "Folder deleted successfully"
        }

    except Exception:
        db.rollback()
        raise
