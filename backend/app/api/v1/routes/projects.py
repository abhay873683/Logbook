from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

from app.services.project_service import (
    create_project,
    get_all_projects,
    get_project_by_id,
    update_project,
    delete_project,
)

from app.services.activity_log_service import (
    log_activity,
)


router = APIRouter()


# ----------------------------------------
# Get Client IP
# ----------------------------------------

def get_client_ip(
    request: Request,
) -> str | None:
    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


# ----------------------------------------
# Create Project
# ----------------------------------------

@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=201,
)
def create_new_project(
    project: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        created = create_project(
            db,
            project,
            current_user,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="project_created",
            entity_type="project",
            entity_id=created.id,
            description=(
                f"Project '{created.name}' created"
            ),
            ip_address=get_client_ip(request),
        )

        return created

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ----------------------------------------
# Get Projects
# ----------------------------------------

@router.get(
    "/",
    response_model=List[ProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_projects(
        db,
        current_user.id,
    )


# ----------------------------------------
# Get Single Project
# ----------------------------------------

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_project_by_id(
            db,
            project_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Update Project
# ----------------------------------------

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated = update_project(
            db,
            project_id,
            project,
            current_user.id,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="project_updated",
            entity_type="project",
            entity_id=updated.id,
            description=(
                f"Project '{updated.name}' updated"
            ),
            ip_address=get_client_ip(request),
        )

        return updated

    except ValueError as e:
        error_message = str(e)

        if (
            "not found" in error_message.lower()
            or "permission" in error_message.lower()
            or "access denied" in error_message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=error_message,
        )


# ----------------------------------------
# Delete Project
# ----------------------------------------

@router.delete(
    "/{project_id}"
)
def delete_existing_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = get_project_by_id(
            db,
            project_id,
            current_user.id,
        )

        project_name = existing.name

        result = delete_project(
            db,
            project_id,
            current_user.id,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="project_deleted",
            entity_type="project",
            entity_id=project_id,
            description=(
                f"Project '{project_name}' deleted"
            ),
            ip_address=get_client_ip(request),
        )

        return result

    except ValueError as e:
        error_message = str(e)

        if (
            "not found" in error_message.lower()
            or "permission" in error_message.lower()
            or "access denied" in error_message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=error_message,
        )