from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.time_log import TimeLog
from app.models.timer_session import TimerSession
from app.models.timesheet import Timesheet
from app.models.timesheet_log import TimesheetLog

from app.schemas.time_tracking import (
    TimeLogCreate,
    TimeLogUpdate,
    TimerStartRequest,
    TimesheetLogCreate,
    TimesheetUpdate,
)

from app.utils.time_utils import calculate_duration_seconds, utc_now


# ============================================================
# TIME LOGS
# ============================================================

def create_time_log(db: Session, user_id: int, data: TimeLogCreate):
    try:
        duration = calculate_duration_seconds(
            data.start_time,
            data.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    time_log = TimeLog(
        user_id=user_id,
        task_id=data.task_id,
        project_id=data.project_id,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        duration=duration,
        is_billable=data.is_billable,
        source="manual",
    )

    db.add(time_log)
    db.commit()
    db.refresh(time_log)

    return time_log


def get_time_logs(db: Session, user_id: int):
    return (
        db.query(TimeLog)
        .filter(TimeLog.user_id == user_id)
        .order_by(TimeLog.created_at.desc())
        .all()
    )


def get_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
):
    time_log = (
        db.query(TimeLog)
        .filter(
            TimeLog.id == time_log_id,
            TimeLog.user_id == user_id,
        )
        .first()
    )

    if not time_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time log not found",
        )

    return time_log


def update_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
    data: TimeLogUpdate,
):
    time_log = get_time_log(
        db,
        user_id,
        time_log_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(time_log, field, value)

    try:
        time_log.duration = calculate_duration_seconds(
            time_log.start_time,
            time_log.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    db.commit()
    db.refresh(time_log)

    return time_log


def delete_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
):
    time_log = get_time_log(
        db,
        user_id,
        time_log_id,
    )

    db.delete(time_log)
    db.commit()

    return {
        "message": "Time log deleted successfully"
    }


# ============================================================
# TIMER
# ============================================================

def start_timer(
    db: Session,
    user_id: int,
    data: TimerStartRequest,
):
    existing_timer = (
        db.query(TimerSession)
        .filter(
            TimerSession.user_id == user_id,
            TimerSession.is_active.is_(True),
        )
        .first()
    )

    if existing_timer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active timer already exists",
        )

    timer = TimerSession(
        user_id=user_id,
        task_id=data.task_id,
        project_id=data.project_id,
        description=data.description,
        is_billable=data.is_billable,
        start_time=utc_now(),
        is_active=True,
    )

    db.add(timer)
    db.commit()
    db.refresh(timer)

    return timer


def get_active_timer(
    db: Session,
    user_id: int,
):
    return (
        db.query(TimerSession)
        .filter(
            TimerSession.user_id == user_id,
            TimerSession.is_active.is_(True),
        )
        .first()
    )


def get_timer_history(
    db: Session,
    user_id: int,
):
    return (
        db.query(TimerSession)
        .filter(TimerSession.user_id == user_id)
        .order_by(TimerSession.created_at.desc())
        .all()
    )


def stop_timer(
    db: Session,
    user_id: int,
):
    timer = get_active_timer(
        db,
        user_id,
    )

    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active timer found",
        )

    timer.end_time = utc_now()
    timer.is_active = False

    duration = calculate_duration_seconds(
        timer.start_time,
        timer.end_time,
    )

    time_log = TimeLog(
        user_id=user_id,
        task_id=timer.task_id,
        project_id=timer.project_id,
        description=timer.description,
        start_time=timer.start_time,
        end_time=timer.end_time,
        duration=duration,
        is_billable=timer.is_billable,
        source="timer",
    )

    db.add(time_log)
    db.commit()

    db.refresh(timer)
    db.refresh(time_log)

    return {
        "timer_session": timer,
        "time_log": time_log,
    }


# ============================================================
# TIME SUMMARY
# ============================================================

def get_time_summary(
    db: Session,
    user_id: int,
):
    logs = (
        db.query(TimeLog)
        .filter(TimeLog.user_id == user_id)
        .all()
    )

    total_seconds = sum(
        log.duration or 0
        for log in logs
    )

    billable_seconds = sum(
        log.duration or 0
        for log in logs
        if log.is_billable
    )

    return {
        "total_seconds": total_seconds,
        "billable_seconds": billable_seconds,
        "non_billable_seconds":
            total_seconds - billable_seconds,
        "total_entries": len(logs),
    }


# ============================================================
# TIMESHEETS
# ============================================================

