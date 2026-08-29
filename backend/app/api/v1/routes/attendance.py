from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.attendance import Attendance
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceUpdate,
)
from app.services.attendance_service import (
    VALID_ATTENDANCE_STATUSES,
    attendance_summary,
    create_attendance,
    get_attendance,
    update_attendance,
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
    return str(
        getattr(user, "role", "") or ""
    ).strip().lower() in REVIEWER_ROLES


def require_reviewer(user):
    if not is_reviewer(user):
        raise HTTPException(
            status_code=403,
            detail="Manager or admin permission required",
        )


def build_query(
    db,
    current_user,
    status_filter=None,
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
        Attendance
    )

    if is_reviewer(current_user):
        if user_id is not None:
            query = query.filter(
                Attendance.user_id == user_id
            )
    else:
        query = query.filter(
            Attendance.user_id == current_user.id
        )

    if department_id is not None:
        query = query.filter(
            Attendance.department_id == department_id
        )

    if status_filter:
        normalized = status_filter.strip().lower()

        if normalized not in VALID_ATTENDANCE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid attendance status",
            )

        query = query.filter(
            Attendance.status == normalized
        )

    if start_date:
        query = query.filter(
            Attendance.date >= start_date
        )

    if end_date:
        query = query.filter(
            Attendance.date <= end_date
        )

    return query


@router.post(
    "/log/",
    response_model=AttendanceResponse,
    status_code=201,
)
def log_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = create_attendance(
        db,
        current_user.id,
        data,
    )

    cache_clear()

    return result


@router.get(
    "/logs/",
    response_model=list[AttendanceResponse],
)
def attendance_logs(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
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
        department_id,
        user_id,
        start_date,
        end_date,
    ).order_by(
        Attendance.date.desc()
    ).all()


@router.put(
    "/logs/{attendance_id}/",
    response_model=AttendanceResponse,
)
def edit_attendance(
    attendance_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = get_attendance(
        db,
        attendance_id,
    )

    if (
        item.user_id != current_user.id
        and not is_reviewer(current_user)
    ):
        raise HTTPException(
            status_code=403,
            detail="Attendance access denied",
        )

    result = update_attendance(
        db,
        attendance_id,
        data,
    )

    cache_clear()

    return result


@router.get(
    "/summary/",
    response_model=AttendanceSummaryResponse,
)
def summary(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    department_id: int | None = None,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    key = (
        f"attendance-summary:"
        f"{current_user.id}:"
        f"{status_filter}:"
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
        department_id,
        user_id,
        start_date,
        end_date,
    )

    result = attendance_summary(
        query
    )

    cache_set(
        key,
        result,
    )

    return result


@router.get(
    "/report/",
    response_model=AttendanceSummaryResponse,
)
def report(
    department_id: int | None = None,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = build_query(
        db,
        current_user,
        None,
        department_id,
        user_id,
        start_date,
        end_date,
    )

    return attendance_summary(
        query
    )


@router.get("/export/csv/")
def export_attendance_csv(
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
        None,
        department_id,
        user_id,
        start_date,
        end_date,
    ).order_by(
        Attendance.date.desc()
    ).all()

    content = build_csv(
        [
            "id",
            "user_id",
            "department_id",
            "date",
            "status",
            "check_in",
            "check_out",
            "hours_worked",
        ],
        [
            [
                x.id,
                x.user_id,
                x.department_id,
                x.date,
                x.status,
                x.check_in or "",
                x.check_out or "",
                x.hours_worked,
            ]
            for x in items
        ],
    )

    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="attendance_report.csv"'
        },
    )


@router.get("/export/pdf/")
def export_attendance_pdf(
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
        Attendance.date.desc()
    ).all()

    lines = [
        (
            f"ID {x.id} | User {x.user_id} | "
            f"{x.date} | {x.status} | "
            f"{x.hours_worked} hours"
        )
        for x in items
    ]

    return Response(
        content=build_simple_pdf(
            "TreeFlow AI - Attendance Report",
            lines,
        ),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="attendance_report.pdf"'
        },
    )
