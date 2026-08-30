from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from app.services.task_service import (
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)

from app.services.activity_log_service import (
    log_activity,
)


router = APIRouter(
    tags=["Tasks"]
)


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


@router.get(
    "/",
    response_model=list[TaskResponse]
)
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(
        task_id,
        db
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201
)
def create_new_task(
    task: TaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        created = create_task(
            task=task,
            created_by=current_user.id,
            db=db,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="task_created",
            entity_type="task",
            entity_id=created.id,
            description=(
                f"Task '{created.name}' created"
            ),
            ip_address=get_client_ip(request),
        )

        return created

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_existing_task(
    task_id: int,
    task: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_task = update_task(
            task_id,
            task,
            db
        )

        if not updated_task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="task_updated",
            entity_type="task",
            entity_id=updated_task.id,
            description=(
                f"Task '{updated_task.name}' updated"
            ),
            ip_address=get_client_ip(request),
        )

        return updated_task

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{task_id}")
def delete_existing_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_task_by_id(
        task_id,
        db
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task_name = existing.name

    deleted = delete_task(
        task_id,
        db
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="task_deleted",
        entity_type="task",
        entity_id=task_id,
        description=(
            f"Task '{task_name}' deleted"
        ),
        ip_address=get_client_ip(request),
    )

    return {
        "message": "Task deleted successfully"
    }
