from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


# ----------------------------------------
# Get All Projects
# ----------------------------------------
def get_all_projects(db: Session):
    return db.query(Project).all()


# ----------------------------------------
# Get Project By ID
# ----------------------------------------
def get_project_by_id(db: Session, project_id: int):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    return project


# ----------------------------------------
# Create Project
# ----------------------------------------
def create_project(
    db: Session,
    project: ProjectCreate,
    current_user
):

    new_project = Project(
        name=project.name,
        description=project.description,
        company_id=project.company_id,
        created_by=current_user.id,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        is_active=project.is_active
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
    project_data: ProjectUpdate
):

    project = get_project_by_id(
        db,
        project_id
    )

    if project_data.name is not None:
        project.name = project_data.name

    if project_data.description is not None:
        project.description = project_data.description

    if project_data.company_id is not None:
        project.company_id = project_data.company_id

    if project_data.start_date is not None:
        project.start_date = project_data.start_date

    if project_data.end_date is not None:
        project.end_date = project_data.end_date

    if project_data.status is not None:
        project.status = project_data.status

    if project_data.is_active is not None:
        project.is_active = project_data.is_active

    db.commit()
    db.refresh(project)

    return project


# ----------------------------------------
# Delete Project
# ----------------------------------------
def delete_project(
    db: Session,
    project_id: int
):

    project = get_project_by_id(
        db,
        project_id
    )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }