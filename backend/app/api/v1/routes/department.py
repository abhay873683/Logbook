from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

from app.services.department_service import (
    get_all_departments,
    get_department_by_id,
    create_department,
    update_department,
    delete_department,
)

router = APIRouter()


# ----------------------------------------
# Get All Departments
# ----------------------------------------
@router.get(
    "/",
    response_model=list[DepartmentResponse],
)
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_departments(db)


# ----------------------------------------
# Get Department By ID
# ----------------------------------------
@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_department_by_id(
            db,
            department_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Create Department
# ----------------------------------------
@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=201,
)
def create_new_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_department(
            db,
            department,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ----------------------------------------
# Update Department
# ----------------------------------------
@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_existing_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_department(
            db,
            department_id,
            department,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Delete Department
# ----------------------------------------
@router.delete("/{department_id}")
def delete_existing_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_department(
            db,
            department_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )