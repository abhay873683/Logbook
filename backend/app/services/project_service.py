from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_user import ProjectUser
from app.models.company import Company
from app.models.department import Department
from app.models.team import Team

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


# ----------------------------------------
# Allowed Project Statuses
# ----------------------------------------

ALLOWED_PROJECT_STATUSES = {
    "Planned",
    "In Progress",
    "On Hold",
    "Completed",
    "Cancelled",
}


# ----------------------------------------
# Get Accessible Project IDs
# ----------------------------------------

def get_accessible_project_ids(
    db: Session,
    user_id: int,
):
    created_project_ids = (
        db.query(Project.id)
        .filter(
            Project.created_by == user_id,
            Project.is_active.is_(True),
        )
    )

    member_project_ids = (
        db.query(ProjectUser.project_id)
        .join(
            Project,
            Project.id == ProjectUser.project_id,
        )
        .filter(
            ProjectUser.user_id == user_id,
            Project.is_active.is_(True),
        )
    )

    return created_project_ids.union(
        member_project_ids
    )


# ----------------------------------------
# Get All Accessible Projects
# ----------------------------------------

def get_all_projects(
    db: Session,
    user_id: int,
):
    accessible_ids = get_accessible_project_ids(
        db,
        user_id,
    )

    return (
        db.query(Project)
        .filter(
            Project.id.in_(accessible_ids),
            Project.is_active.is_(True),
        )
        .order_by(
            Project.updated_at.desc(),
            Project.id.desc(),
        )
        .all()
    )


# ----------------------------------------
# Get Accessible Project By ID
# ----------------------------------------

def get_project_by_id(
    db: Session,
    project_id: int,
    user_id: int,
):
    accessible_ids = get_accessible_project_ids(
        db,
        user_id,
    )

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.id.in_(accessible_ids),
            Project.is_active.is_(True),
        )
        .first()
    )

    if not project:
        raise ValueError(
            "Project not found or access denied"
        )

    return project


# ----------------------------------------
# Get Project Owned By Current User
# ----------------------------------------

def get_owned_project_by_id(
    db: Session,
    project_id: int,
    user_id: int,
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.created_by == user_id,
            Project.is_active.is_(True),
        )
        .first()
    )

    if not project:
        raise ValueError(
            "Project not found or permission denied"
        )

    return project


# ----------------------------------------
# Validate Company
# ----------------------------------------

def validate_company(
    db: Session,
    company_id: int,
):
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise ValueError(
            "Company not found"
        )

    return company


# ----------------------------------------
# Validate Department
# ----------------------------------------

def validate_department(
    db: Session,
    department_id: int | None,
    company_id: int,
):
    if department_id is None:
        return None

    department = (
        db.query(Department)
        .filter(
            Department.id == department_id
        )
        .first()
    )

    if not department:
        raise ValueError(
            "Department not found"
        )

    if department.company_id != company_id:
        raise ValueError(
            "Department does not belong to this company"
        )

    return department


# ----------------------------------------
# Validate Team
# ----------------------------------------

def validate_team(
    db: Session,
    team_id: int | None,
    department_id: int | None,
):
    if team_id is None:
        return None

    team = (
        db.query(Team)
        .filter(
            Team.id == team_id
        )
        .first()
    )

    if not team:
        raise ValueError(
            "Team not found"
        )

    if department_id is None:
        raise ValueError(
            "Department is required when assigning a team"
        )

    if team.department_id != department_id:
        raise ValueError(
            "Team does not belong to this department"
        )

    return team


# ----------------------------------------
# Validate Dates
# ----------------------------------------

def validate_project_dates(
    start_date,
    end_date,
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise ValueError(
            "Start date cannot be after end date"
        )


# ----------------------------------------
# Validate Status
# ----------------------------------------

def validate_project_status(
    status: str,
):
    if status not in ALLOWED_PROJECT_STATUSES:
        raise ValueError(
            "Invalid project status. "
            f"Allowed statuses: "
            f"{', '.join(sorted(ALLOWED_PROJECT_STATUSES))}"
        )


# ----------------------------------------
# Validate Progress
# ----------------------------------------

def validate_project_progress(
    progress: int,
):
    if progress < 0 or progress > 100:
        raise ValueError(
            "Project progress must be between 0 and 100"
        )


# ----------------------------------------
# Create Project
# ----------------------------------------

def create_project(
    db: Session,
    project: ProjectCreate,
    current_user,
):
    validate_company(
        db,
        project.company_id,
    )

    validate_department(
        db,
        project.department_id,
        project.company_id,
    )

    validate_team(
        db,
        project.team_id,
        project.department_id,
    )

    validate_project_dates(
        project.start_date,
        project.end_date,
    )

    validate_project_status(
        project.status,
    )

    validate_project_progress(
        project.progress,
    )

    new_project = Project(
        name=project.name,
        description=project.description,
        company_id=project.company_id,
        department_id=project.department_id,
        team_id=project.team_id,
        created_by=current_user.id,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        progress=project.progress,
        is_active=project.is_active,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# ----------------------------------------
# Update Project
# ----------------------------------------

def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
    user_id: int,
):
    project = get_owned_project_by_id(
        db,
        project_id,
        user_id,
    )

    final_company_id = (
        project_data.company_id
        if project_data.company_id is not None
        else project.company_id
    )

    final_department_id = (
        project_data.department_id
        if project_data.department_id is not None
        else project.department_id
    )

    final_team_id = (
        project_data.team_id
        if project_data.team_id is not None
        else project.team_id
    )

    final_start_date = (
        project_data.start_date
        if project_data.start_date is not None
        else project.start_date
    )

    final_end_date = (
        project_data.end_date
        if project_data.end_date is not None
        else project.end_date
    )

    final_status = (
        project_data.status
        if project_data.status is not None
        else project.status
    )

    final_progress = (
        project_data.progress
        if project_data.progress is not None
        else project.progress
    )

    validate_company(
        db,
        final_company_id,
    )

    validate_department(
        db,
        final_department_id,
        final_company_id,
    )

    validate_team(
        db,
        final_team_id,
        final_department_id,
    )

    validate_project_dates(
        final_start_date,
        final_end_date,
    )

    validate_project_status(
        final_status,
    )

    validate_project_progress(
        final_progress,
    )

    update_data = project_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            project,
            key,
            value,
        )

    db.commit()
    db.refresh(project)

    return project


# ----------------------------------------
# Delete Project
# ----------------------------------------

def delete_project(
    db: Session,
    project_id: int,
    user_id: int,
):
    project = get_owned_project_by_id(
        db,
        project_id,
        user_id,
    )

    if project.tasks:
        raise ValueError(
            "Project cannot be deleted because tasks are linked to it"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }