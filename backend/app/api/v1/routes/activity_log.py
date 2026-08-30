from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
)

from app.models.user import User

from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse,
    ActivityStatsResponse,
)

from app.services.activity_log_service import (
    create_activity_log,
    get_activity_log_for_user,
    get_activity_logs,
    get_activity_stats,
    get_all_activity_logs,
    is_admin,
)


router = APIRouter()


def get_client_ip(
    request: Request,
) -> str | None:
    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:
        return (
            forwarded
            .split(",")[0]
            .strip()
        )

    if request.client:
        return request.client.host

    return None


@router.post(
    "/",
    response_model=ActivityLogResponse,
    status_code=201,
)
def create_new_activity_log(
    activity: ActivityLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        secure_activity = (
            activity.model_copy(
                update={
                    "user_id": (
                        current_user.id
                    ),
                    "ip_address": (
                        get_client_ip(
                            request
                        )
                    ),
                }
            )
        )

        return create_activity_log(
            db,
            secure_activity,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/my",
    response_model=list[
        ActivityLogResponse
    ],
)
def read_my_activity_logs(
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    action: str | None = Query(
        None,
        max_length=100,
    ),
    module: str | None = Query(
        None,
        max_length=100,
    ),
    module_id: int | None = Query(
        None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_activity_logs(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        action=action,
        module=module,
        module_id=module_id,
    )


@router.get(
    "/all",
    response_model=list[
        ActivityLogResponse
    ],
)
def read_all_activity_logs(
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
    ),
    user_id: int | None = Query(
        None,
        ge=1,
    ),
    action: str | None = Query(
        None,
        max_length=100,
    ),
    module: str | None = Query(
        None,
        max_length=100,
    ),
    module_id: int | None = Query(
        None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if not is_admin(
        current_user
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Admin access required"
            ),
        )

    return get_all_activity_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        module=module,
        module_id=module_id,
    )


@router.get(
    "/stats",
    response_model=ActivityStatsResponse,
)
def read_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_activity_stats(
        db,
        current_user,
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityLogResponse,
)
def read_activity_log(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return get_activity_log_for_user(
            db,
            activity_id,
            current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )
