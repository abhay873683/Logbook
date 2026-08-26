from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


def create_folder(
    db: Session,
    user_id: int,
    data: FolderCreate,
):
    if data.parent_id is not None:
        parent = (
            db.query(Folder)
            .filter(
                Folder.id == data.parent_id,
                Folder.owner_id == user_id,
            )
            .first()
        )

        if not parent:
            raise ValueError("Parent folder not found")

    folder = Folder(
        name=data.name.strip(),
        description=data.description,
        parent_id=data.parent_id,
        owner_id=user_id,
    )

    db.add(folder)
    db.commit()
    db.refresh(folder)

    return folder


def get_folders(
    db: Session,
    user_id: int,
):
    return (
        db.query(Folder)
        .filter(Folder.owner_id == user_id)
        .order_by(Folder.created_at.desc())
        .all()
    )


def get_folder_by_id(
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
        raise ValueError("Folder not found")

    return folder


def update_folder(
    db: Session,
    folder_id: int,
    user_id: int,
    data: FolderUpdate,
):
    folder = get_folder_by_id(
        db,
        folder_id,
        user_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        name = update_data["name"].strip()

        if not name:
            raise ValueError("Folder name cannot be empty")

        folder.name = name

    if "description" in update_data:
        folder.description = update_data["description"]

    if "parent_id" in update_data:
        parent_id = update_data["parent_id"]

        if parent_id == folder.id:
            raise ValueError(
                "Folder cannot be its own parent"
            )

        if parent_id is not None:
            parent = (
                db.query(Folder)
                .filter(
                    Folder.id == parent_id,
                    Folder.owner_id == user_id,
                )
                .first()
            )

            if not parent:
                raise ValueError(
                    "Parent folder not found"
                )

        folder.parent_id = parent_id

    db.commit()
    db.refresh(folder)

    return folder


def delete_folder(
    db: Session,
    folder_id: int,
    user_id: int,
):
    folder = get_folder_by_id(
        db,
        folder_id,
        user_id,
    )

    db.delete(folder)
    db.commit()

    return {
        "message": "Folder deleted successfully"
    }