from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
)

from app.models.user import User

from app.schemas.activity_anomaly import (
    ActivityAnomalyResponse,
    ActivityAnomalyScanResponse,
)

from app.services.activity_anomaly_service import (
    get_anomaly_for_current_user,
    get_anomaly_for_user,
    scan_activity_anomalies,
)

from app.services.activity_log_service import (
    is_admin,
)


router = APIRouter()


@router.get(
    "/my",
    response_model=ActivityAnomalyResponse,
)
def analyze_my_activity(
    window_hours: int = Query(
        24,
        ge=1,
        le=720,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_anomaly_for_current_user(
        db=db,
        current_user=current_user,
        window_hours=window_hours,
    )


@router.get(
    "/scan",
    response_model=ActivityAnomalyScanResponse,
)
def scan_all_users(
    window_hours: int = Query(
        24,
        ge=1,
        le=720,
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
            detail="Admin access required",
        )

    return scan_activity_anomalies(
        db=db,
        window_hours=window_hours,
    )


@router.get(
    "/users/{user_id}",
    response_model=ActivityAnomalyResponse,
)
def analyze_user_activity(
    user_id: int,
    window_hours: int = Query(
        24,
        ge=1,
        le=720,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return get_anomaly_for_user(
            db=db,
            current_user=current_user,
            user_id=user_id,
            window_hours=window_hours,
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
