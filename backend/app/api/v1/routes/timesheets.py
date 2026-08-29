from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy import cast, Date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.time_log import TimeLog
from app.models.timesheet import Timesheet

from app.schemas.time_tracking import (
    TimesheetCreate,
    TimesheetRejectRequest,
    TimesheetResponse,
    TimesheetSummaryResponse,
    TimesheetUpdate,
)

from app.services.time_tracking_service import (
    approve_timesheet,
    create_or_refresh_timesheet,
    delete_timesheet,
    get_pending_timesheets,
    get_timesheet_by_id,
    get_timesheet_summary,
    reject_timesheet,
    submit_timesheet,
    update_timesheet,
)

from app.utils.timesheet_exports import (
    build_timesheet_csv,
    build_timesheet_pdf,
    cache_clear,
    cache_get,
    cache_set,
    check_export_rate_limit,
)


router = APIRouter()

REVIEWER_ROLES = {
    "manager",
    "admin",
    "superadmin",
    "super_admin",
}


# ============================================================
# PERMISSION HELPERS
# ============================================================

def is_reviewer(user):
    role = str(
        getattr(user, "role", "") or ""
    ).strip().lower()

    return role in REVIEWER_ROLES


def require_reviewer(user):
    if not is_reviewer(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin permission required",
        )


def require_owner_or_reviewer(item, user):
    if (
        item.user_id != user.id
        and not is_reviewer(user)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Timesheet access denied",
        )


# ============================================================
# QUERY BUILDER
# ============================================================

def build_query(
    db,
    current_user,
    status_filter=None,
    start_date=None,
    end_date=None,
    user_id=None,
    project_id=None,
):
    """
    Build a timesheet query with support for:

    - status
    - start_date
    - end_date
    - user_id
    - project_id

    Normal users can only see their own timesheets.

    Reviewers can view all users or filter by user_id.

    project_id filtering is based on matching TimeLog records
    belonging to the same user and calendar date as the
    timesheet.
    """

    # --------------------------------------------------------
    # Validate date range
    # --------------------------------------------------------

    if (
        start_date
        and end_date
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = db.query(Timesheet)

    # --------------------------------------------------------
    # User access/filter
    # --------------------------------------------------------

    if is_reviewer(current_user):
        if user_id is not None:
            query = query.filter(
                Timesheet.user_id == user_id
            )
    else:
        query = query.filter(
            Timesheet.user_id == current_user.id
        )

    # --------------------------------------------------------
    # Status filter
    # --------------------------------------------------------

    if status_filter:
        normalized = (
            status_filter
            .strip()
            .lower()
        )

        allowed_statuses = {
            "draft",
            "submitted",
            "approved",
            "rejected",
        }

        if normalized not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid timesheet status",
            )

        query = query.filter(
            Timesheet.status == normalized
        )

    # --------------------------------------------------------
    # Start date filter
    # --------------------------------------------------------

    if start_date:
        query = query.filter(
            Timesheet.date >= start_date
        )

    # --------------------------------------------------------
    # End date filter
    # --------------------------------------------------------

    if end_date:
        query = query.filter(
            Timesheet.date <= end_date
        )

    # --------------------------------------------------------
    # Project filter
    #
    # A Timesheet itself does not contain project_id.
    # TimeLog does contain project_id.
    #
    # Therefore:
    # Find a TimeLog where:
    #
    # TimeLog.user_id == Timesheet.user_id
    # TimeLog project == requested project
    # TimeLog calendar date == Timesheet.date
    #
    # EXISTS prevents duplicate Timesheet rows.
    # --------------------------------------------------------

    if project_id is not None:
        project_log_exists = (
            db.query(TimeLog.id)
            .filter(
                TimeLog.user_id
                == Timesheet.user_id,
                TimeLog.project_id
                == project_id,
                cast(
                    TimeLog.start_time,
                    Date,
                )
                == Timesheet.date,
            )
            .exists()
        )

        query = query.filter(
            project_log_exists
        )

    return query


# ============================================================
# LIST TIMESHEETS
# ============================================================

@router.get(
    "/",
    response_model=list[TimesheetResponse],
)
def list_timesheets(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    start_date: date | None = None,
    end_date: date | None = None,
    user_id: int | None = None,
    project_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        build_query(
            db=db,
            current_user=current_user,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            project_id=project_id,
        )
        .order_by(
            Timesheet.date.desc()
        )
        .all()
    )


# ============================================================
# CREATE TIMESHEET
# ============================================================

