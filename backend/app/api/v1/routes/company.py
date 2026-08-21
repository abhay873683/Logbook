from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
)

from app.models.user import User

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)

from app.services.company_service import (
    get_all_companies,
    get_company_by_id,
    create_company,
    update_company,
    delete_company,
)

router = APIRouter()


# ----------------------------------------
# Get All Companies
# ----------------------------------------
@router.get(
    "/",
    response_model=list[CompanyResponse],
)
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_companies(db)


# ----------------------------------------
# Get Company By ID
# ----------------------------------------
@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_company_by_id(
            db,
            company_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Create Company
# ----------------------------------------
@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=201,
)
def create_new_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_company(
            db,
            company,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ----------------------------------------
# Update Company
# ----------------------------------------
@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_existing_company(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_company(
            db,
            company_id,
            company,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Delete Company
# ----------------------------------------
@router.delete("/{company_id}")
def delete_existing_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_company(
            db,
            company_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )