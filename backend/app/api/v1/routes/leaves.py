from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.leave import Leave
from app.schemas.leave import (
    LeaveBalanceResponse,
    LeaveCreate,
    LeaveRejectRequest,
    LeaveResponse,
    LeaveSummaryResponse,
    LeaveUpdate,
)
from app.services.leave_service import (
    VALID_LEAVE_TYPES,
    VALID_STATUSES,
    approve_leave,
    create_leave,
    delete_leave,
    get_leave,
    get_leave_balance,
    get_leave_summary,
    reject_leave,
    update_leave,
)
from app.utils.leave_attendance_utils import (
    build_csv,
    build_simple_pdf,
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


def owner_or_reviewer(item, user):
    if (
        item.user_id != user.id
        and not is_reviewer(user)
    ):
        raise HTTPException(
            status_code=403,
            detail="Leave access denied",
        )


def build_query(
    db,
    current_user,
    status_filter=None,
    leave_type=None,
    department_id=None,
    user_id=None,
    start_date=None,
    end_date=None,
):
    if (
        start_date
        and end_date
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    query = db.query(
        Leave
    )

    if is_reviewer(current_user):
        if user_id is not None:
            query = query.filter(
                Leave.user_id == user_id
            )
    else:
        query = query.filter(
            Leave.user_id == current_user.id
        )

    if department_id is not None:
        query = query.filter(
            Leave.department_id == department_id
        )

    if status_filter:
        normalized = status_filter.strip().lower()

        if normalized not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid leave status",
            )

        query = query.filter(
            Leave.status == normalized
        )

    if leave_type:
        normalized_type = leave_type.strip().lower()

        if normalized_type not in VALID_LEAVE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid leave type",
            )

        query = query.filter(
            Leave.leave_type == normalized_type
        )

    if start_date:
        query = query.filter(
            Leave.end_date >= start_date
        )

    if end_date:
        query = query.filter(
            Leave.start_date <= end_date
        )

    return query


@router.get(
    "/balance/",
    response_model=LeaveBalanceResponse,
)
def leave_balance(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_leave_balance(
        db,
        current_user.id,
        year,
    )


@router.get(
    "/summary/",
    response_model=LeaveSummaryResponse,
)
def leave_summary(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    leave_type: str | None = None,
    department_id: int | None = None,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    key = (
        f"leave-summary:"
        f"{current_user.id}:"
        f"{status_filter}:"
        f"{leave_type}:"
        f"{department_id}:"
        f"{user_id}:"
        f"{start_date}:"
        f"{end_date}"
    )

    cached = cache_get(key)

    if cached is not None:
        return cached

    query = build_query(
        db,
        current_user,
        status_filter,
        leave_type,
        department_id,
        user_id,
        start_date,
        end_date,
    )

    result = get_leave_summary(
        query
    )

    cache_set(
        key,
        result,
    )

    return result


@router.get("/export/csv/")
def export_leave_csv(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    leave_type: str | None = None,
    department_id: int | None = None,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
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

    items = build_query(
        db,
        current_user,
        status_filter,
        leave_type,
        department_id,
        user_id,
        start_date,
        end_date,
    ).order_by(
        Leave.start_date.desc()
    ).all()

    content = build_csv(
        [
            "id",
            "user_id",
            "department_id",
            "leave_type",
            "start_date",
            "end_date",
            "status",
            "reason",
        ],
        [
            [
                x.id,
                x.user_id,
                x.department_id,
                x.leave_type,
                x.start_date,
                x.end_date,
                x.status,
                x.reason or "",
            ]
            for x in items
        ],
    )

    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="leave_report.csv"'
        },
    )


@router.get("/export/pdf/")
def export_leave_pdf(
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

    items = build_query(
        db,
        current_user,
    ).order_by(
        Leave.start_date.desc()
    ).all()

    lines = [
        (
            f"ID {x.id} | User {x.user_id} | "
            f"{x.leave_type} | "
            f"{x.start_date} to {x.end_date} | "
            f"{x.status}"
        )
        for x in items
    ]

    return Response(
        content=build_simple_pdf(
            "TreeFlow AI - Leave Report",
            lines,
        ),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="leave_report.pdf"'
        },
    )


@router.post(
    "/",
    response_model=LeaveResponse,
    status_code=201,
)
def add_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = create_leave(
        db,
        current_user.id,
        data,
    )

    cache_clear()

    return result


@router.get(
    "/",
    response_model=list[LeaveResponse],
)
def list_leaves(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    leave_type: str | None = None,
    department_id: int | None = None,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return build_query(
        db,
        current_user,
        status_filter,
        leave_type,
        department_id,
        user_id,
        start_date,
        end_date,
    ).order_by(
        Leave.created_at.desc()
    ).all()


@router.get(
    "/{leave_id}/",
    response_model=LeaveResponse,
)
def read_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = get_leave(
        db,
        leave_id,
    )

    owner_or_reviewer(
        item,
        current_user,
    )

    return item


@router.put(
    "/{leave_id}/",
    response_model=LeaveResponse,
)
def edit_leave(
    leave_id: int,
    data: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = update_leave(
        db,
        current_user.id,
        leave_id,
        data,
    )

    cache_clear()

    return result


@router.delete("/{leave_id}/")
def remove_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = delete_leave(
        db,
        current_user.id,
        leave_id,
    )

    cache_clear()

    return result


@router.post(
    "/{leave_id}/approve/",
    response_model=LeaveResponse,
)
def approve_user_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    result = approve_leave(
        db,
        leave_id,
        current_user.id,
    )

    cache_clear()

    return result


@router.post(
    "/{leave_id}/reject/",
    response_model=LeaveResponse,
)
def reject_user_leave(
    leave_id: int,
    data: LeaveRejectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_reviewer(
        current_user
    )

    result = reject_leave(
        db,
        leave_id,
        current_user.id,
        data.reason,
    )

    cache_clear()

    return result