def get_timesheets(
    db: Session,
    user_id: int,
    status_filter: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    query = (
        db.query(Timesheet)
        .filter(Timesheet.user_id == user_id)
    )

    if status_filter:
        query = query.filter(
            Timesheet.status == status_filter.lower()
        )

    if start_date:
        query = query.filter(
            Timesheet.date >= start_date
        )

    if end_date:
        query = query.filter(
            Timesheet.date <= end_date
        )

    return (
        query
        .order_by(Timesheet.date.desc())
        .all()
    )


def get_timesheet_by_id(
    db: Session,
    timesheet_id: int,
):
    timesheet = (
        db.query(Timesheet)
        .filter(Timesheet.id == timesheet_id)
        .first()
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    return timesheet


def create_or_refresh_timesheet(
    db: Session,
    user_id: int,
    target_date: date,
    notes: str | None = None,
):
    logs = (
        db.query(TimeLog)
        .filter(TimeLog.user_id == user_id)
        .all()
    )

    total_seconds = sum(
        log.duration or 0
        for log in logs
        if log.start_time.date() == target_date
    )

    timesheet = (
        db.query(Timesheet)
        .filter(
            Timesheet.user_id == user_id,
            Timesheet.date == target_date,
        )
        .first()
    )

    if not timesheet:
        timesheet = Timesheet(
            user_id=user_id,
            date=target_date,
            total_seconds=total_seconds,
            status="draft",
            notes=notes,
        )

        db.add(timesheet)

    else:
        if timesheet.status in (
            "submitted",
            "approved",
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Submitted or approved timesheet "
                    "cannot be refreshed"
                ),
            )

        timesheet.total_seconds = total_seconds

        if notes is not None:
            timesheet.notes = notes

        if timesheet.status == "rejected":
            timesheet.status = "draft"
            timesheet.rejected_at = None
            timesheet.rejected_by = None
            timesheet.rejection_reason = None

    db.commit()
    db.refresh(timesheet)

    return timesheet


def update_timesheet(
    db: Session,
    user_id: int,
    timesheet_id: int,
    data: TimesheetUpdate,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this timesheet",
        )

    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft timesheets can be updated",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(timesheet, field, value)

    db.commit()
    db.refresh(timesheet)

    return timesheet


def delete_timesheet(
    db: Session,
    user_id: int,
    timesheet_id: int,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this timesheet",
        )

    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft timesheets can be deleted",
        )

    db.delete(timesheet)
    db.commit()

    return {
        "message": "Timesheet deleted successfully"
    }


# ============================================================
# SUBMIT / APPROVE / REJECT
# ============================================================

def submit_timesheet(
    db: Session,
    user_id: int,
    timesheet_id: int,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this timesheet",
        )

    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft timesheets can be submitted",
        )

    timesheet.status = "submitted"
    timesheet.submitted_at = utc_now()

    timesheet.approved_at = None
    timesheet.approved_by = None

    timesheet.rejected_at = None
    timesheet.rejected_by = None
    timesheet.rejection_reason = None

    db.commit()
    db.refresh(timesheet)

    return timesheet


def approve_timesheet(
    db: Session,
    timesheet_id: int,
    approved_by: int,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted timesheets can be approved",
        )

    timesheet.status = "approved"
    timesheet.approved_at = utc_now()
    timesheet.approved_by = approved_by

    timesheet.rejected_at = None
    timesheet.rejected_by = None
    timesheet.rejection_reason = None

    db.commit()
    db.refresh(timesheet)

    return timesheet


def reject_timesheet(
    db: Session,
    timesheet_id: int,
    rejected_by: int,
    reason: str,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted timesheets can be rejected",
        )

    timesheet.status = "rejected"
    timesheet.rejected_at = utc_now()
    timesheet.rejected_by = rejected_by
    timesheet.rejection_reason = reason

    timesheet.approved_at = None
    timesheet.approved_by = None

    db.commit()
    db.refresh(timesheet)

    return timesheet


def get_pending_timesheets(
    db: Session,
):
    return (
        db.query(Timesheet)
        .filter(Timesheet.status == "submitted")
        .order_by(Timesheet.submitted_at.asc())
        .all()
    )


# ============================================================
# TIMESHEET SUMMARY
# ============================================================

def get_timesheet_summary(
    db: Session,
    user_id: int | None = None,
):
    query = db.query(Timesheet)

    if user_id is not None:
        query = query.filter(
            Timesheet.user_id == user_id
        )

    timesheets = query.all()

    total_seconds = sum(
        item.total_seconds or 0
        for item in timesheets
    )

    return {
        "total_timesheets": len(timesheets),

        "draft": sum(
            1
            for item in timesheets
            if item.status == "draft"
        ),

        "submitted": sum(
            1
            for item in timesheets
            if item.status == "submitted"
        ),

        "approved": sum(
            1
            for item in timesheets
            if item.status == "approved"
        ),

        "rejected": sum(
            1
            for item in timesheets
            if item.status == "rejected"
        ),

        "total_seconds": total_seconds,

        "total_hours": round(
            total_seconds / 3600,
            2,
        ),
    }


# ============================================================
# TIMESHEET LOGS
# ============================================================

def create_timesheet_log(
    db: Session,
    timesheet_id: int,
    user_id: int,
    data: TimesheetLogCreate,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this timesheet",
        )

    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Logs can only be added "
                "to draft timesheets"
            ),
        )

    if data.date != timesheet.date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Timesheet log date must match "
                "the timesheet date"
            ),
        )

    log = TimesheetLog(
        timesheet_id=timesheet.id,
        date=data.date,
        task_id=data.task_id,
        description=data.description,
        hours=data.hours,
        is_billable=data.is_billable,
    )

    db.add(log)

    timesheet.total_seconds += int(
        data.hours * 3600
    )

    db.commit()
    db.refresh(log)
    db.refresh(timesheet)

    return log


def get_timesheet_logs(
    db: Session,
    timesheet_id: int,
    user_id: int,
):
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
    )

    if timesheet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this timesheet",
        )

    return (
        db.query(TimesheetLog)
        .filter(
            TimesheetLog.timesheet_id == timesheet_id
        )
        .order_by(
            TimesheetLog.date.asc(),
            TimesheetLog.id.asc(),
        )
        .all()
    )
