from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate
)


# -------------------------
# Get All Companies
# -------------------------
def get_all_companies(db: Session):
    return db.query(Company).all()


# -------------------------
# Get Company By ID
# -------------------------
def get_company_by_id(
    db: Session,
    company_id: int
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise ValueError("Company not found")

    return company


# -------------------------
# Create Company
# -------------------------
def create_company(
    db: Session,
    company: CompanyCreate
):

    existing = db.query(Company).filter(
        Company.name == company.name
    ).first()

    if existing:
        raise ValueError(
            "Company already exists"
        )

    new_company = Company(
        name=company.name,
        email=company.email,
        phone=company.phone,
        address=company.address,
        website=company.website,
        is_active=company.is_active
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


# -------------------------
# Update Company
# -------------------------
def update_company(
    db: Session,
    company_id: int,
    company_data: CompanyUpdate
):

    company = get_company_by_id(
        db,
        company_id
    )

    if company_data.name is not None:
        company.name = company_data.name

    if company_data.email is not None:
        company.email = company_data.email

    if company_data.phone is not None:
        company.phone = company_data.phone

    if company_data.address is not None:
        company.address = company_data.address

    if company_data.website is not None:
        company.website = company_data.website

    if company_data.is_active is not None:
        company.is_active = company_data.is_active

    db.commit()
    db.refresh(company)

    return company


# -------------------------
# Delete Company
# -------------------------
def delete_company(
    db: Session,
    company_id: int
):

    company = get_company_by_id(
        db,
        company_id
    )

    db.delete(company)
    db.commit()

    return {
        "message": "Company deleted successfully"
    }