@router.post(
    "/",
    response_model=TimesheetResponse,
    status_code=201,
)
def create_timesheet(
    data: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = create_or_refresh_timesheet(
        db,
        current_user.id,
        data.date,
        data.notes,
    )

    cache_clear()

    return result


# ============================================================
# PENDING TIMESHEETS
# ============================================================

@router.get(
    "/pending/",
    response_model=list[TimesheetResponse],
)
def pending_timesheets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    return get_pending_timesheets(
        db
    )


# ============================================================
# OVERALL SUMMARY
# ============================================================

@router.get(
    "/summary/",
    response_model=TimesheetSummaryResponse,
)
def summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    key = "timesheet-summary-all"

    cached = cache_get(
        key
    )

    if cached is not None:
        return cached

    result = get_timesheet_summary(
        db
    )

    cache_set(
        key,
        result,
    )

    return result


# ============================================================
# USER SUMMARY
# ============================================================

@router.get(
    "/user-summary/",
    response_model=TimesheetSummaryResponse,
)
def user_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    key = (
        f"timesheet-summary-"
        f"{current_user.id}"
    )

    cached = cache_get(
        key
    )

    if cached is not None:
        return cached

    result = get_timesheet_summary(
        db,
        current_user.id,
    )

    cache_set(
        key,
        result,
    )

    return result


# ============================================================
# CSV EXPORT
# ============================================================

@router.get(
    "/export/csv/"
)
def export_csv(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    start_date: date | None = None,
    end_date: date | None = None,
    user_id: int | None = None,
    project_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not check_export_rate_limit(
        current_user.id
    ):
        raise HTTPException(
            status_code=429,
            detail="Export rate limit exceeded",
        )

    items = (
        build_query(
            db=db,
            current_user=current_user,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            project_id=project_id,
        )
        .order_by(
            Timesheet.date.desc()
        )
        .all()
    )

    return Response(
        content=build_timesheet_csv(
            items
        ),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="timesheets.csv"'
        },
    )


# ============================================================
# PDF EXPORT
# ============================================================

@router.get(
    "/export/pdf/"
)
def export_pdf(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    start_date: date | None = None,
    end_date: date | None = None,
    user_id: int | None = None,
    project_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not check_export_rate_limit(
        current_user.id
    ):
        raise HTTPException(
            status_code=429,
            detail="Export rate limit exceeded",
        )

    items = (
        build_query(
            db=db,
            current_user=current_user,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            project_id=project_id,
        )
        .order_by(
            Timesheet.date.desc()
        )
        .all()
    )

    return Response(
        content=build_timesheet_pdf(
            items
        ),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="timesheets.pdf"'
        },
    )


# ============================================================
# GET SINGLE TIMESHEET
# ============================================================

@router.get(
    "/{timesheet_id}/",
    response_model=TimesheetResponse,
)
def read_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    require_owner_or_reviewer(
        item,
        current_user,
    )

    return item


# ============================================================
# UPDATE TIMESHEET
# ============================================================

@router.put(
    "/{timesheet_id}/",
    response_model=TimesheetResponse,
)
def edit_timesheet(
    timesheet_id: int,
    data: TimesheetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = update_timesheet(
        db,
        current_user.id,
        timesheet_id,
        data,
    )

    cache_clear()

    return result


# ============================================================
# DELETE TIMESHEET
# ============================================================

@router.delete(
    "/{timesheet_id}/"
)
def remove_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = delete_timesheet(
        db,
        current_user.id,
        timesheet_id,
    )

    cache_clear()

    return result


# ============================================================
# SUBMIT TIMESHEET
# ============================================================

@router.post(
    "/{timesheet_id}/submit/",
    response_model=TimesheetResponse,
)
def submit_user_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = submit_timesheet(
        db,
        current_user.id,
        timesheet_id,
    )

    cache_clear()

    return result


# ============================================================
# APPROVE TIMESHEET
# ============================================================

@router.post(
    "/{timesheet_id}/approve/",
    response_model=TimesheetResponse,
)
def approve_user_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    result = approve_timesheet(
        db,
        timesheet_id,
        current_user.id,
    )

    cache_clear()

    return result


# ============================================================
# REJECT TIMESHEET
# ============================================================

@router.post(
    "/{timesheet_id}/reject/",
    response_model=TimesheetResponse,
)
def reject_user_timesheet(
    timesheet_id: int,
    data: TimesheetRejectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    result = reject_timesheet(
        db,
        timesheet_id,
        current_user.id,
        data.reason,
    )

    cache_clear()

    return result