from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.company import Company

from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


# ----------------------------------------
# Get All Departments
# ----------------------------------------
def get_all_departments(db: Session):
    return db.query(Department).all()


# ----------------------------------------
# Get Department By ID
# ----------------------------------------
def get_department_by_id(
    db: Session,
    department_id: int,
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise ValueError("Department not found")

    return department


# ----------------------------------------
# Create Department
# ----------------------------------------
def create_department(
    db: Session,
    department: DepartmentCreate,
):

    company = (
        db.query(Company)
        .filter(Company.id == department.company_id)
        .first()
    )

    if not company:
        raise ValueError("Company not found")

    existing = (
        db.query(Department)
        .filter(
            Department.name == department.name,
            Department.company_id == department.company_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Department already exists in this company"
        )

    new_department = Department(
        name=department.name,
        description=department.description,
        company_id=department.company_id,
        is_active=department.is_active,
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


# ----------------------------------------
# Update Department
# ----------------------------------------
def update_department(
    db: Session,
    department_id: int,
    department_data: DepartmentUpdate,
):

    department = get_department_by_id(
        db,
        department_id,
    )

    if department_data.company_id is not None:

        company = (
            db.query(Company)
            .filter(
                Company.id == department_data.company_id
            )
            .first()
        )

        if not company:
            raise ValueError("Company not found")

        department.company_id = (
            department_data.company_id
        )

    if department_data.name is not None:
        department.name = department_data.name

    if department_data.description is not None:
        department.description = (
            department_data.description
        )

    if department_data.is_active is not None:
        department.is_active = (
            department_data.is_active
        )

    db.commit()
    db.refresh(department)

    return department


# ----------------------------------------
# Delete Department
# ----------------------------------------
def delete_department(
    db: Session,
    department_id: int,
):

    department = get_department_by_id(
        db,
        department_id,
    )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }