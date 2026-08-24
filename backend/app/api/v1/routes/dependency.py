from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.dependency import (
    DependencyCreate,
    DependencyUpdate,
    DependencyResponse,
)

from app.services.dependency_service import (
    get_all_dependencies,
    get_dependency_by_id,
    get_task_dependencies,
    create_dependency,
    update_dependency,
    delete_dependency,
)


router = APIRouter(
    tags=["Dependencies"]
)


# =========================================================
# GET ALL DEPENDENCIES
# =========================================================
@router.get(
    "/",
    response_model=list[DependencyResponse],
)
def read_dependencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_dependencies(db)


# =========================================================
# GET DEPENDENCIES FOR TASK
# IMPORTANT: Keep this before /{dependency_id}
# =========================================================
@router.get(
    "/task/{task_id}",
    response_model=list[DependencyResponse],
)
def read_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_task_dependencies(
            task_id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# =========================================================
# GET DEPENDENCY BY ID
# =========================================================
@router.get(
    "/{dependency_id}",
    response_model=DependencyResponse,
)
def read_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dependency = get_dependency_by_id(
        dependency_id,
        db,
    )

    if not dependency:
        raise HTTPException(
            status_code=404,
            detail="Dependency not found",
        )

    return dependency


# =========================================================
# CREATE DEPENDENCY
# =========================================================
@router.post(
    "/",
    response_model=DependencyResponse,
    status_code=201,
)
def create_new_dependency(
    dependency: DependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_dependency(
            dependency=dependency,
            db=db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# =========================================================
# UPDATE DEPENDENCY
# =========================================================
@router.put(
    "/{dependency_id}",
    response_model=DependencyResponse,
)
def update_existing_dependency(
    dependency_id: int,
    dependency: DependencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_dependency = update_dependency(
            dependency_id,
            dependency,
            db,
        )

        if not updated_dependency:
            raise HTTPException(
                status_code=404,
                detail="Dependency not found",
            )

        return updated_dependency

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# =========================================================
# DELETE DEPENDENCY
# =========================================================
@router.delete("/{dependency_id}")
def delete_existing_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_dependency(
        dependency_id,
        db,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Dependency not found",
        )

    return {
        "message": "Dependency deleted successfully"
    